"""
shin.py — Couche 3 : SHIN-X.
Retrait de marge optimal par la méthode Shin (Princeton, Hyun Song Shin).

Au lieu de retirer la marge proportionnellement (naïf),
on modélise l'insider trading pour obtenir des probas "vraies".
"""

import math


# ---------- Formule Shin ----------

def _pi_shin(p_i, s, z):
    """
    Probabilité individuelle selon Shin.
    p_i : proba implicite brute (1/cote)
    s   : somme des probas brutes
    z   : paramètre d'insider trading ∈ [0, 1[
    """
    if z >= 1.0:
        return p_i / s  # fallback
    numerateur = math.sqrt(z * z + 4 * (1 - z) * (p_i * p_i) / s) - z
    return numerateur / (2 * (1 - z))


def _somme_shin(cotes, z):
    """Calcule Σ π_i(z)."""
    p_list = [1.0 / c for c in cotes if c > 1.01]
    s = sum(p_list)
    if s <= 0:
        return 0.0
    return sum(_pi_shin(p, s, z) for p in p_list)


def _trouver_z(cotes, tol=1e-6, max_iter=100):
    """
    Trouve z ∈ [0, 1[ tel que Σ π_i(z) = 1.
    Recherche par dichotomie.
    """
    if not cotes or len(cotes) < 2:
        return 0.0

    p_list = [1.0 / c for c in cotes if c > 1.01]
    if not p_list:
        return 0.0
    s = sum(p_list)
    if s <= 1.0:  # pas de marge (rare)
        return 0.0

    # Dichotomie : Σ π(0) > 1 (car s > 1) et Σ π(z→1) = 1
    a, b = 0.0, 0.9999
    for _ in range(max_iter):
        m = (a + b) / 2.0
        somme = _somme_shin(cotes, m)
        if abs(somme - 1.0) < tol:
            return m
        if somme > 1.0:
            a = m
        else:
            b = m
    return (a + b) / 2.0


# ---------- API principale ----------

def retirer_marge_shin(cotes):
    """
    Prend une liste de cotes [1X2] ou [Over, Under].
    Retourne une liste de probas "vraies" (somme = 1).
    """
    if not cotes or len(cotes) < 2:
        return []

    z = _trouver_z(cotes)
    p_list = [1.0 / c for c in cotes if c > 1.01]
    s = sum(p_list)

    probas = []
    for c in cotes:
        if c <= 1.01:
            probas.append(0.0)
            continue
        p_i = 1.0 / c
        probas.append(_pi_shin(p_i, s, z))

    # Normalisation finale (sécurité)
    total = sum(probas)
    if total > 0:
        probas = [p / total for p in probas]

    return probas


def retirer_marge_proportionnel(cotes):
    """Méthode naïve pour comparaison."""
    if not cotes:
        return []
    p_list = [1.0 / c for c in cotes if c > 1.01]
    s = sum(p_list)
    if s <= 0:
        return [0.0] * len(cotes)
    return [p / s for p in p_list]


def analyser_marche(cotes, noms=None):
    """
    Analyse complète : Shin vs Proportionnel.
    Retourne un dict avec les deux méthodes et le z trouvé.
    """
    if not cotes or len(cotes) < 2:
        return {"erreur": "Pas assez de cotes"}

    z = _trouver_z(cotes)
    shin = retirer_marge_shin(cotes)
    prop = retirer_marge_proportionnel(cotes)

    # Marge du book
    p_brut = [1.0 / c for c in cotes if c > 1.01]
    marge = sum(p_brut) - 1.0

    resultat = {
        "z": z,
        "marge_book": marge,
        "cotes": cotes,
        "probas_shin": shin,
        "probas_proportionnelles": prop,
        "noms": noms or [f"sel_{i}" for i in range(len(cotes))],
    }
    return resultat


# ---------- Test local ----------

if __name__ == "__main__":
    print("=== Test Shin vs Proportionnel ===\n")

    # Cas 1 : 1X2 équilibré
    cotes_1x2 = [2.10, 3.40, 3.50]
    res = analyser_marche(cotes_1x2, ["Dom", "Nul", "Ext"])
    print(f"1X2 : {cotes_1x2}")
    print(f"  Marge book : {res['marge_book']:.2%}")
    print(f"  z (insider) : {res['z']:.4f}")
    for i, nom in enumerate(res["noms"]):
        print(f"  {nom:6s} → Shin {res['probas_shin'][i]:.2%} | "
              f"Prop {res['probas_proportionnelles'][i]:.2%}")

    # Cas 2 : Favori net
    print()
    cotes_fav = [1.20, 6.50, 12.00]
    res2 = analyser_marche(cotes_fav, ["Fav", "Nul", "Out"])
    print(f"Favori net : {cotes_fav}")
    print(f"  Marge book : {res2['marge_book']:.2%}")
    print(f"  z (insider) : {res2['z']:.4f}")
    for i, nom in enumerate(res2["noms"]):
        print(f"  {nom:6s} → Shin {res2['probas_shin'][i]:.2%} | "
              f"Prop {res2['probas_proportionnelles'][i]:.2%}")

    # Cas 3 : Over/Under
    print()
    cotes_ou = [1.90, 1.95]
    res3 = analyser_marche(cotes_ou, ["Over", "Under"])
    print(f"O/U : {cotes_ou}")
    print(f"  Marge book : {res3['marge_book']:.2%}")
    print(f"  z (insider) : {res3['z']:.4f}")
    for i, nom in enumerate(res3["noms"]):
        print(f"  {nom:6s} → Shin {res3['probas_shin'][i]:.2%} | "
              f"Prop {res3['probas_proportionnelles'][i]:.2%}")
