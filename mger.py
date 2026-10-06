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


# ---------- Matrice de dépendance ----------

def matrice_dependance(marches):
    """
    Estime la dépendance entre marchés à partir de leur nature.
    Pour l'instant : règles simples basées sur la logique du foot.
    Plus tard : estimée sur historique réel.
    """
    # Base : forte dépendance "structurelle"
    paires = {
        ("1", "2"): -0.95,   # 1 et 2 s'excluent
        ("1", "X"): -0.55,
        ("X", "2"): -0.55,
        ("O2.5", "U2.5"): -1.00,  # complémentaires
        ("O2.5", "BTTS"): 0.55,
        ("U2.5", "BTTS"): -0.35,
        ("1", "O2.5"): 0.25,
        ("2", "O2.5"): 0.20,
        ("1", "BTTS"): -0.10,
        ("2", "BTTS"): 0.15,
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


# ---------- Stress test ----------

def perturber_variables(variables, bruit=0.15):
    """Ajoute un bruit gaussien à chaque variable."""
    perturbees = {}
    for var, val in variables.items():
        delta = random.gauss(0, bruit)
        nouvelle = val + delta
        perturbees[var] = max(0.0, min(1.0, nouvelle))
    return perturbees


def stress_test(market, variables, n_sims=None, bruit=None):
    """
    Lance n simulations Monte Carlo en perturbant les variables.
    Retourne {p_central, p_min, p_max, p_values}.
    """
    n_sims = n_sims or MASTER["monte_carlo_sims"]
    bruit = bruit or MASTER["bruit_lambda"]

    # Probabilité centrale : sur variables non perturbées
    res_central = calculer_proba(market, variables)
    p_central = res_central["proba_calibree"]

    p_values = []
    for _ in range(n_sims):
        v_perturb = perturber_variables(variables, bruit)
        res = calculer_proba(market, v_perturb)
        p_values.append(res["proba_calibree"])

    p_values.sort()
    p_min = p_values[int(0.05 * n_sims)]  # percentile 5
    p_max = p_values[int(0.95 * n_sims)]  # percentile 95

    return {
        "market": market,
        "p_central": p_central,
        "p_min": p_min,
        "p_max": p_max,
        "p_values": p_values,
    }


# ---------- Robustesse ----------

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


# ---------- Edge Stability ----------

def edge_stability(p_values, cote):
    """
    ES = % de scénarios où EV > 0.
    """
    if not p_values or cote <= 0:
        return 0.0
    seuil_ev = 1.0 / cote  # proba break-even
    reussis = sum(1 for p in p_values if p > seuil_ev)
    return reussis / len(p_values)


# ---------- Pipeline complet MGE-R ----------

def analyse_mger(market, variables, cote=None):
    """
    Pipeline complet :
    1. Stress test
    2. Robustesse
    3. Edge Stability (si cote fournie)
    """
    st = stress_test(market, variables)
    rob = calculer_robustesse(st["p_min"], st["p_central"])
    niveau = classer_robustesse(rob)
    acceptable = est_acceptable(rob)

    resultat = {
        "market": market,
        "p_central": st["p_central"],
        "p_min": st["p_min"],
        "p_max": st["p_max"],
        "rob": rob,
        "niveau_rob": niveau,
        "acceptable": acceptable,
    }

    if cote:
        es = edge_stability(st["p_values"], cote)
        resultat["edge_stability"] = es

    return resultat


# ---------- Test local ----------

if __name__ == "__main__":
    exemple_variables = {
        "FORM": 0.72, "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
        "GOALS": 0.58, "ABS": 0.85, "H2H": 0.54, "MOT": 0.60, "GK": 0.65,
        "SET": 0.52, "STYLE": 0.63, "MARKET": 0.58,
    }

    cotes_test = {"1": 2.10, "X": 3.40, "2": 3.30,
                  "O2.5": 1.90, "U2.5": 1.90, "BTTS": 1.75}

    print("=== MGE-R ===")
    for m in ["1", "X", "2", "O2.5", "U2.5", "BTTS"]:
        res = analyse_mger(m, exemple_variables, cote=cotes_test[m])
        print(f"[{m}] P={res['p_central']:.3f} "
              f"ROB={res['rob']:.3f} ({res['niveau_rob']}) "
              f"ES={res.get('edge_stability', 0):.2f} "
              f"{'✅' if res['acceptable'] else '❌'}")
