"""
analyse.py — Couche d'intégration.
Prend les données du formulaire, exécute les 3 cerveaux,
retourne un rapport complet.
"""

from extraction import construire_donnees
from variables import calculer_variables
from mger import analyse_mger
from oracle import analyse_oracle


MARCHES_V1 = ["1", "X", "2", "O2.5", "U2.5", "BTTS"]


def analyser_match(home_form, away_form, h2h,
                   absences, motivation, cote_home, cotes_map):
    """
    Pipeline complet :
    1. Extraction des stats (extraction.py)
    2. Calcul des 13 variables (variables.py)
    3. Analyse multi-marchés (mger + oracle)
    Retourne dict avec variables / qualite / resultats / meilleur.
    """
    donnees = construire_donnees(
        form_data=home_form,
        form_adv_data=away_form,
        absences=absences,
        motivation=motivation,
        cote_home=cote_home,
        h2h_data=h2h,
    )

    volume = donnees.pop("_volume", 1.0)
    fraicheur = donnees.pop("_fraicheur", 0.1)
    completude = donnees.pop("_completude", 1.0)

    variables = calculer_variables(donnees)

    resultats = []
    for market in MARCHES_V1:
        cote = cotes_map.get(market)
        if not cote or cote <= 1.01:
            continue
        try:
            mger_res = analyse_mger(market, variables, cote=cote)
            oracle_res = analyse_oracle(
                variables, mger_res, cote,
                volume_donnees=volume,
                fraicheur_jours=fraicheur,
                completude=completude,
            )
            oracle_res["cote"] = cote
            resultats.append(oracle_res)
        except Exception as e:
            resultats.append({
                "market": market, "erreur": str(e), "accepte": False,
            })

    valides = [r for r in resultats if r.get("accepte")]
    meilleur = max(valides, key=lambda x: x["master_score"]) if valides else None

    return {
        "variables": variables,
        "qualite": {
            "volume": volume,
            "fraicheur": fraicheur,
            "completude": completude,
        },
        "resultats": resultats,
        "meilleur": meilleur,
                     }
