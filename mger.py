"""
mger.py — Cerveau 2 : MGE-R
Dépendance + stress test + robustesse.
"""

import random
import math
from config import (
    VARIABLES, MASTER, POIDS_MARCHE, ROB_SEUILS, ROB_MIN_ACCEPTATION
)
from drcx import calculer_proba


def matrice_dependance(marches):
    paires = {
        ("1", "2"): -0.95, ("1", "X"): -0.55, ("X", "2"): -0.55,
        ("O2.5", "U2.5"): -1.00, ("O2.5", "BTTS"): 0.55,
        ("U2.5", "BTTS"): -0.35,
        ("1", "O2.5"): 0.25, ("2", "O2.5"): 0.20,
        ("1", "BTTS"): -0.10, ("2", "BTTS"): 0.15,
        ("X", "U2.5"): 0.30,
    }

    def rho(a, b):
        if a == b:
            return 1.0
        if (a, b) in paires:
            return paires[(a, b)]
        if (b, a) in paires:
            return paires[(b, a)]
        return 0.0

    return {a: {b: rho(a, b) for b in marches} for a in marches}


def classifier_dependance(rho):
    if abs(rho) >= 0.70:
        return "🔴 CONFLIT" if rho < 0 else "🟢 SYNERGIE"
    if abs(rho) >= 0.35:
        return "🟡 DÉPENDANCE MODÉRÉE"
    return "⚪ INDÉPENDANT"


def perturber_variables(variables, bruit=0.15):
    perturbees = {}
    for var, val in variables.items():
        delta = random.gauss(0, bruit)
        perturbees[var] = max(0.0, min(1.0, val + delta))
    return perturbees


def stress_test(market, variables, n_sims=None, bruit=None, ligue="?"):
    n_sims = n_sims or MASTER["monte_carlo_sims"]
    bruit = bruit or MASTER["bruit_lambda"]

    res_central = calculer_proba(market, variables, ligue=ligue)
    p_central = res_central["proba_calibree"]

    p_values = []
    for _ in range(n_sims):
        v_perturb = perturber_variables(variables, bruit)
        res = calculer_proba(market, v_perturb, ligue=ligue)
        p_values.append(res["proba_calibree"])

    p_values.sort()
    p_min = p_values[int(0.05 * n_sims)]
    p_max = p_values[int(0.95 * n_sims)]

    return {
        "market": market, "p_central": p_central,
        "p_min": p_min, "p_max": p_max, "p_values": p_values,
    }


def calculer_robustesse(p_min, p_central):
    if p_central == 0:
        return 0.0
    return p_min / p_central


def classer_robustesse(rob):
    if rob >= ROB_SEUILS["EXCELLENT"]:
        return "EXCELLENT"
    if rob >= ROB_SEUILS["ROBUSTE"]:
        return "ROBUSTE"
    if rob >= ROB_SEUILS["MOYEN"]:
        return "MOYEN"
    if rob >= ROB_SEUILS["FRAGILE"]:
        return "FRAGILE"
    return "REJET"


def est_acceptable(rob):
    return rob >= ROB_MIN_ACCEPTATION


def edge_stability(p_values, cote):
    if not p_values or cote <= 0:
        return 0.0
    seuil_ev = 1.0 / cote
    reussis = sum(1 for p in p_values if p > seuil_ev)
    return reussis / len(p_values)


def analyse_mger(market, variables, cote=None, ligue="?"):
    st = stress_test(market, variables, ligue=ligue)
    rob = calculer_robustesse(st["p_min"], st["p_central"])
    niveau = classer_robustesse(rob)
    acceptable = est_acceptable(rob)

    resultat = {
        "market": market,
        "p_central": st["p_central"],
        "p_min": st["p_min"], "p_max": st["p_max"],
        "rob": rob, "niveau_rob": niveau, "acceptable": acceptable,
    }
    if cote:
        resultat["edge_stability"] = edge_stability(st["p_values"], cote)
    return resultat
