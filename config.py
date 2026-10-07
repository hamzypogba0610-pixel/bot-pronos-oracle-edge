# ============================================================
# CONFIG — Oracle Edge v2.5
# 14 variables · 18 marchés · 5 familles de compétition
# ============================================================

LEAGUES = {
    # ============== TOP 5 EUROPÉEN ==============
    "Premier League":         {"pays": "Angleterre",       "avg_home": 1.55, "avg_away": 1.30, "type": "national",       "famille": "TOP_EUROPE"},
    "Bundesliga":             {"pays": "Allemagne",        "avg_home": 1.70, "avg_away": 1.40, "type": "national",       "famille": "TOP_EUROPE"},
    "Serie A":                {"pays": "Italie",           "avg_home": 1.50, "avg_away": 1.25, "type": "national",       "famille": "TOP_EUROPE"},
    "La Liga":                {"pays": "Espagne",          "avg_home": 1.45, "avg_away": 1.20, "type": "national",       "famille": "TOP_EUROPE"},
    "Ligue 1":                {"pays": "France",           "avg_home": 1.50, "avg_away": 1.20, "type": "national",       "famille": "TOP_EUROPE"},

    # ============== EUROPE — MAJEURS ==============
    "Eredivisie":             {"pays": "Pays-Bas",         "avg_home": 1.75, "avg_away": 1.45, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Pro League (Belgique)":  {"pays": "Belgique",         "avg_home": 1.60, "avg_away": 1.35, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Primeira Liga":          {"pays": "Portugal",         "avg_home": 1.45, "avg_away": 1.15, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Süper Lig":              {"pays": "Turquie",          "avg_home": 1.65, "avg_away": 1.30, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Championship":           {"pays": "Angleterre D2",    "avg_home": 1.40, "avg_away": 1.15, "type": "national",       "famille": "EUROPE_AUTRES"},

    # ============== EUROPE — SECONDAIRES ==============
    "Süper Lig Autriche":     {"pays": "Autriche",         "avg_home": 1.60, "avg_away": 1.25, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Super League Grèce":     {"pays": "Grèce",            "avg_home": 1.35, "avg_away": 1.05, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Scottish Premiership":   {"pays": "Écosse",           "avg_home": 1.55, "avg_away": 1.25, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Allsvenskan":            {"pays": "Suède",            "avg_home": 1.55, "avg_away": 1.20, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Eliteserien":            {"pays": "Norvège",          "avg_home": 1.65, "avg_away": 1.30, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Superligaen":            {"pays": "Danemark",         "avg_home": 1.60, "avg_away": 1.30, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Veikkausliiga":          {"pays": "Finlande",         "avg_home": 1.40, "avg_away": 1.15, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Swiss Super League":     {"pays": "Suisse",           "avg_home": 1.65, "avg_away": 1.35, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Chypre D1":              {"pays": "Chypre",           "avg_home": 1.40, "avg_away": 1.10, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Ligat ha'Al":            {"pays": "Israël",           "avg_home": 1.40, "avg_away": 1.10, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Ekstraklasa":            {"pays": "Pologne",          "avg_home": 1.45, "avg_away": 1.15, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Fortuna Liga":           {"pays": "Tchéquie",         "avg_home": 1.55, "avg_away": 1.20, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Nemzeti Bajnoksag":      {"pays": "Hongrie",          "avg_home": 1.50, "avg_away": 1.20, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Liga I (Roumanie)":      {"pays": "Roumanie",         "avg_home": 1.35, "avg_away": 1.10, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Serbia SuperLiga":       {"pays": "Serbie",           "avg_home": 1.45, "avg_away": 1.15, "type": "national",       "famille": "EUROPE_AUTRES"},
    "Croatie HNL":            {"pays": "Croatie",          "avg_home": 1.50, "avg_away": 1.20, "type": "national",       "famille": "EUROPE_AUTRES"},

    # ============== AMÉRIQUES ==============
    "Liga MX":                {"pays": "Mexique",          "avg_home": 1.45, "avg_away": 1.20, "type": "national",       "famille": "MONDE_AUTRES"},
    "Brasileirão":            {"pays": "Brésil",           "avg_home": 1.30, "avg_away": 0.95, "type": "national",       "famille": "MONDE_AUTRES"},
    "Liga Profesional (ARG)": {"pays": "Argentine",        "avg_home": 1.20, "avg_away": 0.85, "type": "national",       "famille": "MONDE_AUTRES"},
    "MLS":                    {"pays": "USA",              "avg_home": 1.55, "avg_away": 1.25, "type": "national",       "famille": "MONDE_AUTRES"},
    "Primera A (Colombie)":   {"pays": "Colombie",         "avg_home": 1.25, "avg_away": 0.90, "type": "national",       "famille": "MONDE_AUTRES"},
    "Primera División (Chili)": {"pays": "Chili",          "avg_home": 1.35, "avg_away": 1.00, "type": "national",       "famille": "MONDE_AUTRES"},
    "LigaPro (Équateur)":     {"pays": "Équateur",         "avg_home": 1.35, "avg_away": 1.00, "type": "national",       "famille": "MONDE_AUTRES"},
    "Liga 1 (Pérou)":         {"pays": "Pérou",            "avg_home": 1.30, "avg_away": 0.95, "type": "national",       "famille": "MONDE_AUTRES"},

    # ============== ASIE / MOYEN-ORIENT ==============
    "Saudi Pro League":       {"pays": "Arabie Saoudite",  "avg_home": 1.70, "avg_away": 1.35, "type": "national",       "famille": "MONDE_AUTRES"},
    "UAE Pro League":         {"pays": "Émirats",          "avg_home": 1.70, "avg_away": 1.40, "type": "national",       "famille": "MONDE_AUTRES"},
    "Qatar Stars League":     {"pays": "Qatar",            "avg_home": 1.65, "avg_away": 1.35, "type": "national",       "famille": "MONDE_AUTRES"},
    "J1 League":              {"pays": "Japon",            "avg_home": 1.45, "avg_away": 1.20, "type": "national",       "famille": "MONDE_AUTRES"},
    "K League 1":             {"pays": "Corée du Sud",     "avg_home": 1.40, "avg_away": 1.15, "type": "national",       "famille": "MONDE_AUTRES"},
    "Chinese Super League":   {"pays": "Chine",            "avg_home": 1.55, "avg_away": 1.25, "type": "national",       "famille": "MONDE_AUTRES"},

    # ============== AFRIQUE ==============
    "Ligue 1 (Maroc)":        {"pays": "Maroc",            "avg_home": 1.25, "avg_away": 0.85, "type": "national",       "famille": "MONDE_AUTRES"},
    "Ligue 1 (Tunisie)":      {"pays": "Tunisie",          "avg_home": 1.20, "avg_away": 0.80, "type": "national",       "famille": "MONDE_AUTRES"},
    "Egyptian Premier League": {"pays": "Égypte",          "avg_home": 1.30, "avg_away": 0.90, "type": "national",       "famille": "MONDE_AUTRES"},
    "Ligue 1 (Algérie)":      {"pays": "Algérie",          "avg_home": 1.20, "avg_away": 0.80, "type": "national",       "famille": "MONDE_AUTRES"},
    "Nigeria Premier League": {"pays": "Nigeria",          "avg_home": 1.30, "avg_away": 0.75, "type": "national",       "famille": "MONDE_AUTRES"},
    "Linafoot (RDC)":         {"pays": "RD Congo",         "avg_home": 1.20, "avg_away": 0.70, "type": "national",       "famille": "MONDE_AUTRES"},

    # ============== COUPES DE CLUBS ==============
    "Champions League":       {"pays": "Europe",           "avg_home": 1.55, "avg_away": 1.25, "type": "cup",            "famille": "COUPES_CLUBS"},
    "Europa League":          {"pays": "Europe",           "avg_home": 1.55, "avg_away": 1.20, "type": "cup",            "famille": "COUPES_CLUBS"},
    "Conference League":      {"pays": "Europe",           "avg_home": 1.65, "avg_away": 1.30, "type": "cup",            "famille": "COUPES_CLUBS"},
    "Copa Libertadores":      {"pays": "CONMEBOL",         "avg_home": 1.45, "avg_away": 1.05, "type": "cup",            "famille": "COUPES_CLUBS"},
    "Copa Sudamericana":      {"pays": "CONMEBOL",         "avg_home": 1.45, "avg_away": 1.05, "type": "cup",            "famille": "COUPES_CLUBS"},
    "CAF Champions League":   {"pays": "CAF",              "avg_home": 1.35, "avg_away": 0.90, "type": "cup",            "famille": "COUPES_CLUBS"},

    # ============== SÉLECTIONS ==============
    "Coupe du Monde":         {"pays": "FIFA",             "avg_home": 1.35, "avg_away": 1.10, "type": "national_team",  "famille": "SELECTIONS"},
    "Qualifs CdM":            {"pays": "FIFA",             "avg_home": 1.50, "avg_away": 1.15, "type": "national_team",  "famille": "SELECTIONS"},
    "Euro":                   {"pays": "UEFA",             "avg_home": 1.25, "avg_away": 1.05, "type": "national_team",  "famille": "SELECTIONS"},
    "Qualifs Euro":           {"pays": "UEFA",             "avg_home": 1.45, "avg_away": 1.10, "type": "national_team",  "famille": "SELECTIONS"},
    "CAN":                    {"pays": "CAF",              "avg_home": 1.20, "avg_away": 0.95, "type": "national_team",  "famille": "SELECTIONS"},
    "Qualifs CAN":            {"pays": "CAF",              "avg_home": 1.35, "avg_away": 1.00, "type": "national_team",  "famille": "SELECTIONS"},
    "Copa América":           {"pays": "CONMEBOL",         "avg_home": 1.25, "avg_away": 1.00, "type": "national_team",  "famille": "SELECTIONS"},
    "Ligue des Nations":      {"pays": "UEFA",             "avg_home": 1.35, "avg_away": 1.15, "type": "national_team",  "famille": "SELECTIONS"},
    "Gold Cup":               {"pays": "CONCACAF",         "avg_home": 1.40, "avg_away": 1.10, "type": "national_team",  "famille": "SELECTIONS"},
    "Asian Cup":              {"pays": "AFC",              "avg_home": 1.35, "avg_away": 1.10, "type": "national_team",  "famille": "SELECTIONS"},
}


# --- Multiplicateurs par FAMILLE de compétition ---
# Référence = TOP_EUROPE (tout à 1.0)
MULT_TYPES = {
    "TOP_EUROPE": {
        "FORM": 1.00, "ATT": 1.00, "DEF": 1.00, "XG": 1.00, "HOME": 1.00,
        "GOALS": 1.00, "ABS": 1.00, "H2H": 1.00, "MOT": 1.00, "GK": 1.00,
        "SET": 1.00, "STYLE": 1.00, "MARKET": 1.00, "ELO": 1.00,
    },
    "EUROPE_AUTRES": {
        "FORM": 1.10, "ATT": 1.00, "DEF": 1.00, "XG": 0.85, "HOME": 1.15,
        "GOALS": 1.00, "ABS": 1.00, "H2H": 1.10, "MOT": 1.00, "GK": 1.00,
        "SET": 1.00, "STYLE": 0.95, "MARKET": 1.20, "ELO": 0.95,
    },
    "COUPES_CLUBS": {
        "FORM": 0.85, "ATT": 1.00, "DEF": 1.05, "XG": 0.95, "HOME": 1.05,
        "GOALS": 0.95, "ABS": 1.00, "H2H": 0.85, "MOT": 1.20, "GK": 1.00,
        "SET": 1.00, "STYLE": 1.00, "MARKET": 1.15, "ELO": 1.00,
    },
    "MONDE_AUTRES": {
        "FORM": 1.00, "ATT": 1.00, "DEF": 1.00, "XG": 0.80, "HOME": 1.25,
        "GOALS": 1.00, "ABS": 1.15, "H2H": 1.05, "MOT": 1.10, "GK": 1.00,
        "SET": 1.00, "STYLE": 0.90, "MARKET": 1.25, "ELO": 0.90,
    },
    "SELECTIONS": {
        "FORM": 0.85, "ATT": 0.95, "DEF": 1.10, "XG": 0.95, "HOME": 0.90,
        "GOALS": 1.15, "ABS": 1.10, "H2H": 1.30, "MOT": 1.30, "GK": 1.00,
        "SET": 1.05, "STYLE": 1.05, "MARKET": 1.15, "ELO": 0.95,
    },
}


VARIABLES = [
    "FORM", "ATT", "DEF", "XG", "HOME",
    "GOALS", "ABS", "H2H", "MOT", "GK",
    "SET", "STYLE", "MARKET", "ELO",
]

POIDS_BASE = {
    "FORM": 0.11, "ATT": 0.11, "DEF": 0.11, "XG": 0.13,
    "HOME": 0.07, "GOALS": 0.07, "ABS": 0.07, "H2H": 0.05,
    "MOT": 0.05, "GK": 0.04, "SET": 0.03, "STYLE": 0.05,
    "MARKET": 0.04, "ELO": 0.07,
}

FIABILITE = {
    "FORM": 0.86, "ATT": 0.80, "DEF": 0.78, "XG": 0.92,
    "HOME": 0.82, "GOALS": 0.80, "ABS": 0.72, "H2H": 0.55,
    "MOT": 0.65, "GK": 0.75, "SET": 0.70, "STYLE": 0.68,
    "MARKET": 0.85, "ELO": 0.88,
}

BASELINES = {
    "1":      0.44, "X":      0.26, "2":      0.30,
    "O0.5":   0.92, "U0.5":   0.08,
    "O1.5":   0.78, "U1.5":   0.22,
    "O2.5":   0.52, "U2.5":   0.48,
    "O3.5":   0.28, "U3.5":   0.72,
    "AH-0.5": 0.44, "AH+0.5": 0.56,
    "AH-1.5": 0.28, "AH+1.5": 0.72,
    "AH-2.5": 0.14, "AH+2.5": 0.86,
    "BTTS":   0.52,
}

POIDS_MARCHE = {
    "1":      {"FORM": 11, "ATT": 11, "DEF": 9, "XG": 12, "HOME": 14,
               "GOALS": 5, "ABS": 6, "H2H": 5, "MOT": 5, "GK": 3,
               "SET": 3, "STYLE": 5, "MARKET": 4, "ELO": 7},
    "X":      {"FORM": 6, "ATT": 4, "DEF": 11, "XG": 6, "HOME": 3,
               "GOALS": 17, "ABS": 5, "H2H": 8, "MOT": 6, "GK": 8,
               "SET": 2, "STYLE": 11, "MARKET": 9, "ELO": 4},
    "2":      {"FORM": 12, "ATT": 12, "DEF": 10, "XG": 13, "HOME": -11,
               "GOALS": 5, "ABS": 6, "H2H": 4, "MOT": 4, "GK": 4,
               "SET": 3, "STYLE": 5, "MARKET": 5, "ELO": 6},
    "O0.5":   {"FORM": 5, "ATT": 15, "DEF": -8, "XG": 15, "HOME": 3,
               "GOALS": 12, "ABS": 5, "H2H": 5, "MOT": 3, "GK": -5,
               "SET": 3, "STYLE": 10, "MARKET": 9, "ELO": -2},
    "U0.5":   {"FORM": 4, "ATT": -9, "DEF": 15, "XG": -13, "HOME": -3,
               "GOALS": 17, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 7,
               "SET": 2, "STYLE": 8, "MARKET": 6, "ELO": 2},
    "O1.5":   {"FORM": 5, "ATT": 14, "DEF": -8, "XG": 16, "HOME": 3,
               "GOALS": 13, "ABS": 4, "H2H": 5, "MOT": 3, "GK": -5,
               "SET": 3, "STYLE": 10, "MARKET": 7, "ELO": -2},
    "U1.5":   {"FORM": 5, "ATT": -8, "DEF": 14, "XG": -12, "HOME": -3,
               "GOALS": 16, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 7,
               "SET": 2, "STYLE": 10, "MARKET": 8, "ELO": 2},
    "O2.5":   {"FORM": 6, "ATT": 13, "DEF": -9, "XG": 17, "HOME": 3,
               "GOALS": 13, "ABS": 4, "H2H": 5, "MOT": 3, "GK": -4,
               "SET": 3, "STYLE": 10, "MARKET": 6, "ELO": -3},
    "U2.5":   {"FORM": 5, "ATT": -8, "DEF": 13, "XG": -13, "HOME": -3,
               "GOALS": 17, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 6,
               "SET": 2, "STYLE": 12, "MARKET": 6, "ELO": 3},
    "O3.5":   {"FORM": 5, "ATT": 15, "DEF": -11, "XG": 17, "HOME": 3,
               "GOALS": 11, "ABS": 5, "H2H": 4, "MOT": 3, "GK": -6,
               "SET": 3, "STYLE": 11, "MARKET": 2, "ELO": -4},
    "U3.5":   {"FORM": 5, "ATT": -6, "DEF": 13, "XG": -11, "HOME": -2,
               "GOALS": 15, "ABS": 3, "H2H": 5, "MOT": 3, "GK": 8,
               "SET": 3, "STYLE": 12, "MARKET": 11, "ELO": 3},
    "AH-0.5": {"FORM": 11, "ATT": 12, "DEF": 9, "XG": 13, "HOME": 13,
               "GOALS": 4, "ABS": 6, "H2H": 5, "MOT": 5, "GK": 3,
               "SET": 3, "STYLE": 5, "MARKET": 5, "ELO": 6},
    "AH+0.5": {"FORM": 6, "ATT": 5, "DEF": 12, "XG": 7, "HOME": -8,
               "GOALS": 15, "ABS": 5, "H2H": 7, "MOT": 6, "GK": 7,
               "SET": 3, "STYLE": 10, "MARKET": 6, "ELO": -3},
    "AH-1.5": {"FORM": 10, "ATT": 15, "DEF": 8, "XG": 14, "HOME": 11,
               "GOALS": 5, "ABS": 6, "H2H": 4, "MOT": 4, "GK": 3,
               "SET": 3, "STYLE": 6, "MARKET": 5, "ELO": 6},
    "AH+1.5": {"FORM": 7, "ATT": -3, "DEF": 13, "XG": -5, "HOME": -6,
               "GOALS": 13, "ABS": 5, "H2H": 6, "MOT": 5, "GK": 9,
               "SET": 3, "STYLE": 11, "MARKET": 9, "ELO": -3},
    "AH-2.5": {"FORM": 9, "ATT": 17, "DEF": 7, "XG": 14, "HOME": 9,
               "GOALS": 4, "ABS": 5, "H2H": 4, "MOT": 4, "GK": 3,
               "SET": 3, "STYLE": 8, "MARKET": 8, "ELO": 5},
    "AH+2.5": {"FORM": 8, "ATT": -8, "DEF": 14, "XG": -11, "HOME": -4,
               "GOALS": 11, "ABS": 4, "H2H": 5, "MOT": 4, "GK": 10,
               "SET": 3, "STYLE": 12, "MARKET": 9, "ELO": -4},
    "BTTS":   {"FORM": 4, "ATT": 11, "DEF": -8, "XG": 13, "HOME": 2,
               "GOALS": 11, "ABS": 4, "H2H": 8, "MOT": 3, "GK": -6,
               "SET": 2, "STYLE": 14, "MARKET": 9, "ELO": -3},
}

REGIMES = {
    "A": {"FORM": 0.9, "ATT": 0.7, "DEF": 1.3, "XG": 0.85, "HOME": 1.1,
          "GOALS": 1.3, "ABS": 0.9, "H2H": 1.1, "MOT": 1.0, "GK": 1.3,
          "SET": 1.2, "STYLE": 1.0, "MARKET": 0.9, "ELO": 1.1},
    "B": {"FORM": 1.0, "ATT": 1.3, "DEF": 0.7, "XG": 1.3, "HOME": 1.0,
          "GOALS": 1.1, "ABS": 1.0, "H2H": 0.9, "MOT": 1.0, "GK": 0.8,
          "SET": 1.0, "STYLE": 1.2, "MARKET": 1.0, "ELO": 1.0},
    "C": {"FORM": 1.2, "ATT": 1.2, "DEF": 1.1, "XG": 1.2, "HOME": 1.1,
          "GOALS": 1.0, "ABS": 1.1, "H2H": 0.9, "MOT": 0.9, "GK": 0.9,
          "SET": 0.9, "STYLE": 1.0, "MARKET": 0.8, "ELO": 1.3},
    "D": {"FORM": 1.0, "ATT": 1.0, "DEF": 1.0, "XG": 1.0, "HOME": 0.8,
          "GOALS": 1.0, "ABS": 1.0, "H2H": 1.2, "MOT": 1.1, "GK": 1.0,
          "SET": 1.0, "STYLE": 1.2, "MARKET": 1.1, "ELO": 0.9},
    "E": {"FORM": 0.7, "ATT": 0.7, "DEF": 0.7, "XG": 0.8, "HOME": 0.7,
          "GOALS": 0.7, "ABS": 0.8, "H2H": 0.7, "MOT": 0.6, "GK": 0.8,
          "SET": 0.8, "STYLE": 0.8, "MARKET": 1.4, "ELO": 0.9},
}

ROB_SEUILS = {
    "EXCELLENT": 0.92, "ROBUSTE": 0.85,
    "MOYEN": 0.75, "FRAGILE": 0.65,
}
ROB_MIN_ACCEPTATION = 0.75

MIN_EDGE = 0.03
MIN_ODDS = 1.50
MAX_ODDS = 8.00

SCORE_SEUILS = {
    "REJET": 50, "FAIBLE": 60, "INTERESSANT": 70,
    "FORT": 80, "TRES_FORT": 90,
}

MASTER = {
    "eta": 0.01,
    "chaos_poids": 1.0,
    "monte_carlo_sims": 1000,
    "bruit_lambda": 0.15,
}

FORM_WINDOW = 5
H2H_WINDOW = 5
MAX_GOALS_MATRIX = 6

MODEL_VERSION = "oracle-edge v2.5"
