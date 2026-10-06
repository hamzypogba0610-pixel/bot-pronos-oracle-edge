"""
score_matrix.py — Matrice de scores exacts.
Poisson bivarié + correction Dixon-Coles.

Sert à calculer la probabilité de chaque score exact (0-0, 1-0, 2-1, ...).
"""

import math
from config import MAX_GOALS_MATRIX


# ---------- Lambda (buts attendus) ----------

def calculer_lambdas(variables):
    """
    Estime λ_home et λ_away à partir des 13 variables.
    Formule simple :
      λ_home = base_home × ATT_home × (1 - DEF_away/2) × avantage_dom
      λ_away = base_away × ATT_away × (1 - DEF_home/2)
    """
    att = variables.get("ATT", 0.5)
    defense = variables.get("DEF", 0.5)
    xg = variables.get("XG", 0.5)
    home_adv = variables.get("HOME", 0.5)

    # Base : ~1.35 buts par équipe en moyenne (5 grands championnats)
    base = 1.35

    # Attaque : entre 0.5x et 1.5x selon la valeur
    mult_att = 0.5 + att

    # Défense adverse : plus elle est forte, moins on marque
    # DEF élevé = bonne défense → réduit l'adversaire
    # On utilise défense de l'adversaire en paramètre séparé
    mult_xg = 0.5 + xg

    # Avantage domicile : léger bonus
    dom_bonus = 0.85 + home_adv * 0.3

    lam_home = base * mult_att * mult_xg * dom_bonus
    lam_away = base * mult_att * mult_xg * 0.85

    # Bornes de sécurité
    lam_home = max(0.3, min(4.5, lam_home))
    lam_away = max(0.3, min(4.5, lam_away))

    return lam_home, lam_away


# ---------- Poisson ----------

def poisson_pmf(k, lam):
    """Probabilité d'observer k buts si λ = lam."""
    if lam <= 0:
        return 0.0 if k > 0 else 1.0
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


# ---------- Dixon-Coles ----------

def tau(i, j, lam_h, lam_a, rho=-0.13):
    """
    Correction Dixon-Coles.
    Ajuste les 4 scores faibles : 0-0, 1-0, 0-1, 1-1.
    """
    if i == 0 and j == 0:
        return 1 - lam_h * lam_a * rho
    if i == 0 and j == 1:
        return 1 + lam_h * rho
    if i == 1 and j == 0:
        return 1 + lam_a * rho
    if i == 1 and j == 1:
        return 1 - rho
    return 1.0


def construire_matrice(lam_h, lam_a, n_max=None, rho=-0.13):
    """
    Construit une matrice (n_max+1)×(n_max+1) avec P(i, j).
    Correction Dixon-Coles appliquée.
    """
    n = n_max or MAX_GOALS_MATRIX
    mat = [[0.0] * (n + 1) for _ in range(n + 1)]

    total = 0.0
    for i in range(n + 1):
        for j in range(n + 1):
            p = poisson_pmf(i, lam_h) * poisson_pmf(j, lam_a)
            p *= tau(i, j, lam_h, lam_a, rho)
            p = max(0.0, p)  # éviter les valeurs négatives du DC
            mat[i][j] = p
            total += p

    # Renormalisation
    if total > 0:
        for i in range(n + 1):
            for j in range(n + 1):
                mat[i][j] /= total

    return mat


# ---------- Extraction ----------

def proba_score(mat, score_str):
    """
    Retourne la proba d'un score exact au format "2-1".
    """
    try:
        a, b = score_str.split("-")
        i, j = int(a.strip()), int(b.strip())
    except (ValueError, AttributeError):
        return None

    if 0 <= i < len(mat) and 0 <= j < len(mat[0]):
        return mat[i][j]
    return 0.0


def top_scores(mat, n=5):
    """Retourne les n scores les plus probables."""
    scores = []
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            scores.append((f"{i}-{j}", mat[i][j]))
    scores.sort(key=lambda x: -x[1])
    return scores[:n]


# ---------- Test local ----------

if __name__ == "__main__":
    variables = {
        "ATT": 0.68, "DEF": 0.61, "XG": 0.74, "HOME": 0.66,
    }
    lam_h, lam_a = calculer_lambdas(variables)
    print(f"λ_home = {lam_h:.2f}  λ_away = {lam_a:.2f}")

    mat = construire_matrice(lam_h, lam_a)
    print("\nTop 5 scores :")
    for score, p in top_scores(mat):
        print(f"  {score} : {p:.2%}")
