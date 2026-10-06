"""
gradient.py — Couche 3 : GRADIENT-X.
Optimisation automatique des poids W(i,m) par descente de gradient.

Chaque pari résolu met à jour les poids du marché correspondant
selon la règle : w_i ← w_i - η × (p - y) × x_i + λ × w_i
"""

import json
import math
from pathlib import Path

from config import VARIABLES, POIDS_MARCHE


GRADIENT_FILE = Path("gradient_data.json")

# --- Hyperparamètres ---
ETA = 0.05          # taux d'apprentissage
LAMBDA_L2 = 0.001   # régularisation L2
W_MIN = -40.0       # borne basse par poids
W_MAX = 40.0        # borne haute par poids
MIN_N = 10          # nombre mini de paris avant d'utiliser les poids appris


# ---------- Persistance ----------

def charger():
    if not GRADIENT_FILE.exists():
        return {"poids": {}, "compteurs": {}}
    try:
        with open(GRADIENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"poids": {}, "compteurs": {}}


def sauver(data):
    try:
        with open(GRADIENT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde gradient : {e}")


# ---------- Renormalisation ----------

def renormaliser(poids):
    """Ramène Σ|W| à 100."""
    total = sum(abs(v) for v in poids.values())
    if total == 0:
        return poids
    return {k: v * 100.0 / total for k, v in poids.items()}


# ---------- API principale ----------

def get_poids(market):
    """
    Retourne les poids à utiliser pour ce marché.
    Si assez de paris ont été appris → poids optimisés
    Sinon → poids initiaux de config.py
    """
    data = charger()
    n = data["compteurs"].get(market, 0)
    if n >= MIN_N and market in data["poids"]:
        return dict(data["poids"][market])
    return dict(POIDS_MARCHE.get(market, {}))


def get_compteur(market):
    data = charger()
    return data["compteurs"].get(market, 0)


def mettre_a_jour(market, variables, proba_predite, resultat_reel):
    """
    Effectue une étape de SGD pour le marché donné.
    - variables : dict {var: valeur ∈ [0, 1]}
    - proba_predite : p ∈ [0, 1]
    - resultat_reel : 1 (gagné) ou 0 (perdu)
    """
    data = charger()

    # Initialisation au premier appel
    if market not in data["poids"]:
        data["poids"][market] = dict(POIDS_MARCHE.get(market, {}))
    if market not in data["compteurs"]:
        data["compteurs"][market] = 0

    poids = data["poids"][market]
    erreur = proba_predite - resultat_reel  # p - y

    # Étape de gradient
    for var in VARIABLES:
        x_i = float(variables.get(var, 0.5))
        w_i = float(poids.get(var, 0.0))
        # dL/dw = (p - y) × x_i + λ × w_i
        grad = erreur * x_i + LAMBDA_L2 * w_i
        w_new = w_i - ETA * grad
        # Bornes
        w_new = max(W_MIN, min(W_MAX, w_new))
        poids[var] = round(w_new, 4)

    # Renormalisation pour garder Σ|W| = 100
    poids_renorm = renormaliser(poids)
    data["poids"][market] = {k: round(v, 4) for k, v in poids_renorm.items()}
    data["compteurs"][market] = data["compteurs"][market] + 1

    sauver(data)
    return True


# ---------- Statistiques ----------

def stats_gradient():
    """Retourne l'état d'apprentissage par marché."""
    data = charger()
    resultats = []
    for market in POIDS_MARCHE.keys():
        n = data["compteurs"].get(market, 0)
        actif = n >= MIN_N
        resultats.append({
            "market": market,
            "n": n,
            "actif": actif,
            "statut": "🟢 Optimisé" if actif else f"🟡 Init ({n}/{MIN_N})",
        })
    return sorted(resultats, key=lambda x: x["market"])


def ecart_vs_config(market):
    """
    Compare poids appris vs poids initiaux.
    Retourne les plus grands écarts (utile pour voir ce qui a changé).
    """
    data = charger()
    if market not in data["poids"]:
        return []
    poids_apris = data["poids"][market]
    poids_init = POIDS_MARCHE.get(market, {})
    ecarts = []
    for var in VARIABLES:
        w_a = poids_apris.get(var, 0)
        w_i = poids_init.get(var, 0)
        ecarts.append({
            "variable": var,
            "initial": w_i,
            "appris": w_a,
            "delta": w_a - w_i,
        })
    return sorted(ecarts, key=lambda x: -abs(x["delta"]))


def reinitialiser(market=None):
    """Réinitialise les poids appris (tout ou un seul marché)."""
    if market is None:
        sauver({"poids": {}, "compteurs": {}})
        return True
    data = charger()
    data["poids"].pop(market, None)
    data["compteurs"].pop(market, None)
    sauver(data)
    return True


# ---------- Test local ----------

if __name__ == "__main__":
    reinitialiser()
    print("=== Simulation GRADIENT-X ===\n")

    # Simulation : 30 paris sur "O2.5" où le bot a tendance à sous-estimer
    # (les vraies occurrences sont plus fréquentes que la prédiction)
    import random
    random.seed(42)
    for i in range(30):
        variables = {
            "FORM": 0.5 + random.random() * 0.4,
            "ATT": 0.6 + random.random() * 0.3,
            "DEF": 0.4 + random.random() * 0.3,
            "XG": 0.65 + random.random() * 0.25,
            "HOME": 0.55, "GOALS": 0.6, "ABS": 0.5, "H2H": 0.5,
            "MOT": 0.5, "GK": 0.5, "SET": 0.5, "STYLE": 0.6,
            "MARKET": 0.55,
        }
        p_pred = 0.55
        y_reel = 1 if random.random() < 0.65 else 0  # vraie fréquence 65%
        mettre_a_jour("O2.5", variables, p_pred, y_reel)

    print(f"Compteur O2.5 : {get_compteur('O2.5')} paris")
    print("\nÉcarts vs config (top 5) :")
    for e in ecart_vs_config("O2.5")[:5]:
        print(f"  {e['variable']:8s} : init {e['initial']:+.1f} → "
              f"appris {e['appris']:+.1f} (Δ {e['delta']:+.2f})")

    print("\nStats globales :")
    for s in stats_gradient()[:5]:
        print(f"  {s['market']:8s} : {s['statut']}")
