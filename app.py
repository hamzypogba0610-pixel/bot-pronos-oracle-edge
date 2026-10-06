"""
app.py — Interface Streamlit Oracle Edge.
Formulaire 7 pages + analyse via DRC-X + MGE-R + Oracle Shield.
"""

import json
from datetime import date

import streamlit as st

from config import LEAGUES
from variables import calculer_variables
from drcx import calculer_proba
from mger import analyse_mger, matrice_dependance, classifier_dependance
from oracle import analyse_oracle


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
.stNumberInput label, .stTextArea label {
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
    "Contexte", "Cotes", "Analyse",
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
        "abs_home": 0, "abs_away": 0,
        "mot_home": 0.5, "mot_away": 0.5,
        "cotes_1x2": {"H": 2.00, "D": 3.50, "A": 3.50},
        "cotes_ou": {str(l): {"over": 1.90, "under": 1.90} for l in OU_LIGNES},
        "cotes_btts": {"oui": 1.85, "non": 1.85},
        "cotes_ah": {"-0.5": {"home": 1.90, "away": 1.90},
                     "-1.5": {"home": 3.00, "away": 1.40},
                     "-2.5": {"home": 6.00, "away": 1.12}},
        "cotes_cs": [("2-1", 7.50), ("1-1", 6.50), ("2-0", 9.00),
                     ("1-0", 8.50), ("1-2", 8.00)],
        "analyse_done": False,
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
            <p class="hero-sub">DRC-X · MGE-R · Oracle Shield — 5 championnats</p>
        </div>
        <div class="hero-badge">v1.0</div>
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


def nav():
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.session_state.page > 0:
            if st.button("← Précédent", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
    with c3:
        if st.session_state.page < len(PAGES) - 1:
            label = "Suivant →" if st.session_state.page < len(PAGES) - 2 else "Analyser 🚀"
            if st.button(label, use_container_width=True, type="primary"):
                st.session_state.page += 1
                st.rerun()


# ============================================================
# PAGES
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
    """Page 3 (dom) ou 4 (ext) — même structure."""
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
        c1.markdown(f"Arsenal {ligne}")
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
def extraire_stats_form(form):
    """Retourne (buts_marques, buts_encaisses, xg_moy, xga_moy, tirs_cadres_moy)."""
    buts_pour, buts_contre = [], []
    xgs, xgas, tcs = [], [], []
    for m in form:
        s = m.get("score", "")
        if "-" in s:
            try:
                a, b = s.split("-")
                buts_pour.append(int(a))
                buts_contre.append(int(b))
            except ValueError:
                pass
        xgs.append(m.get("xg", 0.0))
        xgas.append(m.get("xga", 0.0))
        tcs.append(m.get("tirs_cadres", 0))

    def moy(l):
        return sum(l) / len(l) if l else 0.0

    return moy(buts_pour), moy(buts_contre), moy(xgs), moy(xgas), moy(tcs)


def page_7():
    home = st.session_state.home_team or "Domicile"
    away = st.session_state.away_team or "Extérieur"

    st.markdown(f'<div class="card"><p class="card-title">Analyse finale</p>'
                f'<p class="card-sub">{home} vs {away} — '
                f'{st.session_state.league}</p></div>',
                unsafe_allow_html=True)

    # --- Extraction des stats ---
    bm_h, bc_h, xg_h, xga_h, tc_h = extraire_stats_form(st.session_state.home_form)
    bm_a, bc_a, xg_a, xga_a, tc_a = extraire_stats_form(st.session_state.away_form)

    # --- Construction du dict pour calculer_variables ---
    donnees_home = {
        "form_resultats": [3, 3, 1, 3, 3],  # à améliorer plus tard
        "form_qualite": [0.5] * 5,
        "buts": bm_h, "xg": xg_h, "tirs_cadres": tc_h,
        "buts_encaisses": bc_h, "xga": xga_h,
        "tirs_cadres_conc": tc_a or 4,
        "xga_adversaire": xga_a,
        "perf_dom": 0.6, "perf_ext": 0.5,
        "variance_buts": 1.0,
        "impacts_absences": [st.session_state.abs_home],
        "h2h_resultats": [0.5] * 5,
        "h2h_ages": [100, 200, 300, 400, 500],
        "motivation": st.session_state.mot_home,
        "arrets": 5, "buts_evites": 0, "erreurs_gk": 0,
        "danger_off": 0.5, "solidite_def": 0.5,
        "pressing": 0.5, "possession": 0.5, "compacite": 0.5, "rythme": 0.5,
        "style_adv": {"pressing": 0.5, "possession": 0.5,
                      "compacite": 0.5, "rythme": 0.5},
        "proba_marche": 1 / st.session_state.cotes_1x2["H"],
    }

    try:
        variables = calculer_variables(donnees_home)
    except Exception as e:
        st.error(f"Erreur calcul variables : {e}")
        return

    # --- Affichage des variables ---
    st.markdown("### 🧮 Variables calculées")
    cols = st.columns(4)
    for i, (k, v) in enumerate(variables.items()):
        with cols[i % 4]:
            st.metric(k, f"{v:.2f}")

    # --- Analyse par marché ---
    st.markdown("### 🎯 Analyse multi-marchés")

    cotes_map = {
        "1": st.session_state.cotes_1x2["H"],
        "X": st.session_state.cotes_1x2["D"],
        "2": st.session_state.cotes_1x2["A"],
        "O2.5": st.session_state.cotes_ou["2.5"]["over"],
        "U2.5": st.session_state.cotes_ou["2.5"]["under"],
        "BTTS": st.session_state.cotes_btts["oui"],
    }

    resultats = []
    for market, cote in cotes_map.items():
        try:
            mger_res = analyse_mger(market, variables, cote=cote)
            oracle_res = analyse_oracle(variables, mger_res, cote)
            resultats.append(oracle_res)
        except Exception as e:
            st.warning(f"Marché {market} : {e}")

    # --- Tableau résultats ---
    if resultats:
        import pandas as pd
        df = pd.DataFrame([{
            "Marché": r["market"],
            "P_CAL": f"{r['p_calibree']:.1%}",
            "ROB": f"{r['rob']:.2f}",
            "EV": f"{r['ev']:+.1%}",
            "Chaos": f"{r['chaos']:.2f}",
            "Q": f"{r['quality']:.0f}",
            "Score": f"{r['master_score']:.1f}",
            "Verdict": r["verdict"],
        } for r in resultats])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # --- Meilleur pari ---
        valides = [r for r in resultats if r["accepte"]]
        if valides:
            best = max(valides, key=lambda x: x["master_score"])
            st.markdown("### 🏆 Meilleur pari")
            st.markdown(f"""
            <div class="result-card">
                <p style="font-size:18px;font-weight:700;color:#F8FAFC;margin:0;">
                    🎯 {best['market']} — Cote {cotes_map[best['market']]:.2f}
                </p>
                <p style="margin-top:8px;color:#94A3B8;font-size:13px;">
                    P calibrée : <b style="color:#22C55E;">{best['p_calibree']:.1%}</b> ·
                    ROB : <b style="color:#22C55E;">{best['rob']:.2f}</b> ·
                    EV : <b style="color:#22C55E;">{best['ev']:+.1%}</b> ·
                    ES : <b style="color:#22C55E;">{best.get('edge_stability', 0):.0%}</b>
                </p>
                <p style="margin-top:8px;">
                    <span class="verdict-green">{best['verdict']}</span>
                    — Score Master <b>{best['master_score']:.1f}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("🔴 NO BET — Aucun marché ne passe les filtres.")

        # --- Export JSON ---
        st.markdown("### 💾 Export")
        rapport = {
            "match": {
                "league": st.session_state.league,
                "date": str(st.session_state.match_date),
                "home": home, "away": away,
            },
            "variables": variables,
            "resultats": resultats,
        }
        st.download_button(
            "⬇️ Télécharger le rapport JSON",
            data=json.dumps(rapport, indent=2, ensure_ascii=False, default=str),
            file_name=f"oracle_edge_{home}_vs_{away}.json",
            mime="application/json",
        )


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

nav()
