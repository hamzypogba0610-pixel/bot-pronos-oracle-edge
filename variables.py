"""
variables.py — Calcul des 14 variables normalisées (0-1).
0.5 = neutre. Chaque fonction prend des stats brutes et renvoie [0, 1].
"""

import math


# ---------- Helpers ----------

def normaliser(valeur, min_val, max_val):
    if max_val == min_val:
        return 0.5
    v = (valeur - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, v))


def sigmoide(x, k=1.0):
    try:
        return 1.0 / (1.0 + math.exp(-k * x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def moyenne(liste):
    return sum(liste) / len(liste) if liste else 0.0


def ecart_type(liste):
    if len(liste) < 2:
        return 0.0
    m = moyenne(liste)
    variance = sum((x - m) ** 2 for x in liste) / len(liste)
    return math.sqrt(variance)


# ---------- Les 14 variables ----------

def calc_form(resultats, qualite_adversaires):
    points = sum(resultats)
    r = points / 15.0
    q = moyenne(qualite_adversaires)
    return 0.7 * r + 0.3 * q


def calc_att(buts, xg, tirs_cadres):
    g = normaliser(buts, 0, 3)
    x = normaliser(xg, 0, 3)
    s = normaliser(tirs_cadres, 0, 8)
    return 0.35 * g + 0.35 * x + 0.30 * s


def calc_def(buts_encaisses, xga, tirs_cadres_conc):
    ga = normaliser(buts_encaisses, 0, 3)
    xga_n = normaliser(xga, 0, 3)
    sc = normaliser(tirs_cadres_conc, 0, 8)
    return 1.0 - (0.40 * ga + 0.40 * xga_n + 0.20 * sc)


def calc_xg(xg_equipe, xga_adversaire, k=1.5):
    return sigmoide(k * (xg_equipe - xga_adversaire))


def calc_home(perf_dom, perf_ext, k=2.0):
    return sigmoide(k * (perf_dom - perf_ext))


def calc_goals(buts_marques, buts_encaisses, variance):
    gf = normaliser(buts_marques, 0, 3)
    ga = normaliser(buts_encaisses, 0, 3)
    var_pen = normaliser(variance, 0, 4)
    return 0.5 * gf + 0.3 * (1 - ga) + 0.2 * (1 - var_pen)


def calc_abs(impacts, impact_max=10.0):
    total = sum(impacts)
    return max(0.0, 1.0 - total / impact_max)


def calc_h2h(resultats, ages_jours, lambda_decay=0.01):
    if not resultats:
        return 0.5
    total_w = 0.0
    total = 0.0
    for r, t in zip(resultats, ages_jours):
        w = math.exp(-lambda_decay * t)
        total += w * r
        total_w += w
    return total / total_w if total_w > 0 else 0.5


def calc_mot(score_contextuel):
    return max(0.0, min(1.0, score_contextuel))


def calc_gk(arrets, buts_evites, erreurs):
    a = normaliser(arrets, 0, 10)
    be = normaliser(buts_evites, -5, 5)
    er = normaliser(erreurs, 0, 3)
    return 0.5 * a + 0.4 * be + 0.1 * (1 - er)


def calc_set(danger_off, solidite_def):
    return 0.5 * danger_off + 0.5 * solidite_def


def calc_style(pressing, possession, compacite, rythme, style_adv):
    mes_axes = [pressing, possession, compacite, rythme]
    adv_axes = [style_adv["pressing"], style_adv["possession"],
                style_adv["compacite"], style_adv["rythme"]]
    ecarts = [abs(a - b) for a, b in zip(mes_axes, adv_axes)]
    return moyenne(ecarts)


def calc_market(proba_implicite_nette):
    return max(0.0, min(1.0, proba_implicite_nette))


def calc_elo(ecart_elo, k=1.0):
    """
    ELO normalisé ∈ [0, 1].
    - ecart_elo = 0    → 0.50 (match équilibré)
    - ecart_elo = +200 → ~0.73 (domicile favori)
    - ecart_elo = −200 → ~0.27 (extérieur favori)
    """
    return sigmoide(ecart_elo / 200.0, k=k)


# ---------- Calcul complet ----------

def calculer_variables(donnees):
    """
    Prend un dict de données brutes, retourne les 14 variables.
    """
    return {
        "FORM":   calc_form(donnees["form_resultats"], donnees["form_qualite"]),
        "ATT":    calc_att(donnees["buts"], donnees["xg"], donnees["tirs_cadres"]),
        "DEF":    calc_def(donnees["buts_encaisses"], donnees["xga"],
                            donnees["tirs_cadres_conc"]),
        "XG":     calc_xg(donnees["xg"], donnees["xga_adversaire"]),
        "HOME":   calc_home(donnees["perf_dom"], donnees["perf_ext"]),
        "GOALS":  calc_goals(donnees["buts"], donnees["buts_encaisses"],
                              donnees["variance_buts"]),
        "ABS":    calc_abs(donnees["impacts_absences"]),
        "H2H":    calc_h2h(donnees["h2h_resultats"], donnees["h2h_ages"]),
        "MOT":    calc_mot(donnees["motivation"]),
        "GK":     calc_gk(donnees["arrets"], donnees["buts_evites"],
                           donnees["erreurs_gk"]),
        "SET":    calc_set(donnees["danger_off"], donnees["solidite_def"]),
        "STYLE":  calc_style(donnees["pressing"], donnees["possession"],
                              donnees["compacite"], donnees["rythme"],
                              donnees["style_adv"]),
        "MARKET": calc_market(donnees["proba_marche"]),
        "ELO":    calc_elo(donnees.get("ecart_elo", 0.0)),
    }
