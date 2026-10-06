"""
analyse.py — Couche d'intégration.
Pipeline complet :
18 marchés + scores + combinés + CLV + Meta-Brain + ELO + Shin + Cohérence.
Recalcule EV + Master Score APRÈS la correction de cohérence.
"""

import math

from extraction import construire_donnees
from variables import calculer_variables
from poids import detecter_regime
from mger import analyse_mger
from oracle import analyse_oracle, facteur_value, classer_score, no_bet_gate
from score_matrix import (
    calculer_lambdas,
    construire_matrice,
    proba_score,
    top_scores,
)
from combines import generer_combines
from coherence import appliquer_coherence


MARCHES_V1 = [
    "1", "X", "2",
    "O0.5", "U0.5",
    "O1.5", "U1.5",
    "O2.5", "U2.5",
    "O3.5", "U3.5",
    "AH-0.5", "AH+0.5",
    "AH-1.5", "AH+1.5",
    "AH-2.5", "AH+2.5",
    "BTTS",
]


GROUPES = {
    "1":      ["1", "X", "2"],
    "X":      ["1", "X", "2"],
    "2":      ["1", "X", "2"],
    "O0.5":   ["O0.5", "U0.5"],
    "U0.5":   ["O0.5", "U0.5"],
    "O1.5":   ["O1.5", "U1.5"],
    "U1.5":   ["O1.5", "U1.5"],
    "O2.5":   ["O2.5", "U2.5"],
    "U2.5":   ["O2.5", "U2.5"],
    "O3.5":   ["O3.5", "U3.5"],
    "U3.5":   ["O3.5", "U3.5"],
    "AH-0.5": ["AH-0.5", "AH+0.5"],
    "AH+0.5": ["AH-0.5", "AH+0.5"],
    "AH-1.5": ["AH-1.5", "AH+1.5"],
    "AH+1.5": ["AH-1.5", "AH+1.5"],
    "AH-2.5": ["AH-2.5", "AH+2.5"],
    "AH+2.5": ["AH-2.5", "AH+2.5"],
    "BTTS":   ["BTTS"],
}


def construire_groupes_cotes(market, cotes_map):
    cles = GROUPES.get(market, [market])
    groupe = {}
    for k in cles:
        c = cotes_map.get(k)
        if c and c > 1.01:
            groupe[k] = c
    return groupe if len(groupe) >= 2 else None


def recalculer_apres_coherence(r):
    """
    Recalcule EV, facteur value, Master Score, verdict, accepte
    APRÈS que la couche cohérence ait corrigé p_calibree.
    """
    if "p_calibree" not in r or "cote" not in r:
        return r

    p_cal = r["p_calibree"]
    cote = r["cote"]

    # EV
    ev = p_cal * cote - 1.0 if cote > 0 else 0.0
    r["ev"] = ev
    r["value_factor"] = facteur_value(ev)

    # Edge Shin recalculé sur la nouvelle proba (si cotes groupe dispo)
    p_imp_shin = r.get("proba_implicite_shin")
    if p_imp_shin is not None:
        r["edge_shin"] = p_cal - p_imp_shin
    p_imp_naive = r.get("proba_implicite_naive")
    if p_imp_naive is not None:
        r["edge_naif"] = p_cal - p_imp_naive

    # Master Score
    rob = r.get("rob", 1.0)
    q = r.get("quality", 100.0)
    chaos = r.get("chaos", 0.0)
    clv_factor = r.get("clv_factor", 1.0)
    meta_factor = r.get("meta_factor", 1.0)
    vf = r["value_factor"]
    ms = 100 * p_cal * rob * (q / 100.0) * vf * (1 - chaos) * clv_factor * meta_factor
    ms = max(0.0, min(100.0, ms))
    r["master_score"] = ms
    r["verdict"] = classer_score(ms)

    # Redécision NO BET
    piege = r.get("piege", False)
    meta_score = r.get("meta_data", {}).get("score", 0.0)
    accepte, raisons = no_bet_gate(
        p_cal, rob, chaos, q, ev, cote,
        r.get("score_contradictions", 0.0),
        r.get("edge_stability"),
        piege, meta_score,
    )
    r["accepte"] = accepte
    r["raisons_rejet"] = raisons

    return r


def analyser_scores_exacts(variables, cotes_cs):
    lam_h, lam_a = calculer_lambdas(variables)
    mat = construire_matrice(lam_h, lam_a)

    resultats = []
    for score, cote in cotes_cs:
        if not score or not cote or cote <= 1.01:
            continue
        p = proba_score(mat, score)
        if p is None:
            continue
        proba_implicite = 1 / cote
        edge = p - proba_implicite
        ev = p * cote - 1
        resultats.append({
            "score": score,
            "proba": p,
            "cote": cote,
            "proba_implicite": proba_implicite,
            "edge": edge,
            "ev": ev,
        })

    return {
        "lambdas": {"home": lam_h, "away": lam_a},
        "scores_saisis": resultats,
        "top_modele": top_scores(mat, 5),
    }


def analyser_match(home_form, away_form, h2h,
                   absences, motivation, cote_home, cotes_map,
                   cotes_cs=None, cotes_ouverture_map=None,
                   ligue="?", home_team=None, away_team=None):
    donnees = construire_donnees(
        form_data=home_form,
        form_adv_data=away_form,
        absences=absences,
        motivation=motivation,
        cote_home=cote_home,
        h2h_data=h2h,
        home_team=home_team,
        away_team=away_team,
    )

    volume = donnees.pop("_volume", 1.0)
    fraicheur = donnees.pop("_fraicheur", 0.1)
    completude = donnees.pop("_completude", 1.0)

    variables = calculer_variables(donnees)

    try:
        regime = detecter_regime(variables, gap_niveau=0.5)
    except Exception:
        regime = "?"

    cotes_ouv = cotes_ouverture_map or {}

    # === 1. Analyse brute par marché ===
    resultats = []
    for market in MARCHES_V1:
        cote = cotes_map.get(market)
        if not cote or cote <= 1.01:
            continue
        try:
            mger_res = analyse_mger(market, variables, cote=cote)
            groupe = construire_groupes_cotes(market, cotes_map)
            oracle_res = analyse_oracle(
                variables, mger_res, cote,
                cote_ouverture=cotes_ouv.get(market),
                volume_donnees=volume,
                fraicheur_jours=fraicheur,
                completude=completude,
                regime=regime,
                ligue=ligue,
                cotes_groupe=groupe,
            )
            oracle_res["cote"] = cote
            resultats.append(oracle_res)
        except Exception as e:
            resultats.append({
                "market": market, "erreur": str(e), "accepte": False,
            })

    # === 2. Cohérence ===
    try:
        resultats = appliquer_coherence(resultats)
    except Exception as e:
        print(f"Erreur coherence : {e}")

    # === 3. Recalcul EV / Master Score après cohérence ===
    resultats = [recalculer_apres_coherence(r) for r in resultats]

    # === 4. Meilleur pari ===
    valides = [r for r in resultats if r.get("accepte")]
    meilleur = max(valides, key=lambda x: x["master_score"]) if valides else None

    # === 5. Scores exacts ===
    scores_exacts = None
    if cotes_cs:
        try:
            scores_exacts = analyser_scores_exacts(variables, cotes_cs)
        except Exception as e:
            scores_exacts = {"erreur": str(e)}

    # === 6. Combinés ===
    combines = None
    try:
        combines = generer_combines(resultats, top_n=10, ev_min=0.0)
    except Exception as e:
        combines = {"erreur": str(e)}

    return {
        "variables": variables,
        "qualite": {
            "volume": volume,
            "fraicheur": fraicheur,
            "completude": completude,
        },
        "regime": regime,
        "ligue": ligue,
        "resultats": resultats,
        "meilleur": meilleur,
        "scores_exacts": scores_exacts,
        "combines": combines,
}
