"""
oracle.py — Cerveau 3 : Oracle Shield
Contradictions + Chaos + Quality + NO BET + Master Score.
"""

import math
from config import (
    SCORE_SEUILS, ROB_MIN_ACCEPTATION,
    MIN_EDGE, MIN_ODDS, MAX_ODDS
)


# ---------- Détecteur de contradictions ----------

def detecter_contradictions(variables):
    """
    Cherche des paires de signaux contradictoires.
    Un signal "fort" est > 0.65. Un signal "faible" est < 0.35.
    """
    forts = [v for v, x in variables.items() if x > 0.65]
    faibles = [v for v, x in variables.items() if x < 0.35]

    # Paires connues de variables "opposées"
    paires_opposees = [
        ("ATT", "DEF"),          # attaque forte vs défense faible
        ("XG", "GOALS"),         # qualité vs profil
        ("FORM", "H2H"),         # forme vs historique
        ("HOME", "ABS"),         # avantage dom vs absences
    ]

    contradictions = []
    for a, b in paires_opposees:
        va = variables.get(a, 0.5)
        vb = variables.get(b, 0.5)
        if abs(va - vb) > 0.35:
            contradictions.append({
                "pair": (a, b),
                "ecart": abs(va - vb),
                "sens": f"{a}={'fort' if va > 0.5 else 'faible'} vs "
                        f"{b}={'fort' if vb > 0.5 else 'faible'}",
            })

    return contradictions


def score_contradictions(contradictions):
    """Score 0-1 : plus c'est élevé, plus il y a de contradictions."""
    if not contradictions:
        return 0.0
    total = sum(min(1.0, c["ecart"] / 0.6) for c in contradictions)
    return min(1.0, total / 3.0)  # normalisé sur 3 contradictions max


# ---------- Chaos Index ----------

def chaos_index(variables, contradictions_score):
    """
    CHAOS = combinaison de :
    - dispersion des variables (variance)
    - contradictions
    - écart à la neutralité (0.5)
    """
    vals = list(variables.values())

    # Dispersion
    moy = sum(vals) / len(vals)
    variance = sum((v - moy) ** 2 for v in vals) / len(vals)
    dispersion = min(1.0, math.sqrt(variance) * 2.0)

    # Écart à la neutralité (combien de variables sont extrêmes)
    extremes = sum(1 for v in vals if abs(v - 0.5) > 0.30) / len(vals)

    chaos = 0.4 * dispersion + 0.4 * contradictions_score + 0.2 * extremes
    return min(1.0, chaos)


# ---------- Quality (Q) ----------

def calculer_quality(volume_donnees, fraicheur_jours, completude):
    """
    Q sur 100.
    - volume_donnees : 0-1 (nb matchs disponibles / 5)
    - fraicheur_jours : 0-1 (0 = très frais, 1 = très vieux)
    - completude : 0-1 (xG dispo, cotes dispo, etc.)
    """
    q_volume = 40 * min(1.0, volume_donnees)
    q_fraicheur = 30 * (1.0 - min(1.0, fraicheur_jours))
    q_completude = 30 * min(1.0, completude)
    return q_volume + q_fraicheur + q_completude  # 0-100


# ---------- Value ----------

def calculer_ev(p_calibree, cote):
    if cote <= 0:
        return 0.0
    return p_calibree * cote - 1.0


def facteur_value(ev):
    """
    V_F = 1 + tanh(EV). Borné naturellement entre 0 et 2.
    """
    try:
        return 1.0 + math.tanh(ev)
    except OverflowError:
        return 2.0 if ev > 0 else 0.0


# ---------- NO BET Gate ----------

def no_bet_gate(p_cal, rob, chaos, q, ev, cote,
                contradictions_score, es=None):
    """
    Retourne (accepte: bool, raisons: list[str]).
    """
    raisons = []

    # Verrous durs
    if rob < ROB_MIN_ACCEPTATION:
        raisons.append(f"ROB trop bas ({rob:.2f} < {ROB_MIN_ACCEPTATION})")
    if ev <= 0:
        raisons.append(f"EV négatif ({ev:+.2%})")
    if not (MIN_ODDS <= cote <= MAX_ODDS):
        raisons.append(f"Cote hors bornes ({cote:.2f})")
    if chaos > 0.60:
        raisons.append(f"Chaos trop élevé ({chaos:.2f})")
    if contradictions_score > 0.50:
        raisons.append(f"Contradictions fortes ({contradictions_score:.2f})")
    if q < 50:
        raisons.append(f"Qualité données insuffisante ({q:.0f}/100)")
    if es is not None and es < 0.50:
        raisons.append(f"Edge Stability faible ({es:.2f})")

    return (len(raisons) == 0, raisons)


# ---------- Master Score ----------

def master_score(p_cal, rob, q, value_factor, chaos):
    """
    MASTER = 100 × P_CAL × ROB × (Q/100) × V_F × (1 - CHAOS)
    Retourne un score 0-100.
    """
    score = 100 * p_cal * rob * (q / 100.0) * value_factor * (1 - chaos)
    return max(0.0, min(100.0, score))


def classer_score(score):
    if score >= SCORE_SEUILS["TRES_FORT"]:
        return "💎 EXCEPTIONNEL"
    if score >= SCORE_SEUILS["FORT"]:
        return "🟢 TRÈS FORT"
    if score >= SCORE_SEUILS["INTERESSANT"]:
        return "🟢 FORT"
    if score >= SCORE_SEUILS["FAIBLE"]:
        return "🟡 INTÉRESSANT"
    if score >= SCORE_SEUILS["REJET"]:
        return "🟡 FAIBLE"
    return "🔴 REJET"


# ---------- Pipeline complet Oracle ----------

def analyse_oracle(variables, market_result, cote,
                   volume_donnees=1.0, fraicheur_jours=0.1, completude=1.0):
    """
    Prend :
    - variables (dict des 13)
    - market_result : dict retourné par analyse_mger()
    - cote
    - qualité données (volume, fraicheur, complétude)
    Retourne le rapport complet.
    """
    p_cal = market_result["p_central"]
    rob = market_result["rob"]
    es = market_result.get("edge_stability")

    # Contradictions et chaos
    contradictions = detecter_contradictions(variables)
    sc_contra = score_contradictions(contradictions)
    chaos = chaos_index(variables, sc_contra)

    # Quality
    q = calculer_quality(volume_donnees, fraicheur_jours, completude)

    # Value
    ev = calculer_ev(p_cal, cote)
    vf = facteur_value(ev)

    # Décision
    accepte, raisons = no_bet_gate(
        p_cal, rob, chaos, q, ev, cote, sc_contra, es
    )

    # Master score
    ms = master_score(p_cal, rob, q, vf, chaos)

    return {
        "market": market_result["market"],
        "p_calibree": p_cal,
        "rob": rob,
        "chaos": chaos,
        "quality": q,
        "ev": ev,
        "value_factor": vf,
        "edge_stability": es,
        "contradictions": contradictions,
        "score_contradictions": sc_contra,
        "master_score": ms,
        "verdict": classer_score(ms),
        "accepte": accepte,
        "raisons_rejet": raisons,
    }


# ---------- Test local ----------

if __name__ == "__main__":
    from mger import analyse_mger

    exemple_variables = {
        "FORM": 0.72, "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
        "GOALS": 0.58, "ABS": 0.85, "H2H": 0.54, "MOT": 0.60, "GK": 0.65,
        "SET": 0.52, "STYLE": 0.63, "MARKET": 0.58,
    }
    cotes = {"1": 2.10, "X": 3.40, "2": 3.30,
             "O2.5": 1.90, "U2.5": 1.90, "BTTS": 1.75}

    print("=== ORACLE SHIELD ===\n")
    for m, c in cotes.items():
        mger_res = analyse_mger(m, exemple_variables, cote=c)
        oracle_res = analyse_oracle(exemple_variables, mger_res, c)
        statut = "✅" if oracle_res["accepte"] else "🔴"
        print(f"{statut} [{m}] MS={oracle_res['master_score']:.1f}/100 "
              f"verdict={oracle_res['verdict']} "
              f"chaos={oracle_res['chaos']:.2f}")
        if not oracle_res["accepte"]:
            for r in oracle_res["raisons_rejet"]:
                print(f"     └─ {r}")
