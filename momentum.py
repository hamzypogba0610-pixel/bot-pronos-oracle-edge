"""
momentum.py — Couche 1 : Momentum Tracker (CLV Engine).
Détecte le mouvement du marché entre ouverture et fermeture.
"""

import math


def calculer_clv(cote_ouverture, cote_fermeture):
    """
    CLV = (Cote_ouverture / Cote_fermeture) - 1
    Positif → le marché s'est resserré vers nous (bon signe)
    Négatif → le marché s'est éloigné (warning)
    """
    if not cote_ouverture or not cote_fermeture:
        return 0.0
    if cote_ouverture <= 1.01 or cote_fermeture <= 1.01:
        return 0.0
    return (cote_ouverture / cote_fermeture) - 1.0


def classer_clv(clv):
    """Retourne un verdict lisible."""
    if clv >= 0.05:
        return "🟢 CLV+ FORT"
    if clv >= 0.02:
        return "🟢 CLV+ LÉGER"
    if clv >= -0.02:
        return "⚪ NEUTRE"
    if clv >= -0.05:
        return "🟡 CLV− LÉGER"
    return "🔴 CLV− FORT"


def facteur_clv(clv):
    """
    V_F_CLV = 1 + tanh(k × CLV)
    Borné entre 0 et 2. k = 5 pour être réactif.
    """
    try:
        return 1.0 + math.tanh(5.0 * clv)
    except OverflowError:
        return 2.0 if clv > 0 else 0.0


def detecter_piege(clv, ev):
    """
    Signaux de piège :
    - EV fort positif mais CLV très négatif → le marché nous dit qu'on se trompe
    - Signal classique d'info cachée (blessure, compo, météo)
    """
    if ev > 0.08 and clv < -0.05:
        return True, "⚠️ PIÈGE : value positive mais marché très défavorable"
    if ev > 0.15 and clv < -0.02:
        return True, "⚠️ PIÈGE : forte value mais marché qui s'éloigne"
    return False, ""


def analyse_momentum(cote_ouverture, cote_fermeture, ev):
    """
    Pipeline complet Momentum.
    Retourne un dict avec CLV, verdict, facteur multiplicateur et alerte piège.
    """
    clv = calculer_clv(cote_ouverture, cote_fermeture)
    verdict = classer_clv(clv)
    facteur = facteur_clv(clv)
    piege, raison = detecter_piege(clv, ev)

    return {
        "clv": clv,
        "verdict": verdict,
        "facteur": facteur,
        "piege": piege,
        "raison_piege": raison,
        "cote_ouverture": cote_ouverture,
        "cote_fermeture": cote_fermeture,
    }


# --- Test local ---
if __name__ == "__main__":
    exemples = [
        (2.10, 1.95, 0.10),
        (2.10, 2.30, 0.10),
        (2.10, 2.10, 0.10),
        (3.00, 2.60, 0.20),
        (2.50, 3.20, 0.15),
    ]
    for ou, fe, ev in exemples:
        res = analyse_momentum(ou, fe, ev)
        print(f"Ouv={ou:.2f} Ferm={fe:.2f} → "
              f"CLV={res['clv']:+.1%} ({res['verdict']}) "
              f"Facteur={res['facteur']:.2f}"
              + (f"  {res['raison_piege']}" if res['piege'] else ""))
