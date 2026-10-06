"""
poids.py — Gestion des poids W(i,m) par marché + régimes + anti-redondance.

Source des poids :
- Au démarrage : poids initiaux de config.POIDS_MARCHE
- Après 10 paris par marché : poids optimisés par gradient.py (GRADIENT-X)
"""

import math
from config import POIDS_MARCHE, REGIMES, VARIABLES
import gradient


# ---------- Détection du régime ----------

def detecter_regime(variables, gap_niveau=0.5):
    """
    Classifie le match dans un des 5 régimes A/B/C/D/E.
    Priorité stricte : E > C > B > A > D.
    """
    xg_total = variables.get("XG", 0.5) * 2

    vals = list(variables.values())
    moy = sum(vals) / len(vals)
    variance = sum((v - moy) ** 2 for v in vals) / len(vals)
    chaos_early = math.sqrt(variance)

    gap = gap_niveau

    if chaos_early > 0.50:
        return "E"
    if gap > 0.60:
        return "C"
    if xg_total > 1.40:
        return "B"
    if xg_total < 0.90:
        return "A"
    return "D"


# ---------- Application du régime ----------

def appliquer_regime(poids, regime):
    multiplicateurs = REGIMES.get(regime, {})
    return {
        var: poids.get(var, 0) * multiplicateurs.get(var, 1.0)
        for var in VARIABLES
    }


# ---------- Anti-redondance ----------

def matrice_correlation(historique_variables):
    n = len(historique_variables)
    if n < 2:
        return {v1: {v2: 0.0 for v2 in VARIABLES} for v1 in VARIABLES}

    moyennes = {v: sum(h[v] for h in historique_variables) / n for v in VARIABLES}
    ecarts = {
        v: [h[v] - moyennes[v] for h in historique_variables]
        for v in VARIABLES
    }
    ecarts_types = {
        v: math.sqrt(sum(e ** 2 for e in ecarts[v]) / n)
        for v in VARIABLES
    }

    corr = {v1: {} for v1 in VARIABLES}
    for v1 in VARIABLES:
        for v2 in VARIABLES:
            if v1 == v2:
                corr[v1][v2] = 1.0
                continue
            if ecarts_types[v1] == 0 or ecarts_types[v2] == 0:
                corr[v1][v2] = 0.0
                continue
            cov = sum(ecarts[v1][i] * ecarts[v2][i] for i in range(n)) / n
            corr[v1][v2] = cov / (ecarts_types[v1] * ecarts_types[v2])
    return corr


def reduire_redundance(poids, correlation, seuil=0.70):
    poids_ajuste = dict(poids)
    deja_traite = set()

    for v1 in VARIABLES:
        for v2 in VARIABLES:
            if v1 == v2 or (v1, v2) in deja_traite or (v2, v1) in deja_traite:
                continue
            c = abs(correlation.get(v1, {}).get(v2, 0.0))
            if c > seuil:
                facteur = 1.0 + c
                poids_ajuste[v1] = poids_ajuste.get(v1, 0) / facteur
                poids_ajuste[v2] = poids_ajuste.get(v2, 0) / facteur
                deja_traite.add((v1, v2))
    return poids_ajuste


# ---------- Renormalisation ----------

def renormaliser(poids):
    total = sum(abs(v) for v in poids.values())
    if total == 0:
        return poids
    return {k: v * 100.0 / total for k, v in poids.items()}


# ---------- Fonction principale ----------

def calculer_poids_final(market, variables, historique=None, gap_niveau=0.5):
    """
    Pipeline complet :
    1. Récupère les poids (optimisés par gradient si dispo, sinon config)
    2. Détection du régime
    3. Application des multiplicateurs
    4. Anti-redondance (si historique dispo)
    5. Renormalisation
    """
    if market not in POIDS_MARCHE:
        raise ValueError(f"Marché inconnu : {market}")

    # --- Source des poids : gradient (si appris) sinon config ---
    try:
        poids = dict(gradient.get_poids(market))
    except Exception:
        poids = dict(POIDS_MARCHE[market])

    # Si gradient retourne vide → fallback config
    if not poids:
        poids = dict(POIDS_MARCHE[market])

    regime = detecter_regime(variables, gap_niveau)
    poids = appliquer_regime(poids, regime)

    if historique and len(historique) >= 5:
        corr = matrice_correlation(historique)
        poids = reduire_redundance(poids, corr)

    poids = renormaliser(poids)
    return poids, regime
