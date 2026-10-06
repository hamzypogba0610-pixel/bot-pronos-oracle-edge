"""
elo.py — Couche 3 : ELO-FORCE.
Rating Elo dynamique par équipe, ajusté pour le football.

Formule standard Elo adaptée :
- Avantage domicile : +65 points au rating dom
- Facteur K ajusté par écart de buts
- Mise à jour à chaque match enregistré
"""

import json
import math
from pathlib import Path


ELO_FILE = Path("elo_data.json")

# --- Paramètres ---
RATING_INITIAL = 1500
K_BASE = 25           # facteur K de base (football : 20-30)
HOME_ADVANTAGE = 65   # avantage domicile en points Elo


# ---------- Persistance ----------

def charger():
    if not ELO_FILE.exists():
        return {"ratings": {}, "historique": []}
    try:
        with open(ELO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"ratings": {}, "historique": []}


def sauver(data):
    try:
        with open(ELO_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde elo : {e}")


# ---------- API principale ----------

def get_rating(team):
    """Retourne le rating d'une équipe (1500 si inconnue)."""
    data = charger()
    return data["ratings"].get(team, RATING_INITIAL)


def set_rating(team, rating):
    data = charger()
    data["ratings"][team] = float(rating)
    sauver(data)


def expected_score(rating_team, rating_opp):
    """
    Score attendu ∈ [0, 1] selon la formule Elo standard.
    E = 1 / (1 + 10^((R_opp - R_team)/400))
    """
    exposant = (rating_opp - rating_team) / 400.0
    try:
        return 1.0 / (1.0 + 10 ** exposant)
    except OverflowError:
        return 0.0 if exposant > 0 else 1.0


def facteur_k(ecart_buts):
    """
    K ajusté par l'écart de buts.
    Une victoire 5-0 donne plus de K qu'un 1-0.
    K = K_base × (1 + ln(1 + |écart|))
    """
    ecart = abs(ecart_buts)
    return K_BASE * (1.0 + math.log(1.0 + ecart))


def resultat_reel(buts_pour, buts_contre):
    """1 = victoire, 0.5 = nul, 0 = défaite."""
    if buts_pour > buts_contre:
        return 1.0
    if buts_pour == buts_contre:
        return 0.5
    return 0.0


def maj_apres_match(home_team, away_team, buts_home, buts_away):
    """
    Met à jour les ratings des deux équipes après un match.
    Retourne un dict avec les changements.
    """
    data = charger()

    r_home = data["ratings"].get(home_team, RATING_INITIAL)
    r_away = data["ratings"].get(away_team, RATING_INITIAL)

    # Score attendu (avec avantage domicile appliqué au rating dom)
    e_home = expected_score(r_home + HOME_ADVANTAGE, r_away)
    e_away = 1.0 - e_home

    # Résultat réel
    s_home = resultat_reel(buts_home, buts_away)
    s_away = 1.0 - s_home

    # Facteur K ajusté
    ecart = buts_home - buts_away
    k = facteur_k(ecart)

    # Nouveaux ratings
    r_home_new = r_home + k * (s_home - e_home)
    r_away_new = r_away + k * (s_away - e_away)

    data["ratings"][home_team] = round(r_home_new, 2)
    data["ratings"][away_team] = round(r_away_new, 2)

    # Historique
    data["historique"].append({
        "home": home_team, "away": away_team,
        "buts_home": buts_home, "buts_away": buts_away,
        "r_home_avant": round(r_home, 2),
        "r_away_avant": round(r_away, 2),
        "r_home_apres": round(r_home_new, 2),
        "r_away_apres": round(r_away_new, 2),
        "delta_home": round(r_home_new - r_home, 2),
        "delta_away": round(r_away_new - r_away, 2),
        "k": round(k, 2),
    })

    sauver(data)

    return {
        "r_home_avant": r_home,
        "r_away_avant": r_away,
        "r_home_apres": r_home_new,
        "r_away_apres": r_away_new,
        "delta_home": r_home_new - r_home,
        "delta_away": r_away_new - r_away,
        "k": k,
    }


# ---------- Lecture rapide ----------

def ecart_elo(home_team, away_team):
    """Retourne l'écart Elo (avec avantage domicile) : rating_dom − rating_ext."""
    r_home = get_rating(home_team) + HOME_ADVANTAGE
    r_away = get_rating(away_team)
    return r_home - r_away


def proba_elo(home_team, away_team):
    """
    Probabilité implicite (Elo pur) que le domicile ne perde pas.
    Utile pour comparer avec notre modèle.
    """
    ecart = ecart_elo(home_team, away_team)
    e_home = expected_score(get_rating(home_team) + HOME_ADVANTAGE,
                             get_rating(away_team))
    # On redistribue : E_home + 0.5 × P(nul estimé)
    # Approximation : P(nul) ≈ 0.28 − 0.001 × |écart|
    p_nul_estime = max(0.15, 0.28 - 0.001 * abs(ecart))
    p_home = max(0.0, e_home - p_nul_estime / 2)
    p_away = max(0.0, 1.0 - e_home - p_nul_estime / 2)
    return {
        "p_home": p_home,
        "p_draw": p_nul_estime,
        "p_away": p_away,
    }


def stats_elo():
    """Classement des équipes par rating."""
    data = charger()
    equipes = [{"equipe": k, "rating": v} for k, v in data["ratings"].items()]
    return sorted(equipes, key=lambda x: -x["rating"])


def reinitialiser():
    sauver({"ratings": {}, "historique": []})


# ---------- Test local ----------

if __name__ == "__main__":
    reinitialiser()

    # Simuler 3 matchs
    print("=== Simulation ELO ===\n")
    matchs = [
        ("Arsenal", "Liverpool", 2, 1),
        ("Man City", "Arsenal", 3, 0),
        ("Liverpool", "Man City", 1, 1),
    ]
    for h, a, bh, ba in matchs:
        res = maj_apres_match(h, a, bh, ba)
        print(f"{h} {bh}-{ba} {a}")
        print(f"  {h}: {res['r_home_avant']:.0f} → {res['r_home_apres']:.0f} "
              f"({res['delta_home']:+.1f})")
        print(f"  {a}: {res['r_away_avant']:.0f} → {res['r_away_apres']:.0f} "
              f"({res['delta_away']:+.1f})\n")

    print("=== Classement ===")
    for e in stats_elo():
        print(f"  {e['equipe']}: {e['rating']:.0f}")

    print(f"\nÉcart Elo Arsenal vs Liverpool : "
          f"{ecart_elo('Arsenal', 'Liverpool'):+.0f}")
    probas = proba_elo("Arsenal", "Liverpool")
    print(f"Probas Elo : Dom {probas['p_home']:.1%} · "
          f"Nul {probas['p_draw']:.1%} · Ext {probas['p_away']:.1%}")
