"""
calibration.py — Moteur d'apprentissage de la calibration.
Enregistre les prédictions, les résultats réels, et corrige les probas.
"""

import json
import os
from pathlib import Path

CALIBRATION_FILE = Path("calibration_data.json")


# ---------- Persistance ----------

def charger():
    """Charge les données de calibration depuis le disque."""
    if not CALIBRATION_FILE.exists():
        return {
            "bins": {},        # {"market": {"bin_key": {"n": int, "reussites": int}}}
            "historique": [],  # liste des paris enregistrés
            "stats": {},       # stats globales par marché
        }
    try:
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"bins": {}, "historique": [], "stats": {}}


def sauver(data):
    """Sauvegarde les données sur le disque."""
    try:
        with open(CALIBRATION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde calibration : {e}")


# ---------- Bins ----------

def _bin_key(proba, n_bins=20):
    """Retourne la clé de bin pour une probabilité (0..n_bins-1)."""
    idx = int(proba * n_bins)
    return str(min(idx, n_bins - 1))


def calibrer(proba_brute, market, data=None):
    """
    Corrige une probabilité brute en utilisant les bins observés.
    Formule : mélange entre proba brute et fréquence observée
    pondéré par le nombre d'observations (approche bayésienne simple).
    """
    data = data or charger()

    if market not in data["bins"]:
        return proba_brute

    bin_key = _bin_key(proba_brute)
    bin_data = data["bins"][market].get(bin_key)

    if not bin_data or bin_data["n"] < 3:
        return proba_brute

    freq_observee = bin_data["reussites"] / bin_data["n"]
    # Pondération par le nombre d'observations (max 20 matchs = confiance totale)
    poids = min(1.0, bin_data["n"] / 20.0)
    proba_calibree = (1 - poids) * proba_brute + poids * freq_observee
    return proba_calibree


# ---------- Enregistrement ----------

def enregistrer_pari(market, p_calibree, cote, score, rob, verdict):
    """
    Enregistre un pari recommandé (statut = 'en attente').
    Retourne l'id du pari.
    """
    data = charger()
    pari = {
        "id": len(data["historique"]) + 1,
        "market": market,
        "p_calibree": float(p_calibree),
        "cote": float(cote),
        "score_attribue": float(score),
        "rob": float(rob),
        "verdict": verdict,
        "resultat": None,  # None = en attente, True = gagné, False = perdu
    }
    data["historique"].append(pari)
    sauver(data)
    return pari["id"]


def enregistrer_resultat(pari_id, gagne):
    """
    Met à jour un pari avec son résultat réel et met à jour la calibration.
    gagne : True ou False.
    """
    data = charger()
    pari = None
    for p in data["historique"]:
        if p["id"] == pari_id:
            pari = p
            break

    if not pari or pari["resultat"] is not None:
        return False

    pari["resultat"] = bool(gagne)
    market = pari["market"]
    p_calibree = pari["p_calibree"]

    # Mise à jour du bin
    if market not in data["bins"]:
        data["bins"][market] = {}
    bin_key = _bin_key(p_calibree)

    if bin_key not in data["bins"][market]:
        data["bins"][market][bin_key] = {"n": 0, "reussites": 0}

    data["bins"][market][bin_key]["n"] += 1
    if gagne:
        data["bins"][market][bin_key]["reussites"] += 1

    # Mise à jour des stats
    if market not in data["stats"]:
        data["stats"][market] = {"total": 0, "gagnes": 0, "cote_moy": 0.0}

    s = data["stats"][market]
    s["cote_moy"] = (s["cote_moy"] * s["total"] + pari["cote"]) / (s["total"] + 1)
    s["total"] += 1
    if gagne:
        s["gagnes"] += 1

    sauver(data)
    return True


# ---------- Statistiques ----------

def get_stats():
    """Retourne les stats globales et par marché."""
    data = charger()
    stats = {}
    total_p = 0
    total_gagnes = 0

    for market, s in data["stats"].items():
        taux = s["gagnes"] / s["total"] if s["total"] > 0 else 0.0
        stats[market] = {
            "total": s["total"],
            "gagnes": s["gagnes"],
            "taux_reussite": taux,
            "cote_moy": s["cote_moy"],
        }
        total_p += s["total"]
        total_gagnes += s["gagnes"]

    stats["_global"] = {
        "total": total_p,
        "gagnes": total_gagnes,
        "taux_reussite": total_gagnes / total_p if total_p > 0 else 0.0,
    }
    return stats


def paris_en_attente():
    """Retourne la liste des paris sans résultat."""
    data = charger()
    return [p for p in data["historique"] if p["resultat"] is None]


def paris_recents(n=10):
    """Retourne les n derniers paris avec résultat."""
    data = charger()
    resolus = [p for p in data["historique"] if p["resultat"] is not None]
    return resolus[-n:]


def reinitialiser():
    """Efface toute la calibration (pour repartir à zéro)."""
    sauver({"bins": {}, "historique": [], "stats": {}})
