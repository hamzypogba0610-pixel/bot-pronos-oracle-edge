"""
combines.py — Moteur de combinés.
Utilise la matrice de dépendance MGE-R pour évaluer les paires de marchés.
"""

import math
from mger import matrice_dependance, classifier_dependance


# --- Conflits structurels (ne jamais combiner) ---
CONFLITS = {
    ("1", "2"), ("1", "X"), ("X", "2"),
    ("O0.5", "U0.5"), ("O1.5", "U1.5"),
    ("O2.5", "U2.5"), ("O3.5", "U3.5"),
    ("AH-0.5", "AH+0.5"),
    ("AH-1.5", "AH+1.5"),
    ("AH-2.5", "AH+2.5"),
    ("BTTS", "U0.5"),
}

# --- Marchés redondants (même sens, inutile de combiner) ---
REDONDANTS = {
    ("O1.5", "O2.5"), ("O2.5", "O3.5"), ("O1.5", "O3.5"),
    ("U1.5", "U2.5"), ("U2.5", "U3.5"), ("U1.5", "U3.5"),
    ("1", "AH-0.5"),
    ("X", "AH+0.5"),
    ("2", "AH+0.5"),
    ("1", "AH-1.5"),
    ("2", "AH-1.5"),
    ("1", "AH-2.5"),
    ("2", "AH-2.5"),
    ("O2.5", "O1.5"),
    ("U2.5", "U1.5"),
}


def est_conflit(a, b):
    return (a, b) in CONFLITS or (b, a) in CONFLITS


def est_redondant(a, b):
    return (a, b) in REDONDANTS or (b, a) in REDONDANTS


def proba_combinee(p_a, p_b, rho):
    """
    Probabilité de A ∧ B ajustée par corrélation ρ.
    Formule : P(A)×P(B) + ρ × sqrt(P(A)(1-P(A)) × P(B)(1-P(B)))
    """
    if p_a <= 0 or p_a >= 1 or p_b <= 0 or p_b >= 1:
        return max(0.01, min(0.99, p_a * p_b))
    cov = rho * math.sqrt(p_a * (1 - p_a) * p_b * (1 - p_b))
    p = p_a * p_b + cov
    return max(0.01, min(0.99, p))


def generer_combines(resultats_marches, top_n=10, ev_min=0.0):
    """
    Prend la liste des résultats par marché (issus d'analyse.py).
    Retourne les meilleurs combinés triés par EV décroissant.
    """
    marches = {
        r["market"]: r for r in resultats_marches
        if "p_calibree" in r and "cote" in r
    }
    noms = list(marches.keys())
    dep = matrice_dependance(noms)

    combines = []
    for i, a in enumerate(noms):
        for b in noms[i + 1:]:
            if est_conflit(a, b):
                continue
            if est_redondant(a, b):
                continue

            p_a = marches[a]["p_calibree"]
            p_b = marches[b]["p_calibree"]
            cote_a = marches[a]["cote"]
            cote_b = marches[b]["cote"]
            rho = dep.get(a, {}).get(b, 0.0)

            p_comb = proba_combinee(p_a, p_b, rho)
            cote_comb = cote_a * cote_b
            ev = p_comb * cote_comb - 1

            if ev < ev_min:
                continue

            rob_a = marches[a].get("rob", 1.0)
            rob_b = marches[b].get("rob", 1.0)
            rob = min(rob_a, rob_b)

            combines.append({
                "marche_a": a,
                "marche_b": b,
                "p_a": p_a,
                "p_b": p_b,
                "rho": rho,
                "p_combinee": p_comb,
                "cote_combinee": cote_comb,
                "ev": ev,
                "rob": rob,
                "type": classifier_dependance(rho),
                "verdict": _classer_combine(ev, rob),
            })

    combines.sort(key=lambda x: -x["ev"])
    return combines[:top_n]


def _classer_combine(ev, rob):
    if rob < 0.75:
        return "🔴 ROB FAIBLE"
    if ev < 0.05:
        return "🟡 EV FAIBLE"
    if ev < 0.15:
        return "🟡 INTÉRESSANT"
    if ev < 0.30:
        return "🟢 FORT"
    return "💎 EXCEPTIONNEL"


# --- Test local ---
if __name__ == "__main__":
    exemple = [
        {"market": "1", "p_calibree": 0.52, "cote": 2.10, "rob": 0.90},
        {"market": "O2.5", "p_calibree": 0.58, "cote": 1.90, "rob": 0.93},
        {"market": "BTTS", "p_calibree": 0.61, "cote": 1.75, "rob": 0.89},
        {"market": "U3.5", "p_calibree": 0.72, "cote": 1.35, "rob": 0.91},
    ]
    for c in generer_combines(exemple, top_n=5):
        print(f"{c['marche_a']} + {c['marche_b']} : "
              f"P={c['p_combinee']:.1%} · Cote={c['cote_combinee']:.2f} · "
              f"EV={c['ev']:+.1%} · ρ={c['rho']:+.2f} · {c['verdict']}")
