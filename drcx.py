"""
drcx.py — Cerveau 1 : DRC-X
Probabilité brute + calibration.
"""

import math
import json
from pathlib import Path

from config import POIDS_MARCHE, VARIABLES
from variables import sigmoide
from poids import calculer_poids_final


# ---------- Calibration ----------

CALIBRATION_FILE = Path("calibration.json")


def charger_calibration():
    """Charge la table de calibration (ou vide si absente)."""
    if CALIBRATION_FILE.exists():
        with open(CALIBRATION_FILE, "r") as f:
            return json.load(f)
    return {}


def sauver_calibration(table):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(table, f, indent=2)


def calibrer(proba_brute, market, table):
    """
    Calibration par table de correspondance (isotonic simplifiée).
    On découpe [0, 1] en bins de 5% et on corrige selon l'historique.
    """
    if market not in table:
        return proba_brute

    bins = table[market]
    bin_key = str(int(proba_brute * 20))  # 0..20
    if bin_key in bins:
        return bins[bin_key]
    return proba_brute


def mettre_a_jour_calibration(table, market, proba_annoncee, resultat_reel):
    """
    Met à jour la table de calibration après un résultat observé.
    resultat_reel : 1 si l'événement s'est produit, 0 sinon.
    """
    if market not in table:
        table[market] = {}

    bin_key = str(int(proba_annoncee * 20))
    if bin_key not in table[market]:
        table[market][bin_key] = {"somme_probas": 0.0, "somme_resultats": 0.0, "n": 0}

    b = table[market][bin_key]
    b["somme_probas"] += proba_annoncee
    b["somme_resultats"] += resultat_reel
    b["n"] += 1

    # Moyenne observée
    freq_observee = b["somme_resultats"] / b["n"]
    # Correction vers la fréquence observée
    table[market][bin_key]["valeur_calibree"] = freq_observee
    return table


# ---------- Calcul principal ----------

def score_fondamental(variables, poids):
    """Z_m = Σ W(i,m) × X_i."""
    z = 0.0
    for var in VARIABLES:
        w = poids.get(var, 0.0)
        x = variables.get(var, 0.5)
        z += w * x
    # On normalise Z pour rentrer dans la sigmoïde
    return z / 100.0


def proba_brute(z, k=4.0):
    """
    Transforme Z en probabilité.
    k contrôle la pente de la sigmoïde. À calibrer.
    """
    return sigmoide(z, k=k)


def calculer_proba(market, variables, historique=None,
                   gap_niveau=0.5, calibrer_resultat=True):
    """
    Pipeline DRC-X :
    1. Récupère les poids ajustés (via poids.py)
    2. Calcule Z
    3. Transforme en proba brute
    4. Calibre
    Retourne dict : {proba_brute, proba_calibree, regime, poids}
    """
    poids, regime = calculer_poids_final(
        market, variables, historique=historique, gap_niveau=gap_niveau
    )
    z = score_fondamental(variables, poids)
    p_brute = proba_brute(z)

    table = charger_calibration()
    p_cal = calibrer(p_brute, market, table) if calibrer_resultat else p_brute

    return {
        "market": market,
        "regime": regime,
        "poids": poids,
        "z": z,
        "proba_brute": p_brute,
        "proba_calibree": p_cal,
    }


# ---------- Test local ----------

if __name__ == "__main__":
    # Exemple de test avec des variables fictives
    exemple_variables = {
        "FORM": 0.72, "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
        "GOALS": 0.58, "ABS": 0.85, "H2H": 0.54, "MOT": 0.60, "GK": 0.65,
        "SET": 0.52, "STYLE": 0.63, "MARKET": 0.58,
    }

    for m in ["1", "X", "2", "O2.5", "U2.5", "BTTS"]:
        res = calculer_proba(m, exemple_variables)
        print(f"[{m}] brut={res['proba_brute']:.3f} "
              f"cal={res['proba_calibree']:.3f} "
              f"régime={res['regime']}")
