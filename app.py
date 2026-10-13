# -*- coding: utf-8 -*-
"""
AéroLog — Suivi des heures de vol et des cycles des avions
Streamlit · pandas · matplotlib · seaborn  |  Thème light yellow animé
"""
import os
import hashlib
from datetime import date, datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------------- CONFIG
st.set_page_config(page_title="AéroLog | Heures de vol & cycles", page_icon="✈️",
                   layout="wide", initial_sidebar_state="expanded")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
COLS = ["id_vol", "date", "immatriculation", "type_avion", "origine",
        "destination", "heures_vol", "cycles", "remarque"]
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
PALETTE = ["#F59E0B", "#B45309", "#0F766E", "#EA580C", "#CA8A04", "#7C2D12", "#14B8A6", "#A16207"]


def _h(s):
    return hashlib.sha256(s.encode()).hexdigest()


USERS = {  # démo : à remplacer par une vraie authentification en production
    "admin": {"pwd": _h("aero2026"), "name": "Administrateur", "role": "Direction technique"},
    "technicien": {"pwd": _h("aero2026"), "name": "Technicien", "role": "Maintenance"},
    "planning": {"pwd": _h("aero2026"), "name": "Planning", "role": "Opérations"},
}

# Parc : type, cumul à l'origine (TSN/CSN au 01/01/2026) et compteurs depuis la dernière visite A
FLEET = {
    "CN-ROA": dict(type="Boeing 737-800", tsn=41250.0, csn=18420, since_h=210.0, since_c=95),
    "CN-ROB": dict(type="Boeing 737-800", tsn=38900.0, csn=17110, since_h=480.0, since_c=210),
    "CN-ROC": dict(type="Boeing 737-800", tsn=35120.0, csn=15800, since_h=60.0, since_c=30),
    "CN-ROD": dict(type="Boeing 737 MAX 8", tsn=9800.0, csn=4300, since_h=300.0, since_c=130),
    "CN-ROE": dict(type="Boeing 737 MAX 8", tsn=7600.0, csn=3350, since_h=520.0, since_c=240),
    "CN-ROF": dict(type="Boeing 787-9", tsn=22400.0, csn=3100, since_h=410.0, since_c=60),
    "CN-ROG": dict(type="Boeing 787-9", tsn=19800.0, csn=2750, since_h=150.0, since_c=22),
    "CN-ROH": dict(type="ATR 72-600", tsn=15200.0, csn=14100, since_h=330.0, since_c=300),
    "CN-ROI": dict(type="ATR 72-600", tsn=13700.0, csn=12800, since_h=120.0, since_c=110),
    "CN-ROJ": dict(type="Embraer 190", tsn=27300.0, csn=16500, since_h=440.0, since_c=350),
}
# Intervalle de visite A : (heures de vol, cycles)
INTERVALS = {"Boeing 737-800": (600, 450), "Boeing 737 MAX 8": (750, 500),
             "Boeing 787-9": (800, 150), "ATR 72-600": (500, 700), "Embraer 190": (600, 500)}
AIRPORTS = ["CMN", "RAK", "TNG", "AGA", "FEZ", "RBA", "OUD", "NDR", "ESU", "OZZ", "LAA",
            "CDG", "ORY", "MAD", "BCN", "LHR", "FCO", "AMS", "BRU", "JFK", "YUL", "DXB", "GRU", "IAD"]

LOGO = """<svg width="{s}" height="{s}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FBBF24"/>
<stop offset="1" stop-color="#D97706"/></linearGradient></defs>
<circle cx="32" cy="32" r="30" fill="url(#g)"/>
<circle cx="32" cy="32" r="24" fill="none" stroke="#FFFBEB" stroke-width="1.5" stroke-dasharray="3 4"/>
<path d="M50 30 L36 27 L26 12 L22 12 L28 28 L16 26 L12 20 L9 20 L12 32 L9 44 L12 44 L16 38 L28 36 L22 52 L26 52 L36 37 L50 34 Z"
 fill="#FFFBEB" transform="rotate(-20 32 32) translate(3 0)"/></svg>"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');
:root{--bg:#FFFBEB;--bg2:#FEF3C7;--card:#FFFFFF;--bd:#FDE68A;--acc:#F59E0B;--acc2:#D97706;--ink:#422006;--mut:#8A6D3B;
--ok:#15803D;--warn:#B45309;--bad:#B91C1C;}
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:var(--ink);}
h1,h2,h3,h4{font-family:'Poppins',sans-serif!important;color:var(--ink);}
.stApp{background:radial-gradient(900px 500px at 5% -10%,#FEF08A 0%,transparent 60%),
 radial-gradient(800px 500px at 105% 5%,#FDE68A 0%,transparent 55%),linear-gradient(160deg,#FFFDF2,#FFF8DC 60%,#FEF3C7);
 background-attachment:fixed;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#FEF3C7,#FDE68A55);border-right:1px solid var(--bd);}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes shift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes fly{0%{transform:translateX(-30px) translateY(6px) rotate(-6deg);opacity:0}
 20%{opacity:1}80%{opacity:1}100%{transform:translateX(30px) translateY(-6px) rotate(-6deg);opacity:0}}
@keyframes grow{from{width:0}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,.45)}50%{box-shadow:0 0 0 12px rgba(245,158,11,0)}}
.block-container{animation:fade .5s ease;padding-top:1.4rem;}
.title{font-family:'Poppins';font-weight:800;font-size:2rem;margin:0;
 background:linear-gradient(90deg,#B45309,#F59E0B,#CA8A04,#B45309);background-size:300% auto;
 -webkit-background-clip:text;background-clip:text;color:transparent;animation:shift 6s ease infinite;}
.subtitle{color:var(--mut);margin:0 0 1.1rem 0;}
.sec{font-family:'Poppins';font-weight:700;font-size:1.05rem;margin:.3rem 0 .7rem;padding-left:10px;border-left:4px solid var(--acc);}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:16px 16px 12px;animation:up .5s ease both;
 transition:transform .25s,box-shadow .25s,border-color .25s;box-shadow:0 2px 8px rgba(180,83,9,.06);}
.kpi:hover{transform:translateY(-5px);box-shadow:0 14px 28px rgba(217,119,6,.2);border-color:var(--acc);}
.kpi .ic{font-size:1.4rem}.kpi .lb{color:var(--mut);font-size:.74rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.kpi .vl{font-family:'Poppins';font-weight:700;font-size:1.6rem;color:var(--ink)}
.dl{display:inline-block;font-size:.76rem;font-weight:600;padding:2px 9px;border-radius:999px;margin-top:4px}
.up{background:#DCFCE7;color:#166534}.dn{background:#FEE2E2;color:#991B1B}.nt{background:#FEF3C7;color:#92400E}
.card{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:16px;margin-bottom:14px;animation:up .5s ease both;
 transition:transform .25s,box-shadow .25s;}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(217,119,6,.18);}
.bar{height:10px;border-radius:99px;background:#FEF3C7;overflow:hidden;margin:6px 0}
.bar>div{height:100%;border-radius:99px;animation:grow 1.1s ease;}
.badge{display:inline-block;padding:2px 10px;border-radius:99px;font-size:.72rem;font-weight:700}
.b-ok{background:#DCFCE7;color:#166534}.b-warn{background:#FEF3C7;color:#92400E}.b-bad{background:#FEE2E2;color:#991B1B}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{
 background:linear-gradient(90deg,#FBBF24,#F59E0B);color:#422006;border:none;border-radius:10px;font-weight:700;
 transition:transform .2s,box-shadow .2s,filter .2s;}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{
 transform:translateY(-2px);box-shadow:0 8px 18px rgba(217,119,6,.35);filter:brightness(1.05);color:#422006;}
[data-baseweb="select"]>div,.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea{
 background:#FFFFFF!important;border-radius:10px!important;border:1px solid var(--bd)!important;color:var(--ink)!important;}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid var(--bd)}
.stTabs [data-baseweb="tab"]{background:#FEF3C7;border-radius:10px 10px 0 0;color:var(--mut);padding:8px 16px;transition:all .2s}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#FBBF24,#F59E0B)!important;color:#422006!important;font-weight:700}
[data-testid="stSidebar"] [role="radiogroup"] label{background:#FFFBEB;border:1px solid var(--bd);border-radius:10px;
 padding:7px 12px;margin-bottom:6px;transition:all .2s;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{transform:translateX(5px);border-color:var(--acc);background:#FEF3C7}
[data-testid="stDataFrame"]{border:1px solid var(--bd);border-radius:14px;overflow:hidden;animation:fade .5s}
.login{max-width:430px;margin:3vh auto 0;background:#fff;border:1px solid var(--bd);border-radius:22px;padding:34px 32px 18px;
 box-shadow:0 24px 60px rgba(217,119,6,.18);animation:up .6s ease both;text-align:center}
.login .lg{display:inline-block;border-radius:50%;animation:pulse 2.4s infinite}
.login .plane{font-size:1.6rem;display:block;animation:fly 3.2s ease-in-out infinite;margin:6px 0 0}
.login h1{margin:4px 0 0;font-weight:800;font-size:1.8rem}
.login p{color:var(--mut);font-size:.9rem;margin:2px 0 8px}
.hint{text-align:center;color:var(--mut);font-size:.8rem;margin-top:10px;border-top:1px dashed var(--bd);padding-top:10px}
.foot{text-align:center;color:var(--mut);font-size:.78rem;margin-top:2rem;padding-top:.8rem;border-top:1px solid var(--bd)}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

plt.rcParams.update({
    "figure.facecolor": "#FFFFFF", "axes.facecolor": "#FFFDF5", "axes.edgecolor": "#FDE68A",
    "axes.labelcolor": "#422006", "axes.titlecolor": "#422006", "text.color": "#422006",
    "xtick.color": "#8A6D3B", "ytick.color": "#8A6D3B", "grid.color": "#FDE68A", "grid.linestyle": "--",
    "grid.alpha": .7, "font.size": 10, "axes.titleweight": "bold", "legend.frameon": False,
})
sns.set_palette(PALETTE)


# ---------------------------------------------------------------- DONNÉES
def load_df():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["remarque"] = df["remarque"].fillna("")
    return df


def save_df(df):
    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_PATH, index=False)


def fleet_status(df):
    tot = df.groupby("immatriculation").agg(h=("heures_vol", "sum"), c=("cycles", "sum"), der=("date", "max"))
    rows = []
    for reg, f in FLEET.items():
        h = float(tot["h"].get(reg, 0.0)); c = int(tot["c"].get(reg, 0))
        ih, ic = INTERVALS[f["type"]]
        rem_h = ih - (f["since_h"] + h) % ih
        rem_c = ic - (f["since_c"] + c) % ic
        pct = min(rem_h / ih, rem_c / ic) * 100
        statut = "Critique" if pct < 10 else ("À surveiller" if pct < 25 else "OK")
        rows.append(dict(immatriculation=reg, type_avion=f["type"], heures_total=f["tsn"] + h, cycles_total=f["csn"] + c,
                         heures_periode=h, cycles_periode=c, reste_h=rem_h, reste_c=rem_c, pct=pct, statut=statut,
                         derniere=tot["der"].get(reg, pd.NaT)))
    return pd.DataFrame(rows)


def fmt(x, d=0, suf=""):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + suf


def delta30(df, col):
    if df.empty:
        return None
    end = df["date"].max()
    cur = df[df["date"] > end - pd.Timedelta(days=30)][col].sum()
    prev = df[(df["date"] <= end - pd.Timedelta(days=30)) & (df["date"] > end - pd.Timedelta(days=60))][col].sum()
    return None if prev == 0 else (cur - prev) / prev * 100


def kpi(icon, label, value, delta=None, delay=0.0, note="vs 30 j préc."):
    d = ""
    if delta is not None:
        cls = "up" if delta >= 0 else "dn"
        d = f"<div class='dl {cls}'>{'▲' if delta >= 0 else '▼'} {abs(delta):.1f} % {note}</div>"
    st.markdown(f"<div class='kpi' style='animation-delay:{delay}s'><div class='ic'>{icon}</div>"
                f"<div class='lb'>{label}</div><div class='vl'>{value}</div>{d}</div>", unsafe_allow_html=True)


def header(title, sub):
    st.markdown(f"<div class='title'>{title}</div><div class='subtitle'>{sub}</div>", unsafe_allow_html=True)


def sec(t):
    st.markdown(f"<div class='sec'>{t}</div>", unsafe_allow_html=True)


def show(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def clean(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid, alpha=.6)


# ---------------------------------------------------------------- LOGIN
def login_page():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f"""<div class='login'><span class='lg'>{LOGO.format(s=76)}</span>
        <span class='plane'>✈️</span><h1>AéroLog</h1>
        <p>Suivi des heures de vol &amp; des cycles de la flotte</p></div>""", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Identifiant", placeholder="ex : admin")
            p = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            ok = st.form_submit_button("Se connecter →", width="stretch")
        if ok:
            user = USERS.get(u.strip().lower())
            if user and _h(p) == user["pwd"]:
                st.session_state.update(auth=True, user=user["name"], role=user["role"])
                st.rerun()
            st.error("Identifiant ou mot de passe incorrect.")
        st.markdown("<div class='hint'>Démo : <b>admin</b> / <b>aero2026</b> "
                    "(ou <b>technicien</b>, <b>planning</b>)</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------- SIDEBAR
PAGES = ["📊 Tableau de bord", "🛩️ État de la flotte", "➕ Nouvelle saisie", "🗂️ Données"]


def sidebar(df):
    with st.sidebar:
        st.markdown(f"<div style='display:flex;align-items:center;gap:10px'>{LOGO.format(s=44)}"
                    "<div><div style='font-family:Poppins;font-weight:800;font-size:1.25rem;line-height:1.1'>AéroLog</div>"
                    "<div style='color:#8A6D3B;font-size:.72rem'>Heures de vol &amp; cycles</div></div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='card' style='padding:8px 12px;margin:12px 0'><div style='font-size:.72rem;color:#8A6D3B'>"
                    f"Connecté</div><b>{st.session_state.user}</b><br><span class='badge b-warn'>{st.session_state.role}</span></div>",
                    unsafe_allow_html=True)
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.markdown("---")
        sec("🔎 Filtres")
        dmin, dmax = df["date"].min().date(), max(df["date"].max().date(), date.today())
        rng = st.date_input("Période", value=(df["date"].min().date(), df["date"].max().date()),
                            min_value=dmin, max_value=dmax)
        types = st.multiselect("Type d'avion", sorted(df["type_avion"].unique()))
        regs = st.multiselect("Immatriculation", sorted(FLEET))
        dests = st.multiselect("Destination", sorted(df["destination"].unique()))
        st.markdown("---")
        if st.button("🚪 Déconnexion", width="stretch"):
            st.session_state.clear()
            st.rerun()
    f = df.copy()
    if isinstance(rng, tuple) and len(rng) == 2:
        f = f[(f["date"].dt.date >= rng[0]) & (f["date"].dt.date <= rng[1])]
    if types:
        f = f[f["type_avion"].isin(types)]
    if regs:
        f = f[f["immatriculation"].isin(regs)]
    if dests:
        f = f[f["destination"].isin(dests)]
    return page, f


# ---------------------------------------------------------------- PAGES
def page_dashboard(f, full):
    header("📊 Tableau de bord", "Vue d'ensemble de l'activité de la flotte — mise à jour automatique après chaque saisie")
    if f.empty:
        st.info("Aucune donnée pour ces filtres. Élargissez la période ou réinitialisez les filtres.")
        return
    stt = fleet_status(full)
    stt = stt[stt["immatriculation"].isin(f["immatriculation"].unique())]
    h, c = f["heures_vol"].sum(), int(f["cycles"].sum())
    cols = st.columns(6)
    items = [("⏱️", "Heures de vol", fmt(h, 1, " h"), delta30(f, "heures_vol")),
             ("🔄", "Cycles", fmt(c), delta30(f, "cycles")),
             ("📋", "Journées d'exploitation", fmt(len(f)), delta30(f.assign(n=1), "n")),
             ("⚖️", "Heures / cycle", fmt(h / c if c else 0, 2, " h"), None),
             ("🛩️", "Avions actifs", f"{f['immatriculation'].nunique()} / {len(FLEET)}", None),
             ("🛠️", "Visites à surveiller", fmt((stt["statut"] != "OK").sum()), None)]
    for i, (col, it) in enumerate(zip(cols, items)):
        with col:
            kpi(*it[:3], delta=it[3], delay=i * 0.07)
    st.markdown("<br>", unsafe_allow_html=True)

    f = f.assign(mois=f["date"].dt.to_period("M").dt.to_timestamp())
    t1, t2, t3 = st.tabs(["Évolution & répartition", "Par avion", "Intensité & routes"])
    with t1:
        a, b = st.columns([1.7, 1])
        with a:
            sec("Heures de vol et cycles par mois")
            g = f.groupby("mois").agg(h=("heures_vol", "sum"), c=("cycles", "sum")).reset_index()
            lab = [MOIS[m.month - 1] for m in g["mois"]]
            fig, ax = plt.subplots(figsize=(9, 4.2))
            ax.bar(lab, g["h"], color="#FBBF24", edgecolor="#D97706", label="Heures")
            ax.set_ylabel("Heures de vol"); clean(ax)
            ax2 = ax.twinx()
            ax2.plot(lab, g["c"], color="#0F766E", marker="o", lw=2.4, label="Cycles")
            ax2.set_ylabel("Cycles"); ax2.spines[["top"]].set_visible(False)
            fig.legend(loc="upper left", bbox_to_anchor=(0.08, 0.95), ncol=2)
            fig.tight_layout(); show(fig)
        with b:
            sec("Heures par type d'avion")
            g = f.groupby("type_avion")["heures_vol"].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(5, 4.2))
            w, _ = ax.pie(g.values, colors=PALETTE, startangle=90, wedgeprops=dict(width=.42, edgecolor="white", linewidth=2))
            ax.legend(w, g.index, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=8)
            ax.text(0, 0, fmt(g.sum(), 0, "\nheures"), ha="center", va="center", fontweight="bold")
            fig.tight_layout(); show(fig)
    with t2:
        a, b = st.columns(2)
        g = f.groupby("immatriculation").agg(h=("heures_vol", "sum"), c=("cycles", "sum")).reset_index()
        with a:
            sec("Heures de vol par avion")
            s = g.sort_values("h")
            fig, ax = plt.subplots(figsize=(7, 4.6))
            ax.barh(s["immatriculation"], s["h"], color="#F59E0B")
            for y, v in enumerate(s["h"]):
                ax.text(v, y, f" {v:,.0f}".replace(",", " "), va="center", fontsize=8)
            clean(ax, "x"); ax.set_xlabel("Heures"); fig.tight_layout(); show(fig)
        with b:
            sec("Heures par cycle (durée moyenne d'un vol)")
            g["r"] = g["h"] / g["c"]
            s = g.sort_values("r")
            fig, ax = plt.subplots(figsize=(7, 4.6))
            ax.barh(s["immatriculation"], s["r"], color="#0F766E")
            clean(ax, "x"); ax.set_xlabel("Heures / cycle"); fig.tight_layout(); show(fig)
        sec("Corrélation heures ↔ cycles")
        fig, ax = plt.subplots(figsize=(10, 3.8))
        tp = f.groupby("immatriculation")["type_avion"].first()
        g["type"] = g["immatriculation"].map(tp)
        sns.scatterplot(data=g, x="c", y="h", hue="type", s=170, edgecolor="white", ax=ax)
        for _, r in g.iterrows():
            ax.annotate(r["immatriculation"], (r["c"], r["h"]), xytext=(6, 6), textcoords="offset points", fontsize=8)
        ax.set_xlabel("Cycles"); ax.set_ylabel("Heures"); clean(ax, "both"); fig.tight_layout(); show(fig)
    with t3:
        sec("Carte de chaleur : heures de vol par avion et par mois")
        pv = f.pivot_table(index="immatriculation", columns="mois", values="heures_vol", aggfunc="sum", fill_value=0)
        pv.columns = [MOIS[m.month - 1] for m in pv.columns]
        fig, ax = plt.subplots(figsize=(11, 4.2))
        sns.heatmap(pv, cmap="YlOrBr", annot=True, fmt=".0f", linewidths=.6, linecolor="white",
                    cbar_kws={"shrink": .8, "label": "Heures"}, ax=ax)
        ax.set_xlabel(""); ax.set_ylabel(""); fig.tight_layout(); show(fig)
        sec("Destinations les plus desservies (cycles)")
        g = f.groupby("destination")["cycles"].sum().sort_values(ascending=False).head(10).sort_values()
        fig, ax = plt.subplots(figsize=(10, 3.8))
        ax.barh(g.index, g.values, color="#EA580C"); clean(ax, "x"); ax.set_xlabel("Cycles")
        fig.tight_layout(); show(fig)


def page_flotte(full):
    header("🛩️ État de la flotte", "Cumuls (TSN / CSN) et échéance de la prochaine visite A pour chaque avion")
    st_ = fleet_status(full)
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("✅", "Avions conformes", fmt((st_["statut"] == "OK").sum()))
    with c2:
        kpi("⚠️", "À surveiller", fmt((st_["statut"] == "À surveiller").sum()), delay=.08)
    with c3:
        kpi("🚨", "Visites critiques", fmt((st_["statut"] == "Critique").sum()), delay=.16)
    st.markdown("<br>", unsafe_allow_html=True)
    colors = {"OK": ("#16A34A", "b-ok"), "À surveiller": ("#F59E0B", "b-warn"), "Critique": ("#DC2626", "b-bad")}
    cols = st.columns(3)
    for i, r in st_.sort_values("pct").reset_index(drop=True).iterrows():
        col, cls = colors[r["statut"]]
        used = 100 - r["pct"]
        with cols[i % 3]:
            st.markdown(f"""<div class='card' style='animation-delay:{i*0.05}s'>
            <div style='display:flex;justify-content:space-between;align-items:center'>
              <div><b style='font-family:Poppins;font-size:1.1rem'>{r['immatriculation']}</b>
              <div style='color:#8A6D3B;font-size:.8rem'>{r['type_avion']}</div></div>
              <span class='badge {cls}'>{r['statut']}</span></div>
            <div class='bar'><div style='width:{used:.0f}%;background:{col}'></div></div>
            <div style='font-size:.8rem;color:#8A6D3B'>Avant visite A : <b style='color:#422006'>{fmt(r['reste_h'],0)} h</b>
              · <b style='color:#422006'>{fmt(r['reste_c'])} cycles</b></div>
            <div style='display:flex;justify-content:space-between;margin-top:8px;font-size:.85rem'>
              <span>TSN <b>{fmt(r['heures_total'],0)} h</b></span><span>CSN <b>{fmt(r['cycles_total'])}</b></span></div>
            </div>""", unsafe_allow_html=True)
    sec("Tableau récapitulatif")
    show_df = st_.rename(columns={"immatriculation": "Immat.", "type_avion": "Type", "heures_total": "TSN (h)",
                                  "cycles_total": "CSN", "reste_h": "Reste visite (h)", "reste_c": "Reste visite (cycles)",
                                  "statut": "Statut", "derniere": "Dernier vol"})
    show_df = show_df[["Immat.", "Type", "TSN (h)", "CSN", "Reste visite (h)", "Reste visite (cycles)", "Statut", "Dernier vol"]]
    show_df = show_df.round({"TSN (h)": 1, "Reste visite (h)": 1})
    st.dataframe(show_df, width="stretch", hide_index=True)
    st.caption("TSN/CSN = heures / cycles depuis la mise en service (cumul d'origine + saisies). "
               "Seuils : critique < 10 % de marge, à surveiller < 25 %.")


def page_saisie(full):
    header("➕ Nouvelle saisie", "Enregistrez une journée d'exploitation : le tableau de bord se met à jour immédiatement")
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    a, b = st.columns([1, 1.15])
    with a:
        sec("Formulaire")
        with st.form("saisie", clear_on_submit=True):
            reg = st.selectbox("Immatriculation", list(FLEET))
            d = st.date_input("Date", value=date.today(), max_value=date.today())
            o1, o2 = st.columns(2)
            org = o1.selectbox("Origine", AIRPORTS, index=0)
            dst = o2.selectbox("Destination", AIRPORTS, index=1)
            h1, h2 = st.columns(2)
            hv = h1.number_input("Heures de vol", min_value=0.1, max_value=24.0, value=2.0, step=0.1)
            cy = h2.number_input("Cycles (atterrissages)", min_value=1, max_value=10, value=1, step=1)
            rem = st.text_area("Remarque (facultatif)", height=70)
            ok = st.form_submit_button("💾 Enregistrer la saisie", width="stretch")
        if ok:
            if org == dst:
                st.error("L'origine et la destination doivent être différentes.")
            else:
                nid = f"L{int(full['id_vol'].str[1:].astype(int).max()) + 1:05d}"
                row = pd.DataFrame([[nid, pd.Timestamp(d), reg, FLEET[reg]["type"], org, dst, round(hv, 1), int(cy), rem.strip()]],
                                   columns=COLS)
                st.session_state.df = pd.concat([full, row], ignore_index=True)
                save_df(st.session_state.df)
                s = fleet_status(st.session_state.df).set_index("immatriculation").loc[reg]
                st.session_state.flash = (f"Saisie {nid} enregistrée pour {reg} : +{hv:.1f} h, +{cy} cycle(s). "
                                          f"Nouveau cumul : {fmt(s['heures_total'], 1)} h / {fmt(s['cycles_total'])} cycles.")
                st.rerun()
    with b:
        sec("Dernières saisies")
        last = full.sort_values(["date", "id_vol"], ascending=False).head(12)
        st.dataframe(last.drop(columns=["type_avion"]).assign(date=last["date"].dt.strftime("%d/%m/%Y")),
                     width="stretch", hide_index=True, height=400)
        with st.expander("🗑️ Supprimer une saisie"):
            sid = st.selectbox("Identifiant à supprimer", last["id_vol"].tolist())
            if st.button("Supprimer définitivement"):
                st.session_state.df = full[full["id_vol"] != sid].reset_index(drop=True)
                save_df(st.session_state.df)
                st.session_state.flash = f"Saisie {sid} supprimée."
                st.rerun()


def page_donnees(f):
    header("🗂️ Données", "Journal complet des vols filtrés, recherche et export")
    q = st.text_input("🔍 Rechercher (immatriculation, destination, remarque…)")
    v = f
    if q:
        v = f[f.astype(str).apply(lambda c: c.str.contains(q, case=False, na=False)).any(axis=1)]
    st.caption(f"{len(v):,} saisies · {v['heures_vol'].sum():,.1f} h · {int(v['cycles'].sum()):,} cycles".replace(",", " "))
    st.dataframe(v.sort_values("date", ascending=False).assign(date=lambda x: x["date"].dt.strftime("%d/%m/%Y")),
                 width="stretch", hide_index=True, height=520)
    st.download_button("⬇️ Télécharger en CSV", v.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"aerolog_{datetime.now():%Y%m%d_%H%M}.csv", mime="text/csv")


# ---------------------------------------------------------------- MAIN
def main():
    if not st.session_state.get("auth"):
        login_page()
        return
    if "df" not in st.session_state:
        st.session_state.df = load_df()
    full = st.session_state.df
    page, f = sidebar(full)
    if page == PAGES[0]:
        page_dashboard(f, full)
    elif page == PAGES[1]:
        page_flotte(full)
    elif page == PAGES[2]:
        page_saisie(full)
    else:
        page_donnees(f)
    st.markdown(f"<div class='foot'>AéroLog · Suivi heures de vol &amp; cycles · Dernière donnée : "
                f"{full['date'].max():%d/%m/%Y} · © {datetime.now().year}</div>", unsafe_allow_html=True)


main()
