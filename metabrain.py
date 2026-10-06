"""
metabrain.py — Couche 2 : Meta-Brain.
Auto-évaluation contextuelle : le bot apprend OÙ il est fort/faible.

Contexte = market | regime | ligue
"""
import json
import math
from pathlib import Path


METABRAIN_FILE = Path("metabrain_data.json")

# --- Paramètres ---
ALPHA = 0.20     # influence max du MetaScore (±20%)
MIN_N = 5        # nombre min de paris pour activer le MetaScore
N_REF = 30       # nombre de paris pour avoir la confiance max


# ---------- Persistance ----------

def charger():
    if not METABRAIN_FILE.exists():
        return {"contextes": {}}
    try:
        with open(METABRAIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"contextes": {}}


def sauver(data):
    try:
        with open(METABRAIN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde metabrain : {e}")


def _cle(market, regime, ligue):
    return f"{market}|{regime}|{ligue}"


# ---------- Enregistrement ----------

def enregistrer_contexte(market, regime, ligue, gagne):
    """Enregistre le résultat d'un pari dans son contexte."""
    data = charger()
    cle = _cle(market, regime, ligue)
    if cle not in data["contextes"]:
        data["contextes"][cle] = {"n": 0, "gagnes": 0}
    data["contextes"][cle]["n"] += 1
    if gagne:
        data["contextes"][cle]["gagnes"] += 1
    sauver(data)
    return True


# ---------- Calcul du MetaScore ----------

def calculer_metascore(market, regime, ligue):
    """
    Retourne le MetaScore ∈ [-1, +1] pour ce contexte.
    0 si données insuffisantes.
    """
    data = charger()
    cle = _cle(market, regime, ligue)
    ctx = data["contextes"].get(cle)

    if not ctx or ctx["n"] < MIN_N:
        return {
            "score": 0.0,
            "n": ctx["n"] if ctx else 0,
            "taux": None,
            "facteur": 1.0,
            "verdict": "⚪ NEUTRE (données insuffisantes)",
        }

    n = ctx["n"]
    taux = ctx["gagnes"] / n

    # Score brut : taux 0 → -1, 0.5 → 0, 1 → +1
    score_brut = 2.0 * taux - 1.0

    # Pondération par la confiance (nombre de paris)
    confiance = min(1.0, math.sqrt(n) / math.sqrt(N_REF))
    score = score_brut * confiance

    facteur = 1.0 + ALPHA * score

    if score >= 0.50:
        verdict = "🟢 POINT FORT"
    elif score >= 0.15:
        verdict = "🟢 LÉGÈREMENT FAVORABLE"
    elif score >= -0.15:
        verdict = "⚪ NEUTRE"
    elif score >= -0.50:
        verdict = "🟡 LÉGÈREMENT DÉFAVORABLE"
    else:
        verdict = "🔴 POINT FAIBLE"

    return {
        "score": score,
        "n": n,
        "taux": taux,
        "facteur": facteur,
        "verdict": verdict,
    }


# ---------- Statistiques ----------

def stats_contexte():
    """Retourne le tableau complet des contextes enregistrés."""
    data = charger()
    resultats = []
    for cle, ctx in data["contextes"].items():
        try:
            market, regime, ligue = cle.split("|", 2)
        except ValueError:
            continue
        n = ctx["n"]
        taux = ctx["gagnes"] / n if n > 0 else 0
        resultats.append({
            "market": market,
            "regime": regime,
            "ligue": ligue,
            "n": n,
            "gagnes": ctx["gagnes"],
            "taux": taux,
        })
    return sorted(resultats, key=lambda x: -x["n"])


def paris_en_attente_metabrain():
    """Pour usage futur : contextes avec peu d'observations."""
    data = charger()
    return [c for c in data["contextes"].values() if c["n"] < MIN_N]


def reinitialiser():
    sauver({"contextes": {}})


# ---------- Test local ----------

if __name__ == "__main__":
    reinitialiser()
    # Simuler 35 paris sur "1" en régime B en Premier League
    for i in range(35):
        enregistrer_contexte("1", "B", "Premier League", gagne=(i % 3 != 0))

    # Simuler 8 paris sur "AH-2.5" en régime E en Ligue 1 (mauvais)
    for i in range(8):
        enregistrer_contexte("AH-2.5", "E", "Ligue 1", gagne=(i < 2))

    print("=== MetaScores ===\n")
    for market, regime, ligue in [
        ("1", "B", "Premier League"),
        ("AH-2.5", "E", "Ligue 1"),
        ("X", "A", "Serie A"),  # contexte jamais vu
    ]:
        res = calculer_metascore(market, regime, ligue)
        taux_str = f"{res['taux']:.1%}" if res["taux"] is not None else "—"
        print(f"[{market} | {regime} | {ligue}]")
        print(f"   n={res['n']} · taux={taux_str} · "
              f"score={res['score']:+.2f} · facteur={res['facteur']:.2f} "
              f"· {res['verdict']}\n")
