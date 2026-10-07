"""
convergence.py — Conflict Engine + Log Opinion Pool.
Fait parler 4 modèles INDÉPENDANTS et mesure leur convergence.

Modèles :
- DRC-X (14 variables pondérées)
- Elo pur (force long-terme)
- Poisson + Dixon-Coles (distribution buts)
- Marché Shin (consensus bookmakers)

Sortie :
- P_fusion = Log Opinion Pool
- C = convergence ∈ [0,1]
- F = failure mode
- Conf = confiance globale
- P_finale = ramenée vers neutre si confiance faible
"""

import math
from score_matrix import calculer_lambdas, construire_matrice
import elo
import drcx
import shin


# ============================================================
# Extraction de proba depuis une matrice de scores
# ============================================================

def proba_from_matrix(mat, market):
    """Extrait la probabilité d'un marché depuis une matrice P(i,j)."""
    if not mat:
        return None
    n = len(mat) - 1

    try:
        if market == "1":
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1) if i > j)
        if market == "X":
            return sum(mat[i][i] for i in range(n+1))
        if market == "2":
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1) if i < j)
        if market == "BTTS":
            return sum(mat[i][j] for i in range(1, n+1) for j in range(1, n+1))

        if market.startswith("O"):
            line = float(market[1:])
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1) if i + j > line)
        if market.startswith("U"):
            line = float(market[1:])
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1) if i + j < line)

        if market.startswith("AH-"):
            line = abs(float(market[3:]))
            seuil = line + 0.5
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1)
                       if (i - j) >= seuil)
        if market.startswith("AH+"):
            line = abs(float(market[3:]))
            seuil = line - 0.5
            return sum(mat[i][j] for i in range(n+1) for j in range(n+1)
                       if (i - j) <= seuil)
    except (ValueError, IndexError):
        return None

    return None


# ============================================================
# Les 4 modèles indépendants
# ============================================================

def proba_drcx(market, variables, ligue="?"):
    """Modèle principal : DRC-X."""
    try:
        res = drcx.calculer_proba(market, variables, ligue=ligue)
        return res.get("proba_calibree")
    except Exception:
        return None


def proba_elo(market, variables, home_team, away_team):
    """Modèle Elo pur : utilise l'écart de rating pour dériver des λ."""
    if not home_team or not away_team:
        return None
    try:
        ecart = elo.ecart_elo(home_team, away_team)
        base = 1.35
        # Bonus/malus lié à l'écart Elo, borné
        lam_h = max(0.3, min(4.5, base * (1 + ecart / 400)))
        lam_a = max(0.3, min(4.5, base * (1 - ecart / 400)))
        mat = construire_matrice(lam_h, lam_a)
        return proba_from_matrix(mat, market)
    except Exception:
        return None


def proba_poisson(market, variables):
    """Modèle Poisson + Dixon-Coles : utilise les variables pour λ."""
    try:
        lam_h, lam_a = calculer_lambdas(variables)
        mat = construire_matrice(lam_h, lam_a)
        return proba_from_matrix(mat, market)
    except Exception:
        return None


def proba_marche(market, cotes_groupe):
    """Modèle marché : proba implicite après retrait Shin."""
    if not cotes_groupe or market not in cotes_groupe:
        return None
    if len(cotes_groupe) < 2:
        return None
    try:
        cles = list(cotes_groupe.keys())
        cotes = [cotes_groupe[k] for k in cles]
        probas = shin.retirer_marge_shin(cotes)
        if not probas:
            return None
        return probas[cles.index(market)]
    except Exception:
        return None


# ============================================================
# Conflict Engine
# ============================================================

def calculer_convergence(probas):
    """
    Prend une liste de probas disponibles.
    Retourne (C, D) :
    - D = divergence (variance)
    - C = exp(-k × D) ∈ [0, 1]
    """
    vals = [p for p in probas if p is not None]
    if len(vals) < 2:
        return 1.0, 0.0

    moy = sum(vals) / len(vals)
    D = sum((v - moy) ** 2 for v in vals) / len(vals)

    # k = 50 → D=0.01 (écart type ~10%) donne C ≈ 0.61
    k = 50.0
    C = math.exp(-k * D)
    return max(0.0, min(1.0, C)), D


# ============================================================
# Log Opinion Pool
# ============================================================

def log_opinion_pool(probas):
    """
    Fusion multiplicative :
      P_fusion = exp( Σ log(P_i) / N )
    = moyenne géométrique.
    """
    vals = [p for p in probas if p is not None]
    if not vals:
        return None

    log_sum = 0.0
    for p in vals:
        p_safe = max(0.001, min(0.999, p))
        log_sum += math.log(p_safe)

    P = math.exp(log_sum / len(vals))
    return max(0.0, min(1.0, P))


# ============================================================
# Failure Mode
# ============================================================

def calculer_failure(rob):
    """F = 1 - ROB. Traduit la robustesse en risque de rupture."""
    if rob is None:
        return 0.5
    return max(0.0, min(1.0, 1.0 - rob))


# ============================================================
# Confidence Governor
# ============================================================

def calculer_confiance(C, Q_normalized, rob, beta=0.5, alpha=0.5, gamma=0.5):
    """
    Conf = C^β × Q^α × ROB^γ
    - C : convergence ∈ [0,1]
    - Q_normalized : qualité données ∈ [0,1]
    - rob : robustesse ∈ [0,1]
    β, α, γ = 0.5 → exposants "doux"
    """
    C_safe = max(0.001, min(1.0, C))
    Q_safe = max(0.001, min(1.0, Q_normalized))
    rob_safe = max(0.001, min(1.0, rob))
    try:
        return (C_safe ** beta) * (Q_safe ** alpha) * (rob_safe ** gamma)
    except Exception:
        return 0.5


def calculer_p_finale(P_fusion, Conf, base=0.5):
    """
    Ramène vers neutre si confiance faible :
      P_final = base + Conf × (P_fusion − base)
    - Conf = 1 → P_final = P_fusion
    - Conf = 0 → P_final = base (0.5)
    """
    if P_fusion is None:
        return base
    return base + Conf * (P_fusion - base)


# ============================================================
# Pipeline complet
# ============================================================

def analyser_convergence(market, variables, ligue, home_team, away_team,
                         cotes_groupe, rob, quality_normalized):
    """
    Fait parler les 4 modèles, calcule convergence, fusion, confiance.
    """
    p_drcx = proba_drcx(market, variables, ligue=ligue)
    p_elo = proba_elo(market, variables, home_team, away_team)
    p_poisson = proba_poisson(market, variables)
    p_marche = proba_marche(market, cotes_groupe)

    modeles = {
        "DRC-X": p_drcx,
        "Elo": p_elo,
        "Poisson": p_poisson,
        "Marché": p_marche,
    }

    probas_valides = [p for p in modeles.values() if p is not None]

    C, D = calculer_convergence(probas_valides)
    P_fusion = log_opinion_pool(probas_valides)
    F = calculer_failure(rob)
    Conf = calculer_confiance(C, quality_normalized, rob if rob else 0.5)
    P_finale = calculer_p_finale(P_fusion, Conf, base=0.5)

    return {
        "market": market,
        "modeles": modeles,
        "P_fusion": P_fusion,
        "P_finale": P_finale,
        "convergence": C,
        "divergence": D,
        "failure": F,
        "confiance": Conf,
        "n_modeles": len(probas_valides),
    }


# ============================================================
# Test local
# ============================================================

if __name__ == "__main__":
    variables = {
        "FORM": 0.66, "ATT": 0.77, "DEF": 0.62, "XG": 0.78, "HOME": 0.55,
        "GOALS": 0.75, "ABS": 0.79, "H2H": 0.54, "MOT": 0.85, "GK": 0.55,
        "SET": 0.50, "STYLE": 0.50, "MARKET": 0.44, "ELO": 0.58,
    }
    cotes_1x2 = {"1": 2.10, "X": 3.40, "2": 3.50}

    print("=== Convergence Engine ===\n")
    for m in ["1", "X", "2"]:
        res = analyser_convergence(
            market=m, variables=variables, ligue="Premier League",
            home_team="Arsenal", away_team="Liverpool",
            cotes_groupe=cotes_1x2,
            rob=0.92, quality_normalized=0.88,
        )
        print(f"[{m}]")
        for nom, p in res["modeles"].items():
            p_str = f"{p:.1%}" if p is not None else "—"
            print(f"   {nom:8s} : {p_str}")
        print(f"   Fusion  : {res['P_fusion']:.1%}")
        print(f"   Finale  : {res['P_finale']:.1%}")
        print(f"   Convergence : {res['convergence']:.2f}")
        print(f"   Confiance   : {res['confiance']:.2f}\n")
