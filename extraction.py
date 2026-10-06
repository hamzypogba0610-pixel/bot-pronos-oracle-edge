"""
extraction.py — Extraction propre des données du formulaire.
Transforme les saisies utilisateur en dict exploitable par variables.py.

CONVENTION SCORE : tous les scores sont au format
[buts équipe analysée] - [buts adversaire]
"""

from datetime import datetime


# ---------- Parsing ----------

def parser_score(score_str):
    """'2-1' → (2, 1). Retourne None si invalide."""
    if not score_str or "-" not in score_str:
        return None
    parts = score_str.strip().split("-")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return None


def resultat_pour_equipe(buts_pour, buts_contre):
    """3 = victoire, 1 = nul, 0 = défaite."""
    if buts_pour > buts_contre:
        return 3
    if buts_pour == buts_contre:
        return 1
    return 0


# ---------- Extraction de la forme ----------

def extraire_form(form_data):
    """
    Prend une liste de 5 dicts {'score', 'xg', 'xga', 'tirs_cadres', 'date'}.
    Retourne un dict complet avec toutes les stats extraites.
    """
    points = []
    buts_pour = []
    buts_contre = []
    xgs = []
    xgas = []
    tirs_cadres = []
    dates_valides = []

    for m in form_data:
        parsed = parser_score(m.get("score", ""))
        if parsed:
            bp, bc = parsed
            buts_pour.append(bp)
            buts_contre.append(bc)
            points.append(resultat_pour_equipe(bp, bc))

        xgs.append(float(m.get("xg", 0.0) or 0.0))
        xgas.append(float(m.get("xga", 0.0) or 0.0))
        tirs_cadres.append(int(m.get("tirs_cadres", 0) or 0))

        d = m.get("date", "").strip() if m.get("date") else ""
        if d:
            dates_valides.append(d)

    def moy(lst):
        return sum(lst) / len(lst) if lst else 0.0

    def variance(lst):
        if len(lst) < 2:
            return 0.0
        m = moy(lst)
        return sum((x - m) ** 2 for x in lst) / len(lst)

    return {
        "points": points if points else [1, 1, 1, 1, 1],
        "n_matchs_valides": len(points),
        "buts_pour_moy": moy(buts_pour),
        "buts_contre_moy": moy(buts_contre),
        "variance_buts": variance(buts_pour + buts_contre),
        "xg_moy": moy(xgs),
        "xga_moy": moy(xgas),
        "tirs_cadres_moy": moy(tirs_cadres),
        "dates_valides": dates_valides,
    }


# ---------- Métriques de qualité ----------

def calculer_volume(n_matchs_valides, cible=5):
    """0-1 : proportion de matchs réellement saisis."""
    return min(1.0, n_matchs_valides / cible)


def calculer_fraicheur(dates_str, today=None):
    """0-1 : 0 = récent, 1 = très vieux (> 60 jours)."""
    if not dates_str:
        return 0.5

    today = today or datetime.now()
    formats = ["%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%y"]
    ages = []

    for d in dates_str:
        for fmt in formats:
            try:
                dt = datetime.strptime(d.strip(), fmt)
                ages.append((today - dt).days)
                break
            except (ValueError, AttributeError):
                continue

    if not ages:
        return 0.5

    age_moy = sum(ages) / len(ages)
    return min(1.0, max(0.0, age_moy / 60.0))


def calculer_completude(form_data):
    """0-1 : proportion de champs stats remplis (xG, xGA, tirs cadrés)."""
    if not form_data:
        return 0.0
    total = 0
    remplis = 0
    for m in form_data:
        total += 3
        if float(m.get("xg", 0) or 0) > 0:
            remplis += 1
        if float(m.get("xga", 0) or 0) > 0:
            remplis += 1
        if int(m.get("tirs_cadres", 0) or 0) > 0:
            remplis += 1
    return remplis / total if total > 0 else 0.0


def calculer_qualite_adversaires(form_data):
    """Pour l'instant : neutre (0.5). Sera amélioré avec classement réel."""
    return [0.5] * len(form_data)


# ---------- H2H ----------

def extraire_h2h(h2h_data):
    """
    Transforme les 5 H2H en (resultats, ages).
    Convention : bp = score équipe home du match, bc = score équipe away.
    """
    resultats = []
    for m in h2h_data:
        parsed = parser_score(m.get("score", ""))
        if parsed:
            bp, bc = parsed
            if bp > bc:
                resultats.append(1.0)
            elif bp < bc:
                resultats.append(0.0)
            else:
                resultats.append(0.5)

    if not resultats:
        return [0.5] * 5, [100, 200, 300, 400, 500]

    # Compléter jusqu'à 5
    resultats = (resultats + [0.5] * 5)[:5]
    ages = [100, 200, 300, 400, 500]  # à affiner quand on aura les vraies dates
    return resultats, ages


# ---------- Construction du dict final ----------

def construire_donnees(form_data, form_adv_data, absences,
                       motivation, cote_home, h2h_data=None):
    """
    Construit le dict attendu par variables.calculer_variables().
    """
    extrait = extraire_form(form_data)
    extrait_adv = extraire_form(form_adv_data)
    h2h_res, h2h_ages = extraire_h2h(h2h_data or [])

    return {
        # Équipe analysée
        "form_resultats": extrait["points"],
        "form_qualite": calculer_qualite_adversaires(form_data),
        "buts": extrait["buts_pour_moy"],
        "xg": extrait["xg_moy"],
        "tirs_cadres": extrait["tirs_cadres_moy"],
        "buts_encaisses": extrait["buts_contre_moy"],
        "xga": extrait["xga_moy"],
        # Adversaire
        "tirs_cadres_conc": extrait_adv["tirs_cadres_moy"] or 4.0,
        "xga_adversaire": extrait_adv["xga_moy"],
        # Contexte
        "perf_dom": 0.6,
        "perf_ext": 0.5,
        "variance_buts": extrait["variance_buts"],
        "impacts_absences": [absences],
        "h2h_resultats": h2h_res,
        "h2h_ages": h2h_ages,
        "motivation": motivation,
        # Placeholders (à enrichir plus tard)
        "arrets": 5, "buts_evites": 0, "erreurs_gk": 0,
        "danger_off": 0.5, "solidite_def": 0.5,
        "pressing": 0.5, "possession": 0.5,
        "compacite": 0.5, "rythme": 0.5,
        "style_adv": {"pressing": 0.5, "possession": 0.5,
                      "compacite": 0.5, "rythme": 0.5},
        "proba_marche": 1 / cote_home if cote_home > 0 else 0.5,
        # Métadonnées qualité (utilisées pour Q)
        "_volume": calculer_volume(extrait["n_matchs_valides"]),
        "_fraicheur": calculer_fraicheur(extrait["dates_valides"]),
        "_completude": calculer_completude(form_data),
                   }
