"""
drcx.py — Cerveau 1 : DRC-X
Probabilité brute (baseline + z) + calibration.
"""

import math

from config import POIDS_MARCHE, VARIABLES, BASELINES
from variables import sigmoide
from poids import calculer_poids_final
import calibration as calib


def _logit(p):
    p = max(0.001, min(0.999, p))
    return math.log(p / (1 - p))


def _sigmoide_inverse(x):
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def score_fondamental(variables, poids):
    z = 0.0
    for var in VARIABLES:
        w = poids.get(var, 0.0)
        x = variables.get(var, 0.5)
        z += w * (x - 0.5)
    return z / 100.0


def proba_brute(z, baseline, k=2.5):
    logit_base = _logit(baseline)
    return _sigmoide_inverse(logit_base + k * z)


def calculer_proba(market, variables, historique=None,
                   gap_niveau=0.5, calibrer_resultat=True, ligue="?"):
    poids, regime = calculer_poids_final(
        market, variables, historique=historique,
        gap_niveau=gap_niveau, ligue=ligue,
    )
    z = score_fondamental(variables, poids)
    baseline = BASELINES.get(market, 0.50)
    p_brute = proba_brute(z, baseline)

    if calibrer_resultat:
        p_cal = calib.calibrer(p_brute, market)
    else:
        p_cal = p_brute

    return {
        "market": market, "regime": regime, "poids": poids,
        "z": z, "baseline": baseline,
        "proba_brute": p_brute, "proba_calibree": p_cal,
    }


def enregistrer_prediction(market, resultat_oracle, cote,
                            regime="?", ligue="?", variables=None):
    return calib.enregistrer_pari(
        market=market,
        p_calibree=resultat_oracle["p_calibree"],
        cote=cote,
        score=resultat_oracle["master_score"],
        rob=resultat_oracle["rob"],
        verdict=resultat_oracle["verdict"],
        regime=regime, ligue=ligue, variables=variables,
    )
