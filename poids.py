"""
poids.py — Gestion des poids W(i,m) par marché.
Applique multiplicateurs de TYPE (famille) puis de RÉGIME.
"""

import math
from config import POIDS_MARCHE, REGIMES, MULT_TYPES, LEAGUES, VARIABLES
import gradient


def _get_famille(ligue):
    """Retourne la famille de la compétition (défaut : TOP_EUROPE)."""
    if not ligue or ligue not in LEAGUES:
        return "TOP_EUROPE"
    return LEAGUES[ligue].get("famille", "TOP_EUROPE")


def detecter_regime(variables, gap_niveau=0.5):
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


def appliquer_type(poids, famille):
    """Applique les multiplicateurs de famille de compétition."""
    mults = MULT_TYPES.get(famille, MULT_TYPES["TOP_EUROPE"])
    return {var: poids.get(var, 0) * mults.get(var, 1.0) for var in VARIABLES}


def appliquer_regime(poids, regime):
    multiplicateurs = REGIMES.get(regime, {})
    return {var: poids.get(var, 0) * multiplicateurs.get(var, 1.0)
            for var in VARIABLES}


def matrice_correlation(historique_variables):
    n = len(historique_variables)
    if n < 2:
        return {v1: {v2: 0.0 for v2 in VARIABLES} for v1 in VARIABLES}
    moyennes = {v: sum(h[v] for h in historique_variables) / n for v in VARIABLES}
    ecarts = {v: [h[v] - moyennes[v] for h in historique_variables] for v in VARIABLES}
    ecarts_types = {v: math.sqrt(sum(e ** 2 for e in ecarts[v]) / n) for v in VARIABLES}
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
    deja = set()
    for v1 in VARIABLES:
        for v2 in VARIABLES:
            if v1 == v2 or (v1, v2) in deja or (v2, v1) in deja:
                continue
            c = abs(correlation.get(v1, {}).get(v2, 0.0))
            if c > seuil:
                f = 1.0 + c
                poids_ajuste[v1] = poids_ajuste.get(v1, 0) / f
                poids_ajuste[v2] = poids_ajuste.get(v2, 0) / f
                deja.add((v1, v2))
    return poids_ajuste


def renormaliser(poids):
    total = sum(abs(v) for v in poids.values())
    if total == 0:
        return poids
    return {k: v * 100.0 / total for k, v in poids.items()}


def calculer_poids_final(market, variables, historique=None,
                         gap_niveau=0.5, ligue="?"):
    """
    Pipeline : base → famille (type) → régime → anti-redondance → renormalisation.
    """
    if market not in POIDS_MARCHE:
        raise ValueError(f"Marché inconnu : {market}")

    # 1. Poids de base (optimisés si disponibles)
    try:
        poids = dict(gradient.get_poids(market))
    except Exception:
        poids = dict(POIDS_MARCHE[market])
    if not poids:
        poids = dict(POIDS_MARCHE[market])

    # 2. Famille de compétition
    famille = _get_famille(ligue)
    poids = appliquer_type(poids, famille)

    # 3. Régime
    regime = detecter_regime(variables, gap_niveau)
    poids = appliquer_regime(poids, regime)

    # 4. Anti-redondance
    if historique and len(historique) >= 5:
        corr = matrice_correlation(historique)
        poids = reduire_redundance(poids, corr)

    # 5. Renormalisation
    poids = renormaliser(poids)
    return poids, regime
