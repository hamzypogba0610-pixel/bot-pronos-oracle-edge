"""
odds_check.py — Contrôle de plausibilité des cotes.
Détecte les cotes aberrantes qui faussent les EV.
"""

BORNES = {
    "1":      (1.30, 15.00),
    "X":      (2.50, 8.00),
    "2":      (1.30, 15.00),
    "O0.5":   (1.02, 1.25),
    "U0.5":   (5.00, 30.00),
    "O1.5":   (1.15, 1.55),
    "U1.5":   (2.50, 8.00),
    "O2.5":   (1.45, 2.30),
    "U2.5":   (1.45, 2.30),
    "O3.5":   (2.30, 7.00),
    "U3.5":   (1.10, 1.55),
    "AH-0.5": (1.30, 4.50),
    "AH+0.5": (1.30, 4.50),
    "AH-1.5": (1.80, 8.00),
    "AH+1.5": (1.10, 3.00),
    "AH-2.5": (2.50, 20.00),
    "AH+2.5": (1.02, 1.60),
    "BTTS":   (1.40, 2.50),
}


def verifier_cote(market, cote):
    if market not in BORNES:
        return True, ""
    if not cote or cote <= 1.01:
        return True, ""
    mini, maxi = BORNES[market]
    if cote < mini:
        return False, f"Cote {cote:.2f} trop basse (min plausible ≈ {mini})"
    if cote > maxi:
        return False, f"Cote {cote:.2f} trop haute (max plausible ≈ {maxi})"
    return True, ""


def verifier_toutes(cotes_map):
    warnings = []
    for market, cote in cotes_map.items():
        ok, msg = verifier_cote(market, cote)
        if not ok:
            warnings.append({"market": market, "cote": cote, "message": msg})
    return warnings


def stats_bornes():
    return [{"Marché": k, "Min": v[0], "Max": v[1]}
            for k, v in sorted(BORNES.items())]
