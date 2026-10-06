"""
drcx.py — Cerveau 1 : DRC-X
Probabilité brute + calibration.
"""

from config import POIDS_MARCHE, VARIABLES
from variables import sigmoide
from poids import calculer_poids_final
import calibration as calib


# ---------- Score fondamental ----------

def score_fondamental(variables, poids):
    """
    Z_m = Σ W(i,m) × (X_i − 0.5), normalisé sur 100.
    Centrage sur 0.5 : si toutes les variables sont neutres → Z = 0.
    """
    z = 0.0
    for var in VARIABLES:
        w = poids.get(var, 0.0)
        x = variables.get(var, 0.5)
        z += w * (x - 0.5)
    return z / 100.0


def proba_brute(z, k=2.5):
    return sigmoide(z, k=k)


# ---------- Pipeline DRC-X ----------

def calculer_proba(market, variables, historique=None,
                   gap_niveau=0.5, calibrer_resultat=True):
    poids, regime = calculer_poids_final(
        market, variables, historique=historique, gap_niveau=gap_niveau
    )
    z = score_fondamental(variables, poids)
    p_brute = proba_brute(z)

    if calibrer_resultat:
        p_cal = calib.calibrer(p_brute, market)
    else:
        p_cal = p_brute

    return {
        "market": market,
        "regime": regime,
        "poids": poids,
        "z": z,
        "proba_brute": p_brute,
        "proba_calibree": p_cal,
    }


# ---------- Helpers pour l'enregistrement ----------

def enregistrer_prediction(market, resultat_oracle, cote,
                            regime="?", ligue="?", variables=None):
    """
    Enregistre un pari recommandé dans l'historique.
    - variables : dict des 14 variables (pour GRADIENT-X)
    """
    return calib.enregistrer_pari(
        market=market,
        p_calibree=resultat_oracle["p_calibree"],
        cote=cote,
        score=resultat_oracle["master_score"],
        rob=resultat_oracle["rob"],
        verdict=resultat_oracle["verdict"],
        regime=regime,
        ligue=ligue,
        variables=variables,
    )


# ---------- Test local ----------

if __name__ == "__main__":
    exemple_variables = {
        "FORM": 0.72, "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
        "GOALS": 0.58, "ABS": 0.85, "H2H": 0.54, "MOT": 0.60, "GK": 0.65,
        "SET": 0.52, "STYLE": 0.63, "MARKET": 0.58, "ELO": 0.62,
    }

    for m in ["1", "X", "2", "O2.5", "U2.5", "BTTS"]:
        res = calculer_proba(m, exemple_variables)
        print(f"[{m}] brut={res['proba_brute']:.3f} "
              f"cal={res['proba_calibree']:.3f} "
              f"régime={res['regime']}")
