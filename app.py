"""
app.py — Interface Streamlit Oracle Edge v2.0.
DRC-X · MGE-R · Oracle Shield · CLV · Meta-Brain · ELO · Shin · Gradient.
"""

import json
from datetime import date

import streamlit as st

from config import LEAGUES
from analyse import analyser_match
import calibration as calib
import metabrain
import gradient
import elo
import drcx


st.set_page_config(
    page_title="Oracle Edge",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 20% 0%, #16233A 0%, #0E1117 55%) fixed;
    color: #E2E8F0;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px;}

.hero {
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(135deg, rgba(34,197,94,0.10), rgba(15,23,42,0.0));
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.hero-title { font-size: 22px; font-weight: 700; color: #F8FAFC; margin: 0; }
.hero-title span { color: #22C55E; }
.hero-sub { font-size: 12px; color: #94A3B8; margin-top: 3px; }
.hero-badge {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
    color: #22C55E;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 5px 10px; border-radius: 999px;
    font-weight: 600;
}
.steps { display: flex; gap: 5px; margin-bottom: 20px; }
.step { flex: 1; height: 4px; border-radius: 999px; background: rgba(148,163,184,0.15); }
.step.done { background: #22C55E; }
.step.active { background: #F59E0B; box-shadow: 0 0 10px rgba(245,158,11,0.5); }
.card {
    background: rgba(30,41,59,0.55);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
}
.card-title { font-size: 14px; font-weight: 600; color: #F8FAFC; margin: 0 0 4px 0; }
.card-sub { font-size: 12px; color: #94A3B8; margin-bottom: 12px; }
.stSelectbox label, .stTextInput label, .stDateInput label,
.stNumberInput label, .stTextArea label, .stSlider label {
    font-size: 11px !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input, .stDateInput input, .stNumberInput input {
    background: #0F172A !important;
    border: 1px solid rgba(148,163,184,0.2) !important;
    color: #F1F5F9 !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
}
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    border: 1px solid rgba(148,163,184,0.2) !important;
    background: rgba(30,41,59,0.8) !important;
    color: #E2E8F0 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #22C55E, #16A34A) !important;
    border: none !important;
    color: #062410 !important;
}
.result-card {
    background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(245,158,11,0.05));
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.alert-trap {
    background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(245,158,11,0.08));
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #FCA5A5;
    font-size: 13px;
}
.regime-box {
    background: linear-gradient(135deg, rgba(245,158,11,0.10), rgba(34,197,94,0.05));
    border: 1px solid rgba(245,158,11,0.30);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 14px;
}
.verdict-green { color: #22C55E; font-weight: 700; }
.verdict-yellow { color: #F59E0B; font-weight: 700; }
.verdict-red { color: #EF4444; font-weight: 700; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


PAGES = [
    "Sélection", "H2H", "Forme dom.", "Forme ext.",
    "Contexte", "Cotes", "Analyse", "Résultats",
]
OU_LIGNES = [0.5, 1.5, 2.5, 3.5]


def init_state():
    defaults = {
        "page": 0,
        "league": "Premier League",
        "match_date": date.today(),
        "home_team": "",
        "away_team": "",
        "h2h": [{"date": "", "score": ""} for _ in range(5)],
        "home_form": [{"date": "", "score": "", "xg": 0.0, "xga": 0.0,
                       "tirs": 0, "tirs_cadres": 0, "possession": 50} for _ in range(5)],
        "away_form": [{"date": "", "score": "", "xg": 0.0, "xga": 0.0,
                       "tirs": 0, "tirs_cadres": 0, "possession": 50} for _ in range(5)],
        "abs_home": 0.0, "abs_away": 0.0,
        "mot_home": 0.5, "mot_away": 0.5,
        "cotes_1x2": {"H": 2.00, "D": 3.50, "A": 3.50},
        "cotes_ou": {str(l): {"over": 1.90, "under": 1.90} for l in OU_LIGNES},
        "cotes_btts": {"oui": 1.85, "non": 1.85},
        "cotes_ah": {"-0.5": {"home": 1.90, "away": 1.90},
                     "-1.5": {"home": 3.00, "away": 1.40},
                     "-2.5": {"home": 6.00, "away": 1.12}},
        "cotes_cs": [("2-1", 7.50), ("1-1", 6.50), ("2-0", 9.00),
                     ("1-0", 8.50), ("1-2", 8.00)],
        "clv_actif": False,
        "cotes_1x2_ouv": {"H": 0.0, "D": 0.0, "A": 0.0},
        "cotes_ou_ouv": {str(l): {"over": 0.0, "under": 0.0} for l in OU_LIGNES},
        "cotes_btts_ouv": {"oui": 0.0},
        "cotes_ah_ouv": {"-0.5": {"home": 0.0, "away": 0.0},
                         "-1.5": {"home": 0.0, "away": 0.0},
                         "-2.5": {"home": 0.0, "away": 0.0}},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def hero():
    st.markdown("""
    <div class="hero">
        <div>
            <p class="hero-title">⚽ Oracle <span>Edge</span></p>
            <p class="hero-sub">DRC-X · MGE-R · Oracle Shield · CLV · Meta-Brain · ELO · Shin · Gradient</p>
        </div>
        <div class="hero-badge">v2.0</div>
    </div>
    """, unsafe_allow_html=True)


def stepper():
    html = '<div class="steps">'
    for i in range(len(PAGES)):
        cls = "step"
        if i < st.session_state.page:
            cls += " done"
        elif i == st.session_state.page:
            cls += " active"
        html += f'<div class="{cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:11px;color:#94A3B8;text-transform:uppercase;"
        f"font-weight:600;letter-spacing:0.05em;margin-bottom:14px;'>"
        f"Étape {st.session_state.page + 1}/{len(PAGES)} — {PAGES[st.session_state.page]}</p>",
        unsafe_allow_html=True,
    )


LABELS_SUIVANT = {
    0: "Suivant →",
    1: "Suivant →",
    2: "Suivant →",
    3: "Suivant →",
    4: "Suivant →",
    5: "Analyser 🚀",
    6: "Voir les résultats →",
}


def nav():
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.session_state.page > 0:
            if st.button("← Précédent", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
    with c3:
        if st.session_state.page in LABELS_SUIVANT:
            if st.button(LABELS_SUIVANT[st.session_state.page],
                         use_container_width=True, type="primary"):
                st.session_state.page += 1
                st.rerun()


def page_1():
    st.markdown('<div class="card"><p class="card-title">Configuration du match</p>'
                '<p class="card-sub">Championnat, date et équipes.</p></div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.session_state.league = st.selectbox(
            "Championnat", list(LEAGUES.keys()),
            index=list(LEAGUES.keys()).index(st.session_state.league),
        )
        st.caption(LEAGUES[st.session_state.league]["pays"])
    with c2:
        st.session_state.match_date = st.date_input(
            "Date", value=st.session_state.match_date
        )
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.home_team = st.text_input(
            "🏠 Équipe à domicile", value=st.session_state.home_team,
            placeholder="Arsenal",
        )
    with c2:
        st.session_state.away_team = st.text_input(
            "✈️ Équipe à l'extérieur", value=st.session_state.away_team,
            placeholder="Liverpool",
        )
    if st.session_state.home_team and st.session_state.away_team:
        try:
            r_h = elo.get_rating(st.session_state.home_team)
            r_a = elo.get_rating(st.session_state.away_team)
            ecart = elo.ecart_elo(st.session_state.home_team,
                                   st.session_state.away_team)
            st.info(f"🏅 **ELO** · {st.session_state.home_team} : {r_h:.0f} "
                    f"| {st.session_state.away_team} : {r_a:.0f} "
                    f"| Écart (avec avantage dom) : **{ecart:+.0f}**")
        except Exception:
            pass


def page_2():
    st.markdown('<div class="card"><p class="card-title">5 derniers face-à-face</p>'
                '<p class="card-sub">Format : date + score (ex: 2-1).</p></div>',
                unsafe_allow_html=True)
    for i in range(5):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.session_state.h2h[i]["date"] = st.text_input(
                f"Date #{i+1}", value=st.session_state.h2h[i]["date"],
                key=f"h2h_date_{i}", placeholder="JJ/MM/AA",
            )
        with c2:
            st.session_state.h2h[i]["score"] = st.text_input(
                f"Score #{i+1}", value=st.session_state.h2h[i]["score"],
                key=f"h2h_score_{i}", placeholder="2-1",
            )


def page_form(is_home):
    cible = "domicile" if is_home else "extérieur"
    equipe = st.session_state.home_team if is_home else st.session_state.away_team
    key = "home_form" if is_home else "away_form"

    st.markdown(f'<div class="card"><p class="card-title">'
                f'Forme {cible} — {equipe or "(à définir)"}</p>'
                f'<p class="card-sub">5 derniers matchs {cible}. '
                f'Score + xG + xGA + tirs + tirs cadrés + possession.</p></div>',
                unsafe_allow_html=True)

    for i in range(5):
        st.markdown(f"**Match #{i+1}**")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.session_state[key][i]["date"] = st.text_input(
                "Date", value=st.session_state[key][i]["date"],
                key=f"{key}_date_{i}", placeholder="JJ/MM/AA",
            )
        with c2:
            st.session_state[key][i]["score"] = st.text_input(
                "Score", value=st.session_state[key][i]["score"],
                key=f"{key}_score_{i}", placeholder="2-1",
            )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state[key][i]["xg"] = st.number_input(
                "xG", min_value=0.0, max_value=10.0,
                value=float(st.session_state[key][i]["xg"]),
                step=0.1, key=f"{key}_xg_{i}",
            )
        with c2:
            st.session_state[key][i]["xga"] = st.number_input(
                "xGA", min_value=0.0, max_value=10.0,
                value=float(st.session_state[key][i]["xga"]),
                step=0.1, key=f"{key}_xga_{i}",
            )
        with c3:
            st.session_state[key][i]["possession"] = st.number_input(
                "Possession %", min_value=0, max_value=100,
                value=int(st.session_state[key][i]["possession"]),
                step=1, key=f"{key}_pos_{i}",
            )
        c1, c2 = st.columns(2)
        with c1:
            st.session_state[key][i]["tirs"] = st.number_input(
                "Tirs", min_value=0, max_value=40,
                value=int(st.session_state[key][i]["tirs"]),
                step=1, key=f"{key}_tirs_{i}",
            )
        with c2:
            st.session_state[key][i]["tirs_cadres"] = st.number_input(
                "Tirs cadrés", min_value=0, max_value=20,
                value=int(st.session_state[key][i]["tirs_cadres"]),
                step=1, key=f"{key}_tc_{i}",
            )
        st.markdown("---")


def page_5():
    st.markdown('<div class="card"><p class="card-title">Contexte</p>'
                '<p class="card-sub">Absences et motivation. Optionnel.</p></div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**🏠 {st.session_state.home_team or 'Domicile'}**")
        st.session_state.abs_home = st.slider(
            "Impact absences", 0.0, 10.0, float(st.session_state.abs_home),
            key="abs_h", help="0 = aucune absence, 10 = effectif décimé",
        )
        st.session_state.mot_home = st.slider(
            "Motivation", 0.0, 1.0, float(st.session_state.mot_home),
            step=0.05, key="mot_h",
        )
    with c2:
        st.markdown(f"**✈️ {st.session_state.away_team or 'Extérieur'}**")
        st.session_state.abs_away = st.slider(
            "Impact absences", 0.0, 10.0, float(st.session_state.abs_away),
            key="abs_a",
        )
        st.session_state.mot_away = st.slider(
            "Motivation", 0.0, 1.0, float(st.session_state.mot_away),
            step=0.05, key="mot_a",
        )


def page_6():
    st.markdown('<div class="card"><p class="card-title">Cotes bookmaker</p>'
                '<p class="card-sub">Cotes de fermeture obligatoires. '
                'Cotes d\'ouverture optionnelles pour le CLV.</p></div>',
                unsafe_allow_html=True)

    st.session_state.clv_actif = st.toggle(
        "🔓 Activer le calcul du CLV (saisir les cotes d'ouverture)",
        value=st.session_state.clv_actif,
    )

    st.markdown("### **1X2**")
    if st.session_state.clv_actif:
        for label, key in [("🏠 Dom", "H"), ("Nul", "D"), ("✈️ Ext", "A")]:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**{label}**")
            with c2:
                st.session_state.cotes_1x2_ouv[key] = st.number_input(
                    f"Ouv. {label}", min_value=0.0,
                    value=float(st.session_state.cotes_1x2_ouv[key]),
                    step=0.01, key=f"c_ouv_1x2_{key}",
                )
            with c3:
                st.session_state.cotes_1x2[key] = st.number_input(
                    f"Ferm. {label}", min_value=1.01,
                    value=float(st.session_state.cotes_1x2[key]),
                    step=0.01, key=f"c_fer_1x2_{key}",
                )
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.cotes_1x2["H"] = st.number_input(
                "🏠 Dom", min_value=1.01,
                value=float(st.session_state.cotes_1x2["H"]),
                step=0.01, key="c_H",
            )
        with c2:
            st.session_state.cotes_1x2["D"] = st.number_input(
                "Nul", min_value=1.01,
                value=float(st.session_state.cotes_1x2["D"]),
                step=0.01, key="c_D",
            )
        with c3:
            st.session_state.cotes_1x2["A"] = st.number_input(
                "✈️ Ext", min_value=1.01,
                value=float(st.session_state.cotes_1x2["A"]),
                step=0.01, key="c_A",
            )

    st.markdown("### **Over / Under**")
    for l in OU_LIGNES:
        st.markdown(f"**Ligne {l}**")
        if st.session_state.clv_actif:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.cotes_ou_ouv[str(l)]["over"] = st.number_input(
                    "Ouv. Over", min_value=0.0,
                    value=float(st.session_state.cotes_ou_ouv[str(l)]["over"]),
                    step=0.01, key=f"c_ouv_ou_o_{l}",
                )
            with c2:
                st.session_state.cotes_ou[str(l)]["over"] = st.number_input(
                    "Ferm. Over", min_value=1.01,
                    value=float(st.session_state.cotes_ou[str(l)]["over"]),
                    step=0.01, key=f"c_fer_ou_o_{l}",
                )
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.cotes_ou_ouv[str(l)]["under"] = st.number_input(
                    "Ouv. Under", min_value=0.0,
                    value=float(st.session_state.cotes_ou_ouv[str(l)]["under"]),
                    step=0.01, key=f"c_ouv_ou_u_{l}",
                )
            with c2:
                st.session_state.cotes_ou[str(l)]["under"] = st.number_input(
                    "Ferm. Under", min_value=1.01,
                    value=float(st.session_state.cotes_ou[str(l)]["under"]),
                    step=0.01, key=f"c_fer_ou_u_{l}",
                )
        else:
            c1, c2, c3 = st.columns([1, 1, 1])
            c1.markdown(f"Ligne {l}")
            with c2:
                st.session_state.cotes_ou[str(l)]["over"] = st.number_input(
                    "Over", min_value=1.01,
                    value=float(st.session_state.cotes_ou[str(l)]["over"]),
                    step=0.01, key=f"c_ou_o_{l}",
                )
            with c3:
                st.session_state.cotes_ou[str(l)]["under"] = st.number_input(
                    "Under", min_value=1.01,
                    value=float(st.session_state.cotes_ou[str(l)]["under"]),
                    step=0.01, key=f"c_ou_u_{l}",
                )

    st.markdown("### **BTTS**")
    if st.session_state.clv_actif:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.cotes_btts_ouv["oui"] = st.number_input(
                "Ouv. Oui", min_value=0.0,
                value=float(st.session_state.cotes_btts_ouv["oui"]),
                step=0.01, key="c_ouv_btts",
            )
        with c2:
            st.session_state.cotes_btts["oui"] = st.number_input(
                "Ferm. Oui", min_value=1.01,
                value=float(st.session_state.cotes_btts["oui"]),
                step=0.01, key="c_fer_btts",
            )
        with c3:
            st.session_state.cotes_btts["non"] = st.number_input(
                "Ferm. Non", min_value=1.01,
                value=float(st.session_state.cotes_btts["non"]),
                step=0.01, key="c_fer_btts_non",
            )
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.cotes_btts["oui"] = st.number_input(
                "Oui", min_value=1.01,
                value=float(st.session_state.cotes_btts["oui"]),
                step=0.01, key="c_btts_oui",
            )
        with c2:
            st.session_state.cotes_btts["non"] = st.number_input(
                "Non", min_value=1.01,
                value=float(st.session_state.cotes_btts["non"]),
                step=0.01, key="c_btts_non",
            )

    st.markdown("### **Handicaps asiatiques**")
    for ligne in ["-0.5", "-1.5", "-2.5"]:
        st.markdown(f"**Ligne {ligne}**")
        if st.session_state.clv_actif:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.cotes_ah_ouv[ligne]["home"] = st.number_input(
                    "Ouv. Home", min_value=0.0,
                    value=float(st.session_state.cotes_ah_ouv[ligne]["home"]),
                    step=0.01, key=f"c_ouv_ah_h_{ligne}",
                )
            with c2:
                st.session_state.cotes_ah[ligne]["home"] = st.number_input(
                    "Ferm. Home", min_value=1.01,
                    value=float(st.session_state.cotes_ah[ligne]["home"]),
                    step=0.01, key=f"c_fer_ah_h_{ligne}",
                )
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.cotes_ah_ouv[ligne]["away"] = st.number_input(
                    "Ouv. Away", min_value=0.0,
                    value=float(st.session_state.cotes_ah_ouv[ligne]["away"]),
                    step=0.01, key=f"c_ouv_ah_a_{ligne}",
                )
            with c2:
                st.session_state.cotes_ah[ligne]["away"] = st.number_input(
                    "Ferm. Away", min_value=1.01,
                    value=float(st.session_state.cotes_ah[ligne]["away"]),
                    step=0.01, key=f"c_fer_ah_a_{ligne}",
                )
        else:
            c1, c2, c3 = st.columns([1, 1, 1])
            c1.markdown(f"Ligne {ligne}")
            with c2:
                st.session_state.cotes_ah[ligne]["home"] = st.number_input(
                    "Home", min_value=1.01,
                    value=float(st.session_state.cotes_ah[ligne]["home"]),
                    step=0.01, key=f"c_ah_h_{ligne}",
                )
            with c3:
                st.session_state.cotes_ah[ligne]["away"] = st.number_input(
                    "Away", min_value=1.01,
                    value=float(st.session_state.cotes_ah[ligne]["away"]),
                    step=0.01, key=f"c_ah_a_{ligne}",
                )

    st.markdown("### **Top 5 scores exacts**")
    for i in range(5):
        c1, c2 = st.columns([1, 2])
        with c1:
            score_act = st.session_state.cotes_cs[i][0]
            new_score = st.text_input(
                f"Score #{i+1}", value=score_act, key=f"cs_s_{i}",
            )
        with c2:
            new_cote = st.number_input(
                "Cote", min_value=1.01,
                value=float(st.session_state.cotes_cs[i][1]),
                step=0.1, key=f"cs_c_{i}",
            )
        st.session_state.cotes_cs[i] = (new_score, new_cote)


def page_7():
    home = st.session_state.home_team or "Domicile"
    away = st.session_state.away_team or "Extérieur"

    st.markdown(f'<div class="card"><p class="card-title">Analyse finale</p>'
                f'<p class="card-sub">{home} vs {away} — '
                f'{st.session_state.league}</p></div>',
                unsafe_allow_html=True)

    cotes_map = {
        "1": st.session_state.cotes_1x2["H"],
        "X": st.session_state.cotes_1x2["D"],
        "2": st.session_state.cotes_1x2["A"],
        "O0.5": st.session_state.cotes_ou["0.5"]["over"],
        "U0.5": st.session_state.cotes_ou["0.5"]["under"],
        "O1.5": st.session_state.cotes_ou["1.5"]["over"],
        "U1.5": st.session_state.cotes_ou["1.5"]["under"],
        "O2.5": st.session_state.cotes_ou["2.5"]["over"],
        "U2.5": st.session_state.cotes_ou["2.5"]["under"],
        "O3.5": st.session_state.cotes_ou["3.5"]["over"],
        "U3.5": st.session_state.cotes_ou["3.5"]["under"],
        "AH-0.5": st.session_state.cotes_ah["-0.5"]["home"],
        "AH+0.5": st.session_state.cotes_ah["-0.5"]["away"],
        "AH-1.5": st.session_state.cotes_ah["-1.5"]["home"],
        "AH+1.5": st.session_state.cotes_ah["-1.5"]["away"],
        "AH-2.5": st.session_state.cotes_ah["-2.5"]["home"],
        "AH+2.5": st.session_state.cotes_ah["-2.5"]["away"],
        "BTTS": st.session_state.cotes_btts["oui"],
    }

    cotes_ouv_map = None
    if st.session_state.clv_actif:
        cotes_ouv_map = {
            "1": st.session_state.cotes_1x2_ouv["H"],
            "X": st.session_state.cotes_1x2_ouv["D"],
            "2": st.session_state.cotes_1x2_ouv["A"],
            "O0.5": st.session_state.cotes_ou_ouv["0.5"]["over"],
            "U0.5": st.session_state.cotes_ou_ouv["0.5"]["under"],
            "O1.5": st.session_state.cotes_ou_ouv["1.5"]["over"],
            "U1.5": st.session_state.cotes_ou_ouv["1.5"]["under"],
            "O2.5": st.session_state.cotes_ou_ouv["2.5"]["over"],
            "U2.5": st.session_state.cotes_ou_ouv["2.5"]["under"],
            "O3.5": st.session_state.cotes_ou_ouv["3.5"]["over"],
            "U3.5": st.session_state.cotes_ou_ouv["3.5"]["under"],
            "AH-0.5": st.session_state.cotes_ah_ouv["-0.5"]["home"],
            "AH+0.5": st.session_state.cotes_ah_ouv["-0.5"]["away"],
            "AH-1.5": st.session_state.cotes_ah_ouv["-1.5"]["home"],
            "AH+1.5": st.session_state.cotes_ah_ouv["-1.5"]["away"],
            "AH-2.5": st.session_state.cotes_ah_ouv["-2.5"]["home"],
            "AH+2.5": st.session_state.cotes_ah_ouv["-2.5"]["away"],
            "BTTS": st.session_state.cotes_btts_ouv["oui"],
        }

    try:
        resultat = analyser_match(
            home_form=st.session_state.home_form,
            away_form=st.session_state.away_form,
            h2h=st.session_state.h2h,
            absences=st.session_state.abs_home,
            motivation=st.session_state.mot_home,
            cote_home=st.session_state.cotes_1x2["H"],
            cotes_map=cotes_map,
            cotes_cs=st.session_state.cotes_cs,
            cotes_ouverture_map=cotes_ouv_map,
            ligue=st.session_state.league,
            home_team=st.session_state.home_team,
            away_team=st.session_state.away_team,
        )
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        return

    variables = resultat["variables"]
    qualite = resultat["qualite"]
    resultats = resultat["resultats"]
    meilleur = resultat["meilleur"]
    scores_exacts = resultat.get("scores_exacts")
    combines = resultat.get("combines")
    regime = resultat.get("regime", "?")
    ligue = resultat.get("ligue", "?")

    regime_labels = {
        "A": "🅰️ Match fermé",
        "B": "🅱️ Match offensif",
        "C": "🅲 Favori dominant",
        "D": "🅳 Match équilibré",
        "E": "🅴 Forte incertitude",
        "?": "❓ Indéterminé",
    }
    st.markdown(f'<div class="regime-box">'
                f'<b style="color:#F8FAFC;">🎭 Régime :</b> '
                f'<b style="color:#F59E0B;">{regime_labels.get(regime, regime)}</b>'
                f' &nbsp;·&nbsp; <b style="color:#F8FAFC;">🏆 Ligue :</b> '
                f'<b style="color:#22C55E;">{ligue}</b>'
                f' &nbsp;·&nbsp; <b style="color:#F8FAFC;">🏅 ELO :</b> '
                f'<b style="color:#22C55E;">{variables.get("ELO", 0.5):.2f}</b>'
                f'</div>', unsafe_allow_html=True)

    st.markdown("### 📊 Qualité des données")
    c1, c2, c3 = st.columns(3)
    c1.metric("Volume", f"{qualite['volume']:.0%}")
    c2.metric("Fraîcheur", f"{1 - qualite['fraicheur']:.0%}")
    c3.metric("Complétude", f"{qualite['completude']:.0%}")

    st.markdown("### 🧮 Variables calculées (0-1, 0.5 = neutre)")
    cols = st.columns(4)
    for i, (k, v) in enumerate(variables.items()):
        with cols[i % 4]:
            st.metric(k, f"{v:.2f}")

    if scores_exacts and "scores_saisis" in scores_exacts:
        st.markdown("### 🎲 Scores exacts")
        c1, c2 = st.columns(2)
        c1.metric("λ domicile", f"{scores_exacts['lambdas']['home']:.2f}")
        c2.metric("λ extérieur", f"{scores_exacts['lambdas']['away']:.2f}")

        import pandas as pd
        cs_rows = []
        for s in scores_exacts["scores_saisis"]:
            edge = s["edge"]
            if edge >= 0.03:
                verdict = "🟢 Value"
            elif edge >= 0:
                verdict = "🟡 Neutre"
            else:
                verdict = "🔴 Négatif"
            cs_rows.append({
                "Score": s["score"],
                "P modèle": f"{s['proba']:.1%}",
                "Cote": f"{s['cote']:.2f}",
                "Edge": f"{edge:+.1%}",
                "EV": f"{s['ev']:+.1%}",
                "Verdict": verdict,
            })
        if cs_rows:
            st.dataframe(pd.DataFrame(cs_rows),
                         use_container_width=True, hide_index=True)

        st.markdown("**🏅 Top 5 scores selon le modèle**")
        top_rows = [{
            "Score": s,
            "Probabilité": f"{p:.1%}",
        } for s, p in scores_exacts.get("top_modele", [])]
        if top_rows:
            st.dataframe(pd.DataFrame(top_rows),
                         use_container_width=True, hide_index=True)

    st.markdown("### 🎯 Analyse multi-marchés (18 marchés)")
    import pandas as pd

    clv_actif = st.session_state.clv_actif
    rows = []
    for r in resultats:
        row = {
            "Marché": r.get("market", "-"),
            "P_CAL": f"{r.get('p_calibree', 0):.1%}" if "p_calibree" in r else "—",
            "ROB": f"{r.get('rob', 0):.2f}" if "rob" in r else "—",
            "EV": f"{r.get('ev', 0):+.1%}" if "ev" in r else "—",
        }
        if clv_actif:
            clv_data = r.get("clv_data")
            row["CLV"] = f"{clv_data['clv']:+.1%}" if clv_data else "—"
        if "edge_shin" in r:
            row["Edge Shin"] = f"{r['edge_shin']:+.1%}"
        meta_data = r.get("meta_data", {})
        if meta_data:
            row["Meta"] = f"{meta_data.get('score', 0):+.2f} (n={meta_data.get('n', 0)})"
        row["Chaos"] = f"{r.get('chaos', 0):.2f}" if "chaos" in r else "—"
        row["Score"] = f"{r.get('master_score', 0):.1f}" if "master_score" in r else "—"
        row["Verdict"] = r.get("verdict", "—")
        if r.get("piege"):
            row["Verdict"] = "🚨 PIÈGE"
        rows.append(row)

    st.dataframe(pd.DataFrame(rows),
                 use_container_width=True, hide_index=True)

    pieges = [r for r in resultats if r.get("piege")]
    if pieges:
        st.markdown("### 🚨 Alertes pièges")
        for p in pieges:
            raison = p.get("clv_data", {}).get("raison_piege", "Signal défavorable")
            st.markdown(f'<div class="alert-trap">'
                        f'<b>{p["market"]}</b> — {raison}'
                        f'</div>', unsafe_allow_html=True)

    if combines and isinstance(combines, list) and combines:
        st.markdown("### 🔗 Meilleurs combinés (2 marchés)")
        com_rows = []
        for c in combines:
            ev = c["ev"]
            if ev >= 0.30:
                verdict = "💎 EXCEPTIONNEL"
            elif ev >= 0.15:
                verdict = "🟢 FORT"
            elif ev >= 0.05:
                verdict = "🟡 INTÉRESSANT"
            else:
                verdict = "🟡 FAIBLE"
            com_rows.append({
                "Combiné": f"{c['marche_a']} + {c['marche_b']}",
                "P_A": f"{c['p_a']:.1%}",
                "P_B": f"{c['p_b']:.1%}",
                "ρ": f"{c['rho']:+.2f}",
                "P combinée": f"{c['p_combinee']:.1%}",
                "Cote comb.": f"{c['cote_combinee']:.2f}",
                "EV": f"{ev:+.1%}",
                "Verdict": verdict,
            })
        st.dataframe(pd.DataFrame(com_rows),
                     use_container_width=True, hide_index=True)

    if meilleur:
        st.markdown("### 🏆 Meilleur pari")
        extras = []
        if clv_actif and meilleur.get("clv_data"):
            clv_val = meilleur["clv_data"]["clv"]
            extras.append(f'CLV : <b style="color:#F59E0B;">{clv_val:+.1%}</b>')
        if "edge_shin" in meilleur:
            extras.append(f'Edge Shin : <b style="color:#22C55E;">{meilleur["edge_shin"]:+.1%}</b>')
        meta_d = meilleur.get("meta_data", {})
        if meta_d and meta_d.get("n", 0) > 0:
            extras.append(f'Meta : <b style="color:#22C55E;">{meta_d["score"]:+.2f}</b>')
        extras_html = (" · " + " · ".join(extras)) if extras else ""

        st.markdown(f"""
        <div class="result-card">
            <p style="font-size:18px;font-weight:700;color:#F8FAFC;margin:0;">
                🎯 {meilleur['market']} — Cote {meilleur['cote']:.2f}
            </p>
            <p style="margin-top:8px;color:#94A3B8;font-size:13px;">
                P calibrée : <b style="color:#22C55E;">{meilleur['p_calibree']:.1%}</b> ·
                ROB : <b style="color:#22C55E;">{meilleur['rob']:.2f}</b> ·
                EV : <b style="color:#22C55E;">{meilleur['ev']:+.1%}</b> ·
                Chaos : <b style="color:#F59E0B;">{meilleur['chaos']:.2f}</b>{extras_html}
            </p>
            <p style="margin-top:8px;">
                <span class="verdict-green">{meilleur['verdict']}</span>
                — Score Master <b>{meilleur['master_score']:.1f}/100</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("💾 Enregistrer ce pari", type="primary",
                         use_container_width=True):
                try:
                    pari_id = drcx.enregistrer_prediction(
                        market=meilleur["market"],
                        resultat_oracle=meilleur,
                        cote=meilleur["cote"],
                        regime=regime,
                        ligue=ligue,
                        variables=variables,
                    )
                    st.success(f"✅ Pari #{pari_id} enregistré ! "
                               f"Contexte : {regime} / {ligue}.")
                except Exception as e:
                    st.error(f"Erreur enregistrement : {e}")
        with c2:
            st.caption("Enregistre ce pari pour alimenter la calibration, "
                       "le Meta-Brain et GRADIENT-X.")
    else:
        st.error("🔴 NO BET — Aucun marché ne passe les filtres.")

    st.markdown("### 💾 Export")
    rapport = {
        "match": {
            "league": ligue,
            "date": str(st.session_state.match_date),
            "home": home, "away": away,
        },
        "regime": regime,
        "qualite": qualite,
        "variables": variables,
        "resultats": resultats,
        "meilleur": meilleur,
        "scores_exacts": scores_exacts,
        "combines": combines,
        "clv_actif": clv_actif,
    }
    st.download_button(
        "⬇️ Télécharger le rapport JSON",
        data=json.dumps(rapport, indent=2, ensure_ascii=False, default=str),
        file_name=f"oracle_edge_{home}_vs_{away}.json",
        mime="application/json",
            )


def page_8():
    st.markdown('<div class="card"><p class="card-title">Suivi des paris</p>'
                '<p class="card-sub">Marque chaque pari comme Gagné ou Perdu. '
                'Alimente calibration + Meta-Brain + Gradient.</p></div>',
                unsafe_allow_html=True)

    pending = calib.paris_en_attente()

    if not pending:
        st.info("📭 Aucun pari en attente.")
    else:
        st.markdown(f"### ⏳ {len(pending)} pari(s) en attente")
        for p in pending:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    ctx = f" · {p.get('regime', '?')} / {p.get('ligue', '?')}"
                    st.markdown(
                        f"**#{p['id']} — {p['market']}**  \n"
                        f"Cote **{p['cote']:.2f}** · "
                        f"P {p['p_calibree']:.1%} · "
                        f"Score {p['score_attribue']:.1f}"
                        f"<span style='color:#94A3B8;font-size:12px;'>{ctx}</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("✅ Gagné", key=f"w_{p['id']}",
                                 use_container_width=True):
                        calib.enregistrer_resultat(p["id"], True)
                        st.rerun()
                with c3:
                    if st.button("❌ Perdu", key=f"l_{p['id']}",
                                 use_container_width=True):
                        calib.enregistrer_resultat(p["id"], False)
                        st.rerun()
                with c4:
                    st.caption(f"ROB {p['rob']:.2f}")
                st.markdown("---")

    st.markdown("### 📊 Statistiques globales")
    stats = calib.get_stats()

    if stats.get("_global", {}).get("total", 0) > 0:
        g = stats["_global"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Taux de réussite", f"{g['taux_reussite']:.1%}")
        c2.metric("Paris résolus", f"{g['total']}")
        c3.metric("Paris gagnés", f"{g['gagnes']}")

        import pandas as pd
        rows = []
        for m, s in stats.items():
            if m == "_global":
                continue
            rows.append({
                "Marché": m,
                "Total": s["total"],
                "Gagnés": s["gagnes"],
                "Taux": f"{s['taux_reussite']:.1%}",
                "Cote moy.": f"{s['cote_moy']:.2f}",
            })
        if rows:
            st.dataframe(pd.DataFrame(rows),
                         use_container_width=True, hide_index=True)

        st.markdown("### 📜 Historique récent")
        recents = calib.paris_recents(10)
        if recents:
            hist_rows = [{
                "ID": p["id"],
                "Marché": p["market"],
                "Régime": p.get("regime", "?"),
                "Ligue": p.get("ligue", "?"),
                "Cote": f"{p['cote']:.2f}",
                "Résultat": "✅" if p["resultat"] else "❌",
            } for p in reversed(recents)]
            st.dataframe(pd.DataFrame(hist_rows),
                         use_container_width=True, hide_index=True)

    st.markdown("### 🧠 Meta-Brain — Performance par contexte")
    contextes = metabrain.stats_contexte()
    if not contextes:
        st.caption("Aucun contexte enregistré.")
    else:
        import pandas as pd
        ctx_rows = []
        for c in contextes:
            meta = metabrain.calculer_metascore(
                c["market"], c["regime"], c["ligue"]
            )
            ctx_rows.append({
                "Marché": c["market"],
                "Régime": c["regime"],
                "Ligue": c["ligue"],
                "n": c["n"],
                "Taux": f"{c['taux']:.0%}",
                "MetaScore": f"{meta['score']:+.2f}",
                "Verdict": meta["verdict"],
            })
        st.dataframe(pd.DataFrame(ctx_rows),
                     use_container_width=True, hide_index=True)

    st.markdown("### ⚙️ GRADIENT-X — Optimisation des poids")
    stats_g = gradient.stats_gradient()
    if stats_g:
        import pandas as pd
        g_rows = [{
            "Marché": s["market"],
            "Paris": s["n"],
            "Statut": s["statut"],
        } for s in stats_g]
        st.dataframe(pd.DataFrame(g_rows),
                     use_container_width=True, hide_index=True)

    actifs = [s["market"] for s in stats_g if s["actif"]]
    if actifs:
        with st.expander("🔍 Voir les poids appris vs initiaux"):
            marche_choisi = st.selectbox("Marché", actifs, key="select_ecarts")
            ecarts = gradient.ecart_vs_config(marche_choisi)
            if ecarts:
                import pandas as pd
                e_rows = [{
                    "Variable": e["variable"],
                    "Initial": f"{e['initial']:+.2f}",
                    "Appris": f"{e['appris']:+.2f}",
                    "Δ": f"{e['delta']:+.2f}",
                } for e in ecarts]
                st.dataframe(pd.DataFrame(e_rows),
                             use_container_width=True, hide_index=True)

    st.markdown("### 🏅 ELO — Classement des équipes")
    stats_e = elo.stats_elo()
    if not stats_e:
        st.caption("Aucune équipe dans le classement.")
    else:
        import pandas as pd
        e_rows = [{
            "Équipe": e["equipe"],
            "Rating": f"{e['rating']:.0f}",
        } for e in stats_e[:20]]
        st.dataframe(pd.DataFrame(e_rows),
                     use_container_width=True, hide_index=True)

    with st.expander("⚠️ Zone dangereuse"):
        st.caption("Efface les données d'apprentissage.")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🗑️ Reset calibration"):
                calib.reinitialiser()
                st.success("Calibration réinitialisée.")
                st.rerun()
        with c2:
            if st.button("🗑️ Reset Meta-Brain"):
                metabrain.reinitialiser()
                st.success("Meta-Brain réinitialisé.")
                st.rerun()
        with c3:
            if st.button("🗑️ Reset Gradient"):
                gradient.reinitialiser()
                st.success("Gradient réinitialisé.")
                st.rerun()
        if st.button("🗑️ Reset ELO"):
            elo.reinitialiser()
            st.success("ELO réinitialisé.")
            st.rerun()


hero()
stepper()

p = st.session_state.page
if p == 0: page_1()
elif p == 1: page_2()
elif p == 2: page_form(True)
elif p == 3: page_form(False)
elif p == 4: page_5()
elif p == 5: page_6()
elif p == 6: page_7()
elif p == 7: page_8()

nav()
