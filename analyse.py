"""
analyse.py — Couche d'intégration.
Pipeline complet : 18 marchés + scores exacts + combinés
+ CLV + Meta-Brain + Shin (edge optimal).
"""

from extraction import construire_donnees
from variables import calculer_variables
from poids import detecter_regime
from mger import analyse_mger
from oracle import analyse_oracle
from score_matrix import (
    calculer_lambdas,
    construire_matrice,
    proba_score,
    top_scores,
)
from combines import generer_combines


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


# --- Groupes de cotes pour Shin ---
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
    """Retourne le dict {key: cote} du groupe auquel appartient le marché."""
    cles = GROUPES.get(market, [market])
    groupe = {}
    for k in cles:
        c = cotes_map.get(k)
        if c and c > 1.01:
            groupe[k] = c
    return groupe if len(groupe) >= 2 else None


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
    """
    Pipeline complet.
    """
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

    valides = [r for r in resultats if r.get("accepte")]
    meilleur = max(valides, key=lambda x: x["master_score"]) if valides else None

    scores_exacts = None
    if cotes_cs:
        try:
            scores_exacts = analyser_scores_exacts(variables, cotes_cs)
        except Exception as e:
            scores_exacts = {"erreur": str(e)}

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
