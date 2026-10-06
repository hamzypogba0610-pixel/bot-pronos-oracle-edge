"""
app.py — Interface Streamlit Oracle Edge.
Formulaire 8 pages + analyse 18 marchés + suivi des résultats.
"""

import json
from datetime import date

import streamlit as st

from config import LEAGUES
from analyse import analyser_match
import calibration as calib
import drcx


# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Oracle Edge",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================
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
.verdict-green { color: #22C55E; font-weight: 700; }
.verdict-yellow { color: #F59E0B; font-weight: 700; }
.verdict-red { color: #EF4444; font-weight: 700; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# ÉTAT SESSION
# ============================================================
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ============================================================
# HELPERS UI
# ============================================================
def hero():
    st.markdown("""
    <div class="hero">
        <div>
            <p class="hero-title">⚽ Oracle <span>Edge</span></p>
            <p class="hero-sub">DRC-X · MGE-R · Oracle Shield — 18 marchés</p>
        </div>
        <div class="hero-badge">v1.3</div>
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


# ============================================================
# PAGES 1 à 6
# ============================================================
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
                '<p class="card-sub">Saisis toutes les cotes disponibles.</p></div>',
                unsafe_allow_html=True)

    st.markdown("**1X2**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.cotes_1x2["H"] = st.number_input(
            "🏠 Dom", min_value=1.01, value=float(st.session_state.cotes_1x2["H"]),
            step=0.01, key="c_H",
        )
    with c2:
        st.session_state.cotes_1x2["D"] = st.number_input(
            "Nul", min_value=1.01, value=float(st.session_state.cotes_1x2["D"]),
            step=0.01, key="c_D",
        )
    with c3:
        st.session_state.cotes_1x2["A"] = st.number_input(
            "✈️ Ext", min_value=1.01, value=float(st.session_state.cotes_1x2["A"]),
            step=0.01, key="c_A",
        )

    st.markdown("**Over / Under**")
    for l in OU_LIGNES:
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

    st.markdown("**BTTS**")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.cotes_btts["oui"] = st.number_input(
            "Oui", min_value=1.01, value=float(st.session_state.cotes_btts["oui"]),
            step=0.01, key="c_btts_oui",
        )
    with c2:
        st.session_state.cotes_btts["non"] = st.number_input(
            "Non", min_value=1.01, value=float(st.session_state.cotes_btts["non"]),
            step=0.01, key="c_btts_non",
        )

    st.markdown("**Handicaps asiatiques**")
    for ligne in ["-0.5", "-1.5", "-2.5"]:
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

    st.markdown("**Top 5 scores exacts**")
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


# ============================================================
# PAGE 7 — ANALYSE
# ============================================================
def page_7():
    home = st.session_state.home_team or "Domicile"
    away = st.session_state.away_team or "Extérieur"

    st.markdown(f'<div class="card"><p class="card-title">Analyse finale</p>'
                f'<p class="card-sub">{home} vs {away} — '
                f'{st.session_state.league}</p></div>',
                unsafe_allow_html=True)

    # --- 18 marchés envoyés à l'analyse ---
    cotes_map = {
        # 1X2
        "1": st.session_state.cotes_1x2["H"],
        "X": st.session_state.cotes_1x2["D"],
        "2": st.session_state.cotes_1x2["A"],
        # Over / Under
        "O0.5": st.session_state.cotes_ou["0.5"]["over"],
        "U0.5": st.session_state.cotes_ou["0.5"]["under"],
        "O1.5": st.session_state.cotes_ou["1.5"]["over"],
        "U1.5": st.session_state.cotes_ou["1.5"]["under"],
        "O2.5": st.session_state.cotes_ou["2.5"]["over"],
        "U2.5": st.session_state.cotes_ou["2.5"]["under"],
        "O3.5": st.session_state.cotes_ou["3.5"]["over"],
        "U3.5": st.session_state.cotes_ou["3.5"]["under"],
        # Handicaps asiatiques
        "AH-0.5": st.session_state.cotes_ah["-0.5"]["home"],
        "AH+0.5": st.session_state.cotes_ah["-0.5"]["away"],
        "AH-1.5": st.session_state.cotes_ah["-1.5"]["home"],
        "AH+1.5": st.session_state.cotes_ah["-1.5"]["away"],
        "AH-2.5": st.session_state.cotes_ah["-2.5"]["home"],
        "AH+2.5": st.session_state.cotes_ah["-2.5"]["away"],
        # BTTS
        "BTTS": st.session_state.cotes_btts["oui"],
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
        )
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        return

    variables = resultat["variables"]
    qualite = resultat["qualite"]
    resultats = resultat["resultats"]
    meilleur = resultat["meilleur"]

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

    st.markdown("### 🎯 Analyse multi-marchés (18 marchés)")
    import pandas as pd
    df = pd.DataFrame([{
        "Marché": r.get("market", "-"),
        "P_CAL": f"{r.get('p_calibree', 0):.1%}" if "p_calibree" in r else "—",
        "ROB": f"{r.get('rob', 0):.2f}" if "rob" in r else "—",
        "EV": f"{r.get('ev', 0):+.1%}" if "ev" in r else "—",
        "Chaos": f"{r.get('chaos', 0):.2f}" if "chaos" in r else "—",
        "Score": f"{r.get('master_score', 0):.1f}" if "master_score" in r else "—",
        "Verdict": r.get("verdict", "—"),
    } for r in resultats])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if meilleur:
        st.markdown("### 🏆 Meilleur pari")
        st.markdown(f"""
        <div class="result-card">
            <p style="font-size:18px;font-weight:700;color:#F8FAFC;margin:0;">
                🎯 {meilleur['market']} — Cote {meilleur['cote']:.2f}
            </p>
            <p style="margin-top:8px;color:#94A3B8;font-size:13px;">
                P calibrée : <b style="color:#22C55E;">{meilleur['p_calibree']:.1%}</b> ·
                ROB : <b style="color:#22C55E;">{meilleur['rob']:.2f}</b> ·
                EV : <b style="color:#22C55E;">{meilleur['ev']:+.1%}</b> ·
                Chaos : <b style="color:#F59E0B;">{meilleur['chaos']:.2f}</b>
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
                    )
                    st.success(f"✅ Pari #{pari_id} enregistré ! "
                               f"Va sur la page **Résultats** pour le suivre.")
                except Exception as e:
                    st.error(f"Erreur enregistrement : {e}")
        with c2:
            st.caption("Enregistre ce pari pour suivre son résultat réel "
                       "et améliorer la calibration du bot.")
    else:
        st.error("🔴 NO BET — Aucun marché ne passe les filtres.")

    st.markdown("### 💾 Export")
    rapport = {
        "match": {
            "league": st.session_state.league,
            "date": str(st.session_state.match_date),
            "home": home, "away": away,
        },
        "qualite": qualite,
        "variables": variables,
        "resultats": resultats,
        "meilleur": meilleur,
    }
    st.download_button(
        "⬇️ Télécharger le rapport JSON",
        data=json.dumps(rapport, indent=2, ensure_ascii=False, default=str),
        file_name=f"oracle_edge_{home}_vs_{away}.json",
        mime="application/json",
    )


# ============================================================
# PAGE 8 — RÉSULTATS
# ============================================================
def page_8():
    st.markdown('<div class="card"><p class="card-title">Suivi des paris</p>'
                '<p class="card-sub">Marque chaque pari comme Gagné ou Perdu. '
                'Le bot apprend automatiquement.</p></div>',
                unsafe_allow_html=True)

    pending = calib.paris_en_attente()

    if not pending:
        st.info("📭 Aucun pari en attente. Enregistre un pari depuis la page Analyse.")
    else:
        st.markdown(f"### ⏳ {len(pending)} pari(s) en attente")
        for p in pending:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.markdown(
                        f"**#{p['id']} — {p['market']}**  \n"
                        f"Cote **{p['cote']:.2f}** · "
                        f"P {p['p_calibree']:.1%} · "
                        f"Score {p['score_attribue']:.1f}"
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
                "Cote": f"{p['cote']:.2f}",
                "P": f"{p['p_calibree']:.1%}",
                "Résultat": "✅" if p["resultat"] else "❌",
            } for p in reversed(recents)]
            st.dataframe(pd.DataFrame(hist_rows),
                         use_container_width=True, hide_index=True)
    else:
        st.caption("Aucun pari résolu pour l'instant. "
                   "Les stats apparaîtront après tes premiers résultats.")

    with st.expander("⚠️ Zone dangereuse"):
        st.caption("Efface toute la calibration et l'historique.")
        if st.button("🗑️ Réinitialiser la calibration", type="secondary"):
            calib.reinitialiser()
            st.success("Calibration réinitialisée.")
            st.rerun()


# ============================================================
# ROUTAGE
# ============================================================
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
