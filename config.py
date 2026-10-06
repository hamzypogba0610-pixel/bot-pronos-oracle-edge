# ============================================================
# CONFIG — Oracle Edge
# Fichier de paramètres global. Aucun calcul ici.
# ============================================================

# --- 5 championnats analysés ---
LEAGUES = {
    "Premier League": {"pays": "Angleterre", "avg_home": 1.55, "avg_away": 1.30},
    "Bundesliga":     {"pays": "Allemagne",  "avg_home": 1.70, "avg_away": 1.40},
    "Serie A":        {"pays": "Italie",     "avg_home": 1.50, "avg_away": 1.25},
    "La Liga":        {"pays": "Espagne",    "avg_home": 1.45, "avg_away": 1.20},
    "Ligue 1":        {"pays": "France",     "avg_home": 1.50, "avg_away": 1.20},
}

# --- Les 13 variables et leurs poids initiaux ---
VARIABLES = [
    "FORM", "ATT", "DEF", "XG", "HOME",
    "GOALS", "ABS", "H2H", "MOT", "GK",
    "SET", "STYLE", "MARKET",
]

POIDS_BASE = {
    "FORM": 0.12, "ATT": 0.12, "DEF": 0.12, "XG": 0.14,
    "HOME": 0.08, "GOALS": 0.08, "ABS": 0.08, "H2H": 0.05,
    "MOT": 0.05, "GK": 0.04, "SET": 0.03, "STYLE": 0.05,
    "MARKET": 0.04,
}

# --- Fiabilité initiale de chaque variable (0-1) ---
FIABILITE = {
    "FORM": 0.86, "ATT": 0.80, "DEF": 0.78, "XG": 0.92,
    "HOME": 0.82, "GOALS": 0.80, "ABS": 0.72, "H2H": 0.55,
    "MOT": 0.65, "GK": 0.75, "SET": 0.70, "STYLE": 0.68,
    "MARKET": 0.85,
}

# --- Matrice W(i,m) : poids de chaque variable par marché ---
# Marchés :
#   1X2 : 1, X, 2
#   O/U : O0.5, U0.5, O1.5, U1.5, O2.5, U2.5, O3.5, U3.5
#   AH  : AH-0.5, AH+0.5, AH-1.5, AH+1.5, AH-2.5, AH+2.5
#   BTTS
POIDS_MARCHE = {
    "1":      {"FORM": 12, "ATT": 12, "DEF": 10, "XG": 13, "HOME": 16,
               "GOALS": 5, "ABS": 7, "H2H": 5, "MOT": 5, "GK": 3,
               "SET": 3, "STYLE": 5, "MARKET": 4},
    "X":      {"FORM": 6, "ATT": 4, "DEF": 12, "XG": 6, "HOME": 3,
               "GOALS": 18, "ABS": 6, "H2H": 8, "MOT": 6, "GK": 8,
               "SET": 2, "STYLE": 11, "MARKET": 10},
    "2":      {"FORM": 13, "ATT": 13, "DEF": 11, "XG": 14, "HOME": -12,
               "GOALS": 5, "ABS": 7, "H2H": 4, "MOT": 4, "GK": 4,
               "SET": 3, "STYLE": 5, "MARKET": 5},
    "O0.5":   {"FORM": 5, "ATT": 16, "DEF": -8, "XG": 16, "HOME": 3,
               "GOALS": 12, "ABS": 5, "H2H": 5, "MOT": 3, "GK": -5,
               "SET": 3, "STYLE": 10, "MARKET": 9},
    "U0.5":   {"FORM": 4, "ATT": -10, "DEF": 16, "XG": -14, "HOME": -3,
               "GOALS": 18, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 7,
               "SET": 2, "STYLE": 8, "MARKET": 6},
    "O1.5":   {"FORM": 5, "ATT": 15, "DEF": -9, "XG": 17, "HOME": 3,
               "GOALS": 14, "ABS": 4, "H2H": 5, "MOT": 3, "GK": -5,
               "SET": 3, "STYLE": 10, "MARKET": 7},
    "U1.5":   {"FORM": 5, "ATT": -8, "DEF": 15, "XG": -13, "HOME": -3,
               "GOALS": 17, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 7,
               "SET": 2, "STYLE": 10, "MARKET": 8},
    "O2.5":   {"FORM": 6, "ATT": 14, "DEF": -10, "XG": 18, "HOME": 3,
               "GOALS": 14, "ABS": 4, "H2H": 5, "MOT": 3, "GK": -4,
               "SET": 3, "STYLE": 10, "MARKET": 6},
    "U2.5":   {"FORM": 5, "ATT": -8, "DEF": 14, "XG": -14, "HOME": -3,
               "GOALS": 18, "ABS": 3, "H2H": 6, "MOT": 3, "GK": 6,
               "SET": 2, "STYLE": 12, "MARKET": 6},
    "O3.5":   {"FORM": 5, "ATT": 16, "DEF": -12, "XG": 18, "HOME": 3,
               "GOALS": 12, "ABS": 5, "H2H": 4, "MOT": 3, "GK": -6,
               "SET": 3, "STYLE": 11, "MARKET": 2},
    "U3.5":   {"FORM": 5, "ATT": -6, "DEF": 14, "XG": -12, "HOME": -2,
               "GOALS": 16, "ABS": 3, "H2H": 5, "MOT": 3, "GK": 8,
               "SET": 3, "STYLE": 12, "MARKET": 11},
    # --- Handicaps asiatiques ---
    "AH-0.5": {"FORM": 12, "ATT": 13, "DEF": 10, "XG": 14, "HOME": 14,
               "GOALS": 4, "ABS": 7, "H2H": 5, "MOT": 5, "GK": 3,
               "SET": 3, "STYLE": 5, "MARKET": 5},
    "AH+0.5": {"FORM": 6, "ATT": 5, "DEF": 13, "XG": 7, "HOME": -8,
               "GOALS": 16, "ABS": 6, "H2H": 7, "MOT": 6, "GK": 7,
               "SET": 3, "STYLE": 10, "MARKET": 6},
    "AH-1.5": {"FORM": 11, "ATT": 16, "DEF": 9, "XG": 15, "HOME": 12,
               "GOALS": 5, "ABS": 6, "H2H": 4, "MOT": 4, "GK": 3,
               "SET": 3, "STYLE": 7, "MARKET": 5},
    "AH+1.5": {"FORM": 7, "ATT": -3, "DEF": 14, "XG": -6, "HOME": -6,
               "GOALS": 14, "ABS": 5, "H2H": 6, "MOT": 5, "GK": 9,
               "SET": 3, "STYLE": 11, "MARKET": 9},
    "AH-2.5": {"FORM": 10, "ATT": 18, "DEF": 8, "XG": 15, "HOME": 10,
               "GOALS": 4, "ABS": 5, "H2H": 4, "MOT": 4, "GK": 3,
               "SET": 3, "STYLE": 8, "MARKET": 8},
    "AH+2.5": {"FORM": 8, "ATT": -8, "DEF": 15, "XG": -12, "HOME": -4,
               "GOALS": 12, "ABS": 4, "H2H": 5, "MOT": 4, "GK": 10,
               "SET": 3, "STYLE": 12, "MARKET": 9},
    # --- BTTS ---
    "BTTS":   {"FORM": 4, "ATT": 12, "DEF": -8, "XG": 14, "HOME": 2,
               "GOALS": 12, "ABS": 4, "H2H": 8, "MOT": 3, "GK": -6,
               "SET": 2, "STYLE": 15, "MARKET": 10},
}

# --- Multiplicateurs par régime ---
REGIMES = {
    "A": {"FORM": 0.9, "ATT": 0.7, "DEF": 1.3, "XG": 0.85, "HOME": 1.1,
          "GOALS": 1.3, "ABS": 0.9, "H2H": 1.1, "MOT": 1.0, "GK": 1.3,
          "SET": 1.2, "STYLE": 1.0, "MARKET": 0.9},
    "B": {"FORM": 1.0, "ATT": 1.3, "DEF": 0.7, "XG": 1.3, "HOME": 1.0,
          "GOALS": 1.1, "ABS": 1.0, "H2H": 0.9, "MOT": 1.0, "GK": 0.8,
          "SET": 1.0, "STYLE": 1.2, "MARKET": 1.0},
    "C": {"FORM": 1.2, "ATT": 1.2, "DEF": 1.1, "XG": 1.2, "HOME": 1.1,
          "GOALS": 1.0, "ABS": 1.1, "H2H": 0.9, "MOT": 0.9, "GK": 0.9,
          "SET": 0.9, "STYLE": 1.0, "MARKET": 0.8},
    "D": {"FORM": 1.0, "ATT": 1.0, "DEF": 1.0, "XG": 1.0, "HOME": 0.8,
          "GOALS": 1.0, "ABS": 1.0, "H2H": 1.2, "MOT": 1.1, "GK": 1.0,
          "SET": 1.0, "STYLE": 1.2, "MARKET": 1.1},
    "E": {"FORM": 0.7, "ATT": 0.7, "DEF": 0.7, "XG": 0.8, "HOME": 0.7,
          "GOALS": 0.7, "ABS": 0.8, "H2H": 0.7, "MOT": 0.6, "GK": 0.8,
          "SET": 0.8, "STYLE": 0.8, "MARKET": 1.4},
}

# --- Seuils de robustesse ---
ROB_SEUILS = {
    "EXCELLENT": 0.92,
    "ROBUSTE": 0.85,
    "MOYEN": 0.75,
    "FRAGILE": 0.65,
}
ROB_MIN_ACCEPTATION = 0.75

# --- Seuils de value / EV ---
MIN_EDGE = 0.03
MIN_ODDS = 1.50
MAX_ODDS = 8.00

# --- Seuils de score final ---
SCORE_SEUILS = {
    "REJET": 50,
    "FAIBLE": 60,
    "INTERESSANT": 70,
    "FORT": 80,
    "TRES_FORT": 90,
}

# --- Paramètres du Master Score ---
MASTER = {
    "eta": 0.01,
    "chaos_poids": 1.0,
    "monte_carlo_sims": 1000,
    "bruit_lambda": 0.15,
}

# --- Fenêtres d'analyse ---
FORM_WINDOW = 5
H2H_WINDOW = 5
MAX_GOALS_MATRIX = 6

# --- Modèle ---
MODEL_VERSION = "oracle-edge v1.3"
