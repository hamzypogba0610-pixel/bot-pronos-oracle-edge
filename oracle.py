"""
oracle.py — Cerveau 3 : Oracle Shield
Contradictions + Chaos + Quality + NO BET + Master Score + CLV + Meta-Brain + Shin.
"""

import math
from config import (
    SCORE_SEUILS, ROB_MIN_ACCEPTATION,
    MIN_EDGE, MIN_ODDS, MAX_ODDS
)
from momentum import analyse_momentum
import metabrain
import shin


# ---------- Détecteur de contradictions ----------

def detecter_contradictions(variables):
    paires_opposees = [
        ("ATT", "DEF"),
        ("XG", "GOALS"),
        ("FORM", "H2H"),
        ("HOME", "ABS"),
    ]
    contradictions = []
    for a, b in paires_opposees:
        va = variables.get(a, 0.5)
        vb = variables.get(b, 0.5)
        if abs(va - vb) > 0.35:
            contradictions.append({
                "pair": (a, b),
                "ecart": abs(va - vb),
            })
    return contradictions


def score_contradictions(contradictions):
    if not contradictions:
        return 0.0
    total = sum(min(1.0, c["ecart"] / 0.6) for c in contradictions)
    return min(1.0, total / 3.0)


# ---------- Chaos Index ----------

def chaos_index(variables, contradictions_score):
    vals = list(variables.values())
    moy = sum(vals) / len(vals)
    variance = sum((v - moy) ** 2 for v in vals) / len(vals)
    dispersion = min(1.0, math.sqrt(variance) * 2.0)
    extremes = sum(1 for v in vals if abs(v - 0.5) > 0.30) / len(vals)
    chaos = 0.4 * dispersion + 0.4 * contradictions_score + 0.2 * extremes
    return min(1.0, chaos)


# ---------- Quality ----------

def calculer_quality(volume_donnees, fraicheur_jours, completude):
    q_volume = 40 * min(1.0, volume_donnees)
    q_fraicheur = 30 * (1.0 - min(1.0, fraicheur_jours))
    q_completude = 30 * min(1.0, completude)
    return q_volume + q_fraicheur + q_completude


# ---------- Value ----------

def calculer_ev(p_calibree, cote):
    if cote <= 0:
        return 0.0
    return p_calibree * cote - 1.0


def facteur_value(ev):
    try:
        return 1.0 + math.tanh(ev)
    except OverflowError:
        return 2.0 if ev > 0 else 0.0


# ---------- Shin ----------

def calculer_probas_shin(cotes_groupe, market):
    """
    Prend un dict {market_key: cote} et le market cible.
    Retourne la proba implicite Shin pour ce market (ou None).
    """
    if not cotes_groupe or len(cotes_groupe) < 2:
        return None
    if market not in cotes_groupe:
        return None

    cles = list(cotes_groupe.keys())
    cotes = [cotes_groupe[k] for k in cles]
    try:
        probas = shin.retirer_marge_shin(cotes)
    except Exception:
        return None

    if not probas:
        return None
    return probas[cles.index(market)]


# ---------- NO BET Gate ----------

def no_bet_gate(p_cal, rob, chaos, q, ev, cote,
                contradictions_score, es=None, piege=False,
                metascore=0.0):
    raisons = []

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
    if piege:
        raisons.append("🚨 Piège détecté : value positive mais marché défavorable")
    if metascore <= -0.50:
        raisons.append(f"🔴 Point faible historique sur ce contexte "
                       f"(MetaScore {metascore:+.2f})")

    return (len(raisons) == 0, raisons)


# ---------- Master Score ----------

def master_score(p_cal, rob, q, value_factor, chaos,
                 clv_factor=1.0, meta_factor=1.0):
    score = (100 * p_cal * rob * (q / 100.0)
             * value_factor * (1 - chaos)
             * clv_factor * meta_factor)
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


# ---------- Pipeline complet ----------

def analyse_oracle(variables, market_result, cote,
                   cote_ouverture=None,
                   volume_donnees=1.0, fraicheur_jours=0.1, completude=1.0,
                   regime="?", ligue="?",
                   cotes_groupe=None):
    """
    cotes_groupe : dict optionnel {market_key: cote} du groupe cohérent
                   (ex: {"1": 2.10, "X": 3.40, "2": 3.50}).
                   Si fourni → Shin calcule la proba implicite réelle.
    """
    p_cal = market_result["p_central"]
    rob = market_result["rob"]
    es = market_result.get("edge_stability")
    market = market_result["market"]

    # Contradictions / Chaos
    contradictions = detecter_contradictions(variables)
    sc_contra = score_contradictions(contradictions)
    chaos = chaos_index(variables, sc_contra)

    q = calculer_quality(volume_donnees, fraicheur_jours, completude)
    ev = calculer_ev(p_cal, cote)
    vf = facteur_value(ev)

    # --- Momentum (CLV) ---
    clv_data = None
    clv_factor = 1.0
    piege = False
    if cote_ouverture and cote_ouverture > 1.01:
        clv_data = analyse_momentum(cote_ouverture, cote, ev)
        clv_factor = clv_data["facteur"]
        piege = clv_data["piege"]

    # --- Meta-Brain ---
    meta_data = metabrain.calculer_metascore(market, regime, ligue)
    meta_score = meta_data["score"]
    meta_factor = meta_data["facteur"]

    # --- Shin : proba implicite optimale ---
    p_imp_naive = 1.0 / cote if cote > 0 else 0.0
    p_imp_shin = calculer_probas_shin(cotes_groupe, market)
    if p_imp_shin is None:
        p_imp_shin = p_imp_naive

    edge_naif = p_cal - p_imp_naive
    edge_shin = p_cal - p_imp_shin

    # Décision
    accepte, raisons = no_bet_gate(
        p_cal, rob, chaos, q, ev, cote, sc_contra, es, piege, meta_score
    )

    ms = master_score(p_cal, rob, q, vf, chaos, clv_factor, meta_factor)

    return {
        "market": market,
        "p_calibree": p_cal,
        "rob": rob,
        "chaos": chaos,
        "quality": q,
        "ev": ev,
        "value_factor": vf,
        "clv_factor": clv_factor,
        "clv_data": clv_data,
        "meta_factor": meta_factor,
        "meta_data": meta_data,
        "regime": regime,
        "ligue": ligue,
        "edge_stability": es,
        "contradictions": contradictions,
        "score_contradictions": sc_contra,
        # --- Shin ---
        "proba_implicite_naive": p_imp_naive,
        "proba_implicite_shin": p_imp_shin,
        "edge_naif": edge_naif,
        "edge_shin": edge_shin,
        # --- Master ---
        "master_score": ms,
        "verdict": classer_score(ms),
        "accepte": accepte,
        "raisons_rejet": raisons,
        "piege": piege,
    }


# ---------- Test local ----------

if __name__ == "__main__":
    from mger import analyse_mger

    exemple_variables = {
        "FORM": 0.72, "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
        "GOALS": 0.58, "ABS": 0.85, "H2H": 0.54, "MOT": 0.60, "GK": 0.65,
        "SET": 0.52, "STYLE": 0.63, "MARKET": 0.58, "ELO": 0.62,
    }
    cotes_1x2 = {"1": 2.10, "X": 3.40, "2": 3.50}

    print("=== ORACLE + SHIN ===\n")
    for m in ["1", "X", "2"]:
        c = cotes_1x2[m]
        mger_res = analyse_mger(m, exemple_variables, cote=c)
        oracle_res = analyse_oracle(
            exemple_variables, mger_res, c,
            regime="B", ligue="Premier League",
            cotes_groupe=cotes_1x2,
        )
        print(f"[{m}] p_cal={oracle_res['p_calibree']:.1%} · "
              f"edge naïf={oracle_res['edge_naif']:+.2%} · "
              f"edge Shin={oracle_res['edge_shin']:+.2%}")
