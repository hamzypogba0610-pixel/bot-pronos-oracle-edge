"""
calibration.py — Moteur d'apprentissage de la calibration.
Enregistre les prédictions, les résultats réels, corrige les probas,
et alimente le Meta-Brain (auto-évaluation contextuelle).
"""

import json
from pathlib import Path

import metabrain


CALIBRATION_FILE = Path("calibration_data.json")


# ---------- Persistance ----------

def charger():
    if not CALIBRATION_FILE.exists():
        return {
            "bins": {},
            "historique": [],
            "stats": {},
        }
    try:
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"bins": {}, "historique": [], "stats": {}}


def sauver(data):
    try:
        with open(CALIBRATION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde calibration : {e}")


# ---------- Bins ----------

def _bin_key(proba, n_bins=20):
    idx = int(proba * n_bins)
    return str(min(idx, n_bins - 1))


def calibrer(proba_brute, market, data=None):
    """Corrige une probabilité via les bins observés."""
    data = data or charger()
    if market not in data["bins"]:
        return proba_brute

    bin_key = _bin_key(proba_brute)
    bin_data = data["bins"][market].get(bin_key)
    if not bin_data or bin_data["n"] < 3:
        return proba_brute

    freq_observee = bin_data["reussites"] / bin_data["n"]
    poids = min(1.0, bin_data["n"] / 20.0)
    return (1 - poids) * proba_brute + poids * freq_observee


# ---------- Enregistrement ----------

def enregistrer_pari(market, p_calibree, cote, score, rob, verdict,
                     regime="?", ligue="?"):
    """
    Enregistre un pari recommandé (statut = 'en attente').
    Inclut le régime et la ligue pour le Meta-Brain.
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
        "regime": regime,
        "ligue": ligue,
        "resultat": None,
    }
    data["historique"].append(pari)
    sauver(data)
    return pari["id"]


def enregistrer_resultat(pari_id, gagne):
    """
    Met à jour un pari avec son résultat réel.
    Alimente :
    - les bins de calibration
    - les stats globales
    - le Meta-Brain (par contexte)
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

    # --- Mise à jour du bin ---
    if market not in data["bins"]:
        data["bins"][market] = {}
    bin_key = _bin_key(p_calibree)
    if bin_key not in data["bins"][market]:
        data["bins"][market][bin_key] = {"n": 0, "reussites": 0}
    data["bins"][market][bin_key]["n"] += 1
    if gagne:
        data["bins"][market][bin_key]["reussites"] += 1

    # --- Mise à jour des stats globales ---
    if market not in data["stats"]:
        data["stats"][market] = {"total": 0, "gagnes": 0, "cote_moy": 0.0}
    s = data["stats"][market]
    s["cote_moy"] = (s["cote_moy"] * s["total"] + pari["cote"]) / (s["total"] + 1)
    s["total"] += 1
    if gagne:
        s["gagnes"] += 1

    sauver(data)

    # --- Alimentation du Meta-Brain ---
    try:
        metabrain.enregistrer_contexte(
            market=market,
            regime=pari.get("regime", "?"),
            ligue=pari.get("ligue", "?"),
            gagne=gagne,
        )
    except Exception as e:
        print(f"Erreur metabrain : {e}")

    return True


# ---------- Statistiques ----------

def get_stats():
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
    data = charger()
    return [p for p in data["historique"] if p["resultat"] is None]


def paris_recents(n=10):
    data = charger()
    resolus = [p for p in data["historique"] if p["resultat"] is not None]
    return resolus[-n:]


def reinitialiser():
    sauver({"bins": {}, "historique": [], "stats": {}})
