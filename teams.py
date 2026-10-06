"""
teams.py — Mapping équipe → championnat principal.
Permet la détection automatique de la ligue depuis les noms d'équipes.

⚠️ Une équipe peut jouer dans plusieurs compétitions (ex: Premier League + Champions League).
Ce module retourne sa LIGUE DOMESTIQUE par défaut. L'utilisateur peut toujours changer.
"""


# --- Mapping équipe → ligue ---
TEAMS_TO_LEAGUE = {
    # ============== PREMIER LEAGUE ==============
    "arsenal": "Premier League",
    "liverpool": "Premier League",
    "manchester city": "Premier League",
    "man city": "Premier League",
    "manchester united": "Premier League",
    "man united": "Premier League",
    "chelsea": "Premier League",
    "tottenham": "Premier League",
    "spurs": "Premier League",
    "newcastle": "Premier League",
    "aston villa": "Premier League",
    "brighton": "Premier League",
    "west ham": "Premier League",
    "crystal palace": "Premier League",
    "everton": "Premier League",
    "fulham": "Premier League",
    "brentford": "Premier League",
    "nottingham forest": "Premier League",
    "wolves": "Premier League",
    "wolverhampton": "Premier League",
    "bournemouth": "Premier League",
    "leicester": "Premier League",
    "ipswich": "Premier League",
    "southampton": "Premier League",

    # ============== BUNDESLIGA ==============
    "bayern munich": "Bundesliga",
    "bayern": "Bundesliga",
    "borussia dortmund": "Bundesliga",
    "dortmund": "Bundesliga",
    "rb leipzig": "Bundesliga",
    "leipzig": "Bundesliga",
    "bayer leverkusen": "Bundesliga",
    "leverkusen": "Bundesliga",
    "eintracht frankfurt": "Bundesliga",
    "frankfurt": "Bundesliga",
    "vfb stuttgart": "Bundesliga",
    "stuttgart": "Bundesliga",
    "borussia monchengladbach": "Bundesliga",
    "wolfsburg": "Bundesliga",
    "union berlin": "Bundesliga",
    "freiburg": "Bundesliga",
    "werder bremen": "Bundesliga",
    "mainz": "Bundesliga",
    "hoffenheim": "Bundesliga",
    "augsburg": "Bundesliga",
    "bochum": "Bundesliga",
    "koln": "Bundesliga",
    "cologne": "Bundesliga",
    "heidenheim": "Bundesliga",
    "st pauli": "Bundesliga",

    # ============== SERIE A ==============
    "inter": "Serie A",
    "inter milan": "Serie A",
    "ac milan": "Serie A",
    "milan": "Serie A",
    "juventus": "Serie A",
    "juve": "Serie A",
    "napoli": "Serie A",
    "roma": "Serie A",
    "as roma": "Serie A",
    "lazio": "Serie A",
    "atalanta": "Serie A",
    "fiorentina": "Serie A",
    "bologna": "Serie A",
    "torino": "Serie A",
    "genoa": "Serie A",
    "udinese": "Serie A",
    "monza": "Serie A",
    "lecce": "Serie A",
    "cagliari": "Serie A",
    "verona": "Serie A",
    "empoli": "Serie A",
    "parma": "Serie A",
    "como": "Serie A",
    "venezia": "Serie A",

    # ============== LA LIGA ==============
    "real madrid": "La Liga",
    "barcelona": "La Liga",
    "barca": "La Liga",
    "atletico madrid": "La Liga",
    "atletico": "La Liga",
    "sevilla": "La Liga",
    "real betis": "La Liga",
    "betis": "La Liga",
    "real sociedad": "La Liga",
    "athletic bilbao": "La Liga",
    "athletic club": "La Liga",
    "villarreal": "La Liga",
    "valencia": "La Liga",
    "girona": "La Liga",
    "osasuna": "La Liga",
    "celta vigo": "La Liga",
    "rayo vallecano": "La Liga",
    "mallorca": "La Liga",
    "getafe": "La Liga",
    "alaves": "La Liga",
    "las palmas": "La Liga",
    "espanyol": "La Liga",
    "leganes": "La Liga",
    "valladolid": "La Liga",

    # ============== LIGUE 1 ==============
    "psg": "Ligue 1",
    "paris saint germain": "Ligue 1",
    "paris sg": "Ligue 1",
    "marseille": "Ligue 1",
    "om": "Ligue 1",
    "lyon": "Ligue 1",
    "monaco": "Ligue 1",
    "lille": "Ligue 1",
    "nice": "Ligue 1",
    "rennes": "Ligue 1",
    "lens": "Ligue 1",
    "strasbourg": "Ligue 1",
    "nantes": "Ligue 1",
    "reims": "Ligue 1",
    "toulouse": "Ligue 1",
    "montpellier": "Ligue 1",
    "brest": "Ligue 1",
    "auxerre": "Ligue 1",
    "angers": "Ligue 1",
    "le havre": "Ligue 1",
    "saint etienne": "Ligue 1",

    # ============== EREDIVISIE ==============
    "ajax": "Eredivisie",
    "psv": "Eredivisie",
    "psv eindhoven": "Eredivisie",
    "feyenoord": "Eredivisie",
    "az alkmaar": "Eredivisie",
    "az": "Eredivisie",
    "twente": "Eredivisie",
    "utrecht": "Eredivisie",

    # ============== PRO LEAGUE BELGIQUE ==============
    "club brugge": "Pro League (Belgique)",
    "anderlecht": "Pro League (Belgique)",
    "genk": "Pro League (Belgique)",
    "gent": "Pro League (Belgique)",
    "standard liege": "Pro League (Belgique)",
    "antwerp": "Pro League (Belgique)",
    "union saint gilloise": "Pro League (Belgique)",

    # ============== PRIMEIRA LIGA ==============
    "benfica": "Primeira Liga",
    "porto": "Primeira Liga",
    "fc porto": "Primeira Liga",
    "sporting": "Primeira Liga",
    "sporting cp": "Primeira Liga",
    "braga": "Primeira Liga",
    "vitoria": "Primeira Liga",

    # ============== SÜPER LIG TURQUIE ==============
    "galatasaray": "Süper Lig",
    "fenerbahce": "Süper Lig",
    "besiktas": "Süper Lig",
    "trabzonspor": "Süper Lig",
    "basaksehir": "Süper Lig",

    # ============== SAUDI PRO LEAGUE ==============
    "al hilal": "Saudi Pro League",
    "al nassr": "Saudi Pro League",
    "al ittihad": "Saudi Pro League",
    "al ahli": "Saudi Pro League",
    "al shabab": "Saudi Pro League",

    # ============== MLS ==============
    "inter miami": "MLS",
    "la galaxy": "MLS",
    "lafc": "MLS",
    "los angeles fc": "MLS",
    "atlanta united": "MLS",
    "seattle sounders": "MLS",
    "portland timbers": "MLS",
    "new york city fc": "MLS",
    "nycfc": "MLS",
    "new york red bulls": "MLS",

    # ============== BRASILEIRAO ==============
    "flamengo": "Brasileirão",
    "palmeiras": "Brasileirão",
    "corinthians": "Brasileirão",
    "sao paulo": "Brasileirão",
    "santos": "Brasileirão",
    "fluminense": "Brasileirão",
    "botafogo": "Brasileirão",
    "vasco": "Brasileirão",
    "cruzeiro": "Brasileirão",
    "atletico mineiro": "Brasileirão",
    "gremio": "Brasileirão",
    "internacional": "Brasileirão",

    # ============== ARGENTINE ==============
    "boca juniors": "Liga Profesional (ARG)",
    "river plate": "Liga Profesional (ARG)",
    "racing club": "Liga Profesional (ARG)",
    "independiente": "Liga Profesional (ARG)",
    "san lorenzo": "Liga Profesional (ARG)",

    # ============== LIGA MX ==============
    "club america": "Liga MX",
    "chivas": "Liga MX",
    "guadalajara": "Liga MX",
    "cruz azul": "Liga MX",
    "tigres": "Liga MX",
    "monterrey": "Liga MX",
    "pumas": "Liga MX",

    # ============== AFRIQUE ==============
    "al ahly": "Egyptian Premier League",
    "zamalek": "Egyptian Premier League",
    "wydad": "Ligue 1 (Maroc)",
    "raja casablanca": "Ligue 1 (Maroc)",
    "esperance": "Ligue 1 (Tunisie)",
    "etoile du sahel": "Ligue 1 (Tunisie)",
    "tpmazembe": "Linafoot (RDC)",
    "tp mazembe": "Linafoot (RDC)",
    "as vita club": "Linafoot (RDC)",

    # ============== SÉLECTIONS ==============
    "france": "Euro",
    "espagne": "Euro",
    "spain": "Euro",
    "angleterre": "Euro",
    "england": "Euro",
    "allemagne": "Euro",
    "germany": "Euro",
    "italie": "Euro",
    "italy": "Euro",
    "portugal": "Euro",
    "belgique": "Euro",
    "belgium": "Euro",
    "pays-bas": "Euro",
    "netherlands": "Euro",
    "croatie": "Euro",
    "croatia": "Euro",
    "senegal": "CAN",
    "cote d'ivoire": "CAN",
    "ivory coast": "CAN",
    "maroc": "CAN",
    "morocco": "CAN",
    "egypte": "CAN",
    "egypt": "CAN",
    "nigeria": "CAN",
    "cameroun": "CAN",
    "cameroon": "CAN",
    "algerie": "CAN",
    "algeria": "CAN",
    "tunisie": "CAN",
    "tunisia": "CAN",
    "bresil": "Copa América",
    "brazil": "Copa América",
    "argentine": "Copa América",
    "argentina": "Copa América",
    "uruguay": "Copa América",
    "colombie": "Copa América",
    "colombia": "Copa América",
    "chili": "Copa América",
    "chile": "Copa América",
    "mexique": "Gold Cup",
    "mexico": "Gold Cup",
    "usa": "Gold Cup",
    "etats-unis": "Gold Cup",
}


def _normaliser(nom):
    """Normalise un nom d'équipe pour la recherche."""
    if not nom:
        return ""
    return nom.lower().strip().replace("-", " ").replace("_", " ")


def detecter_ligue(home_team, away_team):
    """
    Détecte automatiquement la ligue probable à partir des noms d'équipes.
    Retourne (ligue, confiance) où confiance ∈ {"high", "medium", "low", None}.
    - high : les 2 équipes reconnues dans la même ligue
    - medium : 1 équipe reconnue
    - low : les 2 reconnues mais ligues différentes
    - None : aucune équipe reconnue
    """
    h = _normaliser(home_team)
    a = _normaliser(away_team)

    ligue_h = TEAMS_TO_LEAGUE.get(h)
    ligue_a = TEAMS_TO_LEAGUE.get(a)

    if ligue_h and ligue_a:
        if ligue_h == ligue_a:
            return ligue_h, "high"
        return ligue_h, "low"
    if ligue_h:
        return ligue_h, "medium"
    if ligue_a:
        return ligue_a, "medium"
    return None, None


def equipe_connue(nom):
    """Vérifie si une équipe est dans la base."""
    return _normaliser(nom) in TEAMS_TO_LEAGUE


def nb_equipes():
    """Nombre d'équipes dans la base."""
    return len(TEAMS_TO_LEAGUE)


# --- Test local ---
if __name__ == "__main__":
    print(f"Base : {nb_equipes()} équipes\n")

    tests = [
        ("Arsenal", "Liverpool"),
        ("Real Madrid", "Barcelona"),
        ("Bayern Munich", "Dortmund"),
        ("PSG", "Marseille"),
        ("Al Hilal", "Al Nassr"),
        ("Flamengo", "Palmeiras"),
        ("Sénégal", "Maroc"),
        ("Arsenal", "Real Madrid"),
        ("Équipe Inconnue", "Autre Inconnue"),
    ]
    for h, a in tests:
        ligue, conf = detecter_ligue(h, a)
        print(f"{h} vs {a} → {ligue} ({conf})")
