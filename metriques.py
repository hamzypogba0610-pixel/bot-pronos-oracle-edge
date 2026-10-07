"""
metriques.py — Mesures de qualité de la calibration.
Brier Score, Log Loss, Expected Calibration Error (ECE).

Ces métriques disent si le bot est vraiment fiable,
pas juste s'il a "gagné ou perdu" des paris.
"""

import math


def _paris_resolus(historique):
    """Filtre les paris avec un résultat connu (Gagné/Perdu)."""
    return [p for p in historique if p.get("resultat") is not None]


def brier_score(historique):
    """
    BS = (1/N) × Σ (p − y)²
    - 0.00 = parfait
    - 0.25 = neutre (comme prédire 50/50)
    - 1.00 = pire
    """
    paris = _paris_resolus(historique)
    if not paris:
        return None
    total = 0.0
    for p in paris:
        proba = p["p_calibree"]
        reel = 1.0 if p["resultat"] else 0.0
        total += (proba - reel) ** 2
    return total / len(paris)


def log_loss(historique):
    """
    LL = -(1/N) × Σ [y·log(p) + (1-y)·log(1-p)]
    Pénalise fortement les erreurs confiantes.
    """
    paris = _paris_resolus(historique)
    if not paris:
        return None
    total = 0.0
    for p in paris:
        proba = max(0.001, min(0.999, p["p_calibree"]))
        if p["resultat"]:
            total += -math.log(proba)
        else:
            total += -math.log(1 - proba)
    return total / len(paris)


def ece(historique, n_bins=10):
    """
    Expected Calibration Error.
    Divise [0, 1] en n_bins, compare proba moyenne vs fréquence réelle.
    - 0.00 = parfait
    - < 0.05 = bon
    - > 0.10 = mauvais
    """
    paris = _paris_resolus(historique)
    if not paris:
        return None

    bins = [[] for _ in range(n_bins)]
    for p in paris:
        proba = max(0.0, min(0.999, p["p_calibree"]))
        idx = min(int(proba * n_bins), n_bins - 1)
        bins[idx].append(p)

    total_n = len(paris)
    ece_val = 0.0
    for bin_paris in bins:
        if not bin_paris:
            continue
        n = len(bin_paris)
        proba_moy = sum(p["p_calibree"] for p in bin_paris) / n
        freq_obs = sum(1 for p in bin_paris if p["resultat"]) / n
        ece_val += (n / total_n) * abs(freq_obs - proba_moy)
    return ece_val


def interpreter_brier(bs):
    if bs is None:
        return "—"
    if bs < 0.15:
        return "🟢 Excellent"
    if bs < 0.20:
        return "🟢 Bon"
    if bs < 0.25:
        return "🟡 Moyen"
    return "🔴 Mauvais"


def interpreter_log_loss(ll):
    if ll is None:
        return "—"
    if ll < 0.50:
        return "🟢 Excellent"
    if ll < 0.65:
        return "🟢 Bon"
    if ll < 0.80:
        return "🟡 Moyen"
    return "🔴 Mauvais"


def interpreter_ece(e):
    if e is None:
        return "—"
    if e < 0.03:
        return "🟢 Excellent"
    if e < 0.05:
        return "🟢 Bon"
    if e < 0.10:
        return "🟡 Moyen"
    return "🔴 Mauvais"


def calculer_toutes(historique):
    """Retourne un dict avec toutes les métriques + interprétations."""
    paris = _paris_resolus(historique)
    bs = brier_score(historique)
    ll = log_loss(historique)
    ec = ece(historique)
    return {
        "n": len(paris),
        "brier": bs,
        "log_loss": ll,
        "ece": ec,
        "brier_txt": interpreter_brier(bs),
        "log_loss_txt": interpreter_log_loss(ll),
        "ece_txt": interpreter_ece(ec),
    }


def hist_bins(historique, n_bins=10):
    """
    Retourne les bins pour affichage :
    [{bin, proba_moy, freq_obs, n}, ...]
    """
    paris = _paris_resolus(historique)
    if not paris:
        return []

    bins = [[] for _ in range(n_bins)]
    for p in paris:
        proba = max(0.0, min(0.999, p["p_calibree"]))
        idx = min(int(proba * n_bins), n_bins - 1)
        bins[idx].append(p)

    resultat = []
    for i, bin_paris in enumerate(bins):
        if not bin_paris:
            continue
        n = len(bin_paris)
        proba_moy = sum(p["p_calibree"] for p in bin_paris) / n
        freq_obs = sum(1 for p in bin_paris if p["resultat"]) / n
        resultat.append({
            "bin": f"{i * 10}-{(i + 1) * 10}%",
            "proba_moy": proba_moy,
            "freq_obs": freq_obs,
            "ecart": freq_obs - proba_moy,
            "n": n,
        })
    return resultat
