"""
coherence.py — Couche de cohérence mathématique.
Détecte et corrige les aberrations de probabilités AVANT qu'elles
ne polluent le Master Score et les EV.

Contrôles :
1. Complémentarité (O0.5 + U0.5 ≈ 1)
2. Bornes (probas dans [0.01, 0.99])
3. Saturation sigmoïde (z extrêmes)
4. Cohérence logique entre marchés liés
"""

import json
from pathlib import Path


LOG_FILE = Path("coherence_log.json")

# --- Bornes ---
P_MIN = 0.01
P_MAX = 0.99
Z_MAX = 2.5          # au-delà, sigmoïde sature
TOLERANCE = 0.03     # tolérance sur la complémentarité

# --- Paires complémentaires ---
PAIRES_COMPLEMENTAIRES = [
    ("O0.5", "U0.5"),
    ("O1.5", "U1.5"),
    ("O2.5", "U2.5"),
    ("O3.5", "U3.5"),
    ("AH-0.5", "AH+0.5"),
    ("AH-1.5", "AH+1.5"),
    ("AH-2.5", "AH+2.5"),
]

# --- Relations d'ordre attendues ---
# (a, b) → P(a) doit être ≤ P(b)
RELATIONS_ORDRE = [
    ("AH-2.5", "AH-1.5"),
    ("AH-1.5", "AH-0.5"),
    ("AH+0.5", "AH+1.5"),
    ("AH+1.5", "AH+2.5"),
    ("O2.5", "O1.5"),
    ("O1.5", "O0.5"),
    ("O3.5", "O2.5"),
    ("U0.5", "U1.5"),
    ("U1.5", "U2.5"),
    ("U2.5", "U3.5"),
    ("1", "1X"),   # si présent
    ("2", "X2"),
]


# ---------- Log ----------

def _charger_log():
    if not LOG_FILE.exists():
        return {"anomalies": []}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"anomalies": []}


def _sauver_log(data):
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError:
        pass


def _log_anomalie(type_anomalie, details):
    data = _charger_log()
    data["anomalies"].append({"type": type_anomalie, "details": details})
    # On garde les 200 dernières anomalies
    data["anomalies"] = data["anomalies"][-200:]
    _sauver_log(data)


# ---------- Contrôle 1 : bornes ----------

def clip_bornes(resultats):
    """Force toutes les probas dans [P_MIN, P_MAX]."""
    corriges = 0
    for r in resultats:
        if "p_calibree" not in r:
            continue
        p = r["p_calibree"]
        if p < P_MIN:
            r["p_calibree"] = P_MIN
            corriges += 1
        elif p > P_MAX:
            r["p_calibree"] = P_MAX
            corriges += 1
    if corriges > 0:
        _log_anomalie("bornes", {"nb_corriges": corriges})
    return resultats


# ---------- Contrôle 2 : complémentarité ----------

def corriger_complementarite(resultats):
    """
    Si P(A) + P(B) ≠ 1 pour A,B complémentaires :
    → on recalibre proportionnellement pour que la somme = 1.
    """
    index = {r.get("market"): r for r in resultats if "market" in r}
    corrections = 0

    for a, b in PAIRES_COMPLEMENTAIRES:
        if a not in index or b not in index:
            continue
        pa = index[a].get("p_calibree")
        pb = index[b].get("p_calibree")
        if pa is None or pb is None:
            continue

        total = pa + pb
        if total <= 0:
            continue

        if abs(total - 1.0) > TOLERANCE:
            pa_new = pa / total
            pb_new = pb / total
            index[a]["p_calibree"] = pa_new
            index[b]["p_calibree"] = pb_new
            index[a]["p_calibree_corrigee"] = True
            index[b]["p_calibree_corrigee"] = True
            corrections += 1
            _log_anomalie("complementarite", {
                "paire": (a, b),
                "avant": [pa, pb],
                "apres": [pa_new, pb_new],
            })

    return resultats


# ---------- Contrôle 3 : saturation sigmoïde ----------

def detecter_saturation(resultats):
    """
    Détecte les probas extrêmes (> 0.95 ou < 0.05) → signe de saturation.
    On atténue vers 0.5 proportionnellement.
    """
    attenues = 0
    for r in resultats:
        p = r.get("p_calibree")
        if p is None:
            continue
        if p > 0.95:
            # Atténuer de 20% vers 0.5
            r["p_calibree"] = p - 0.20 * (p - 0.5)
            attenues += 1
        elif p < 0.05:
            r["p_calibree"] = p + 0.20 * (0.5 - p)
            attenues += 1

    if attenues > 0:
        _log_anomalie("saturation", {"nb_attenues": attenues})
    return resultats


# ---------- Contrôle 4 : relations d'ordre ----------

def corriger_relations_ordre(resultats):
    """
    Ex: P(AH-2.5) doit être ≤ P(AH-1.5) ≤ P(AH-0.5).
    Si violé → on ramène A à la valeur de B (le plus prudent).
    """
    index = {r.get("market"): r for r in resultats if "market" in r}
    corrections = 0

    for a, b in RELATIONS_ORDRE:
        if a not in index or b not in index:
            continue
        pa = index[a].get("p_calibree")
        pb = index[b].get("p_calibree")
        if pa is None or pb is None:
            continue

        if pa > pb:
            # Incohérence : on ramène A à la valeur de B
            index[a]["p_calibree"] = pb
            index[a]["p_calibree_corrigee"] = True
            corrections += 1
            _log_anomalie("ordre", {
                "relation": f"P({a}) ≤ P({b})",
                "avant": [pa, pb],
                "apres": [pb, pb],
            })

    return resultats


# ---------- Contrôle 5 : cohérence 1X2 ----------

def corriger_1x2(resultats):
    """
    P(1) + P(X) + P(2) doit = 1.
    """
    index = {r.get("market"): r for r in resultats if "market" in r}
    if not all(k in index for k in ["1", "X", "2"]):
        return resultats

    p1 = index["1"].get("p_calibree", 0)
    px = index["X"].get("p_calibree", 0)
    p2 = index["2"].get("p_calibree", 0)
    total = p1 + px + p2

    if total <= 0:
        return resultats

    if abs(total - 1.0) > TOLERANCE:
        index["1"]["p_calibree"] = p1 / total
        index["X"]["p_calibree"] = px / total
        index["2"]["p_calibree"] = p2 / total
        for k in ["1", "X", "2"]:
            index[k]["p_calibree_corrigee"] = True
        _log_anomalie("1x2", {
            "avant": [p1, px, p2],
            "apres": [p1 / total, px / total, p2 / total],
        })

    return resultats


# ---------- Pipeline complet ----------

def appliquer_coherence(resultats):
    """
    Applique tous les contrôles dans l'ordre optimal.
    Retourne les résultats corrigés.
    """
    if not resultats:
        return resultats

    resultats = clip_bornes(resultats)
    resultats = corriger_complementarite(resultats)
    resultats = corriger_1x2(resultats)
    resultats = corriger_relations_ordre(resultats)
    resultats = detecter_saturation(resultats)
    resultats = clip_bornes(resultats)  # re-clip après corrections

    return resultats


# ---------- Statistiques ----------

def stats_anomalies():
    data = _charger_log()
    compteur = {}
    for a in data["anomalies"]:
        t = a.get("type", "?")
        compteur[t] = compteur.get(t, 0) + 1
    return compteur


def dernieres_anomalies(n=20):
    data = _charger_log()
    return data["anomalies"][-n:]


def reinitialiser():
    _sauver_log({"anomalies": []})


# ---------- Test local ----------

if __name__ == "__main__":
    # Cas volontairement faux
    test = [
        {"market": "1", "p_calibree": 0.60},
        {"market": "X", "p_calibree": 0.30},
        {"market": "2", "p_calibree": 0.25},
        {"market": "O0.5", "p_calibree": 0.88},
        {"market": "U0.5", "p_calibree": 0.65},
        {"market": "O2.5", "p_calibree": 0.88},
        {"market": "U2.5", "p_calibree": 0.65},
        {"market": "AH-0.5", "p_calibree": 0.93},
        {"market": "AH+0.5", "p_calibree": 0.87},
        {"market": "AH-1.5", "p_calibree": 0.93},
        {"market": "AH+1.5", "p_calibree": 0.77},
    ]

    print("=== AVANT ===\n")
    for r in test:
        print(f"  {r['market']:8s} → {r['p_calibree']:.1%}")

    test = appliquer_coherence(test)

    print("\n=== APRÈS ===\n")
    for r in test:
        flag = " ✏️" if r.get("p_calibree_corrigee") else ""
        print(f"  {r['market']:8s} → {r['p_calibree']:.1%}{flag}")

    print("\n=== ANOMALIES ===\n")
    for t, n in stats_anomalies().items():
        print(f"  {t} : {n}")
