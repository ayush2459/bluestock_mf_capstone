"""
Bluestock Fintech — Mutual Fund Analytics Platform
Redesigned UI/UX: dark luxury fintech aesthetic
Replace your existing scripts/streamlit_app.py with this file.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# GLOBAL CSS — dark luxury fintech theme
# ──────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root theme ── */
:root {
    --bg-base:      #07090f;
    --bg-card:      #0e1117;
    --bg-surface:   #141722;
    --bg-elevated:  #1a1f2e;
    --accent-gold:  #c9a84c;
    --accent-blue:  #3b82f6;
    --accent-green: #10b981;
    --accent-red:   #ef4444;
    --accent-amber: #f59e0b;
    --text-primary: #f0f2f8;
    --text-muted:   #8892a4;
    --text-subtle:  #505c72;
    --border:       rgba(255,255,255,0.07);
    --border-hover: rgba(201,168,76,0.3);
    --radius-sm:    6px;
    --radius-md:    12px;
    --radius-lg:    18px;
    --shadow-glow:  0 0 40px rgba(59,130,246,0.08);
}

/* ── App shell ── */
.stApp {
    background: var(--bg-base) !important;
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
}
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text-muted) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Sora', sans-serif !important;
    letter-spacing: -0.02em !important;
}
h1 { font-size: 1.9rem !important; font-weight: 700 !important; color: var(--text-primary) !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: var(--text-primary) !important; }
h3 { font-size: 1.05rem !important; font-weight: 500 !important; color: var(--text-muted) !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.1rem 1.3rem !important;
    transition: border-color 0.25s, transform 0.2s !important;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-hover) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}

/* ── Selectboxes & inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div:focus-within {
    border-color: var(--accent-gold) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] .stSlider > div > div > div > div {
    background: var(--accent-gold) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border-hover) !important;
    color: var(--accent-gold) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.45rem 1.2rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    background: rgba(201,168,76,0.08) !important;
    border-color: var(--accent-gold) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Sora', sans-serif !important;
    font-size: 0.83rem !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--bg-elevated) !important;
    color: var(--accent-gold) !important;
    border-color: var(--border-hover) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-muted) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Progress / spinner ── */
.stSpinner > div { border-top-color: var(--accent-gold) !important; }

/* ── Alerts ── */
.stAlert { border-radius: var(--radius-md) !important; font-family: 'Sora', sans-serif !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Plotly charts background ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Custom card component ── */
.bf-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    transition: border-color 0.25s, transform 0.2s;
}
.bf-card:hover { border-color: var(--border-hover); transform: translateY(-2px); }

.bf-section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-gold);
    margin-bottom: 0.4rem;
}

.bf-hero-stat {
    font-family: 'DM Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}
.bf-hero-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

.bf-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 20px;
    text-transform: uppercase;
}
.bf-badge-green { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.bf-badge-red   { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.bf-badge-gold  { background: rgba(201,168,76,0.15); color: #c9a84c; border: 1px solid rgba(201,168,76,0.3); }
.bf-badge-blue  { background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--text-subtle); border-radius: 10px; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY THEME — shared across all charts
# ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Sora, sans-serif", color="#8892a4", size=12),
    title_font=dict(family="Sora, sans-serif", color="#f0f2f8", size=14),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color="#505c72", size=11),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color="#505c72", size=11),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.07)",
        borderwidth=1,
        font=dict(color="#8892a4", size=11),
    ),
    margin=dict(l=12, r=12, t=40, b=12),
    hoverlabel=dict(
        bgcolor="#1a1f2e",
        bordercolor="rgba(201,168,76,0.3)",
        font=dict(family="Sora, sans-serif", color="#f0f2f8", size=12),
    ),
)

COLOR_PALETTE = [
    "#c9a84c", "#3b82f6", "#10b981", "#f59e0b",
    "#8b5cf6", "#ef4444", "#06b6d4", "#ec4899",
]

# ──────────────────────────────────────────────
# DB CONNECTION
# ──────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db", "bluestock_mf.db")

@st.cache_resource
def get_conn():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    return None

@st.cache_data(ttl=300)
def query(_conn, sql, params=()):
    try:
        return pd.read_sql_query(sql, _conn, params=params)
    except Exception:
        return pd.DataFrame()

# ──────────────────────────────────────────────
# DEMO DATA — used when DB not present
# ──────────────────────────────────────────────
@st.cache_data
def make_demo_nav(n_funds=10, n_days=500):
    np.random.seed(42)
    funds = [
        "Axis Bluechip Fund", "HDFC Top 100", "SBI Nifty Index",
        "Mirae Asset Emerging", "Parag Parikh Flexi Cap",
        "Kotak Small Cap", "DSP Midcap", "Nippon India Growth",
        "ICICI Pru Value Discovery", "UTI Nifty 50",
    ]
    dates = pd.date_range(end=datetime.today(), periods=n_days, freq="B")
    rows = []
    for f in funds[:n_funds]:
        nav = 50 + np.random.rand() * 150
        drift, vol = np.random.uniform(0.0003, 0.0010), np.random.uniform(0.008, 0.018)
        for d in dates:
            nav = nav * np.exp((drift - 0.5 * vol**2) + vol * np.random.randn())
            rows.append({"date": d, "scheme_name": f, "nav": round(nav, 4)})
    return pd.DataFrame(rows)

@st.cache_data
def make_demo_metrics():
    np.random.seed(7)
    funds = [
        "Axis Bluechip Fund", "HDFC Top 100", "SBI Nifty Index",
        "Mirae Asset Emerging", "Parag Parikh Flexi Cap",
        "Kotak Small Cap", "DSP Midcap", "Nippon India Growth",
        "ICICI Pru Value Discovery", "UTI Nifty 50",
    ]
    categories = ["Large Cap", "Large Cap", "Index", "Mid Cap", "Flexi Cap",
                  "Small Cap", "Mid Cap", "Growth", "Value", "Index"]
    data = {
        "scheme_name": funds, "category": categories,
        "cagr_1y":  np.random.uniform(-5, 32, 10).round(2),
        "cagr_3y":  np.random.uniform(8, 25, 10).round(2),
        "cagr_5y":  np.random.uniform(10, 22, 10).round(2),
        "sharpe":   np.random.uniform(0.5, 2.5, 10).round(3),
        "sortino":  np.random.uniform(0.6, 3.0, 10).round(3),
        "max_dd":   (-np.random.uniform(8, 35, 10)).round(2),
        "beta":     np.random.uniform(0.6, 1.4, 10).round(3),
        "alpha":    np.random.uniform(-2, 8, 10).round(3),
        "var_95":   (-np.random.uniform(1, 4, 10)).round(3),
        "aum_cr":   np.random.uniform(500, 25000, 10).round(0),
        "expense_ratio": np.random.uniform(0.1, 2.0, 10).round(2),
    }
    return pd.DataFrame(data)

@st.cache_data
def make_demo_sip():
    months = pd.date_range("2020-01-01", periods=60, freq="MS")
    return pd.DataFrame({
        "month": months,
        "sip_amount_cr": np.cumsum(np.random.uniform(10000, 15000, 60)).round(0),
        "sip_accounts": np.cumsum(np.random.randint(500000, 800000, 60)),
    })

@st.cache_data
def make_demo_aum():
    houses = ["SBI MF","HDFC MF","ICICI Pru","Nippon India","Kotak","Axis","Mirae","DSP"]
    qtrs = ["Q1 FY23","Q2 FY23","Q3 FY23","Q4 FY23","Q1 FY24","Q2 FY24","Q3 FY24","Q4 FY24"]
    rows = []
    for h in houses:
        base = np.random.uniform(50000, 700000)
        for q in qtrs:
            rows.append({"fund_house": h, "quarter": q,
                         "aum_cr": round(base * np.random.uniform(0.97, 1.08))})
            base = rows[-1]["aum_cr"]
    return pd.DataFrame(rows)

# ──────────────────────────────────────────────
# LOAD DATA (DB or demo)
# ──────────────────────────────────────────────
conn = get_conn()
USE_DB = conn is not None

if USE_DB:
    nav_df  = query(conn, "SELECT date, scheme_name, nav FROM fact_nav ORDER BY date")
    perf_df = query(conn, "SELECT * FROM fact_performance")
    sip_df  = query(conn, "SELECT * FROM fact_sip_industry ORDER BY month")
    aum_df  = query(conn, "SELECT * FROM fact_aum")
    if nav_df.empty:   USE_DB = False

if not USE_DB:
    nav_df  = make_demo_nav()
    perf_df = make_demo_metrics()
    sip_df  = make_demo_sip()
    aum_df  = make_demo_aum()

nav_df["date"] = pd.to_datetime(nav_df["date"])
fund_list = sorted(nav_df["scheme_name"].unique().tolist())

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 0 1.4rem; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom:1.2rem;">
        <div style="font-family:'Sora',sans-serif; font-size:1.15rem; font-weight:700;
                    color:#f0f2f8; letter-spacing:-0.02em;">
            <span style="color:#c9a84c;">⬡</span> Bluestock
        </div>
        <div style="font-size:0.72rem; color:#505c72; margin-top:3px; letter-spacing:0.06em; text-transform:uppercase;">
            MF Analytics Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Overview", "📊  NAV Explorer", "⚡  Performance", "🧪  Simulations", "💡  Recommender"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;color:#505c72;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;'>Filters</div>", unsafe_allow_html=True)

    selected_funds = st.multiselect(
        "Select Funds",
        fund_list,
        default=fund_list[:4],
        help="Pick funds to analyse",
    )
    if not selected_funds:
        selected_funds = fund_list[:4]

    date_range = st.select_slider(
        "Lookback Period",
        options=["1M","3M","6M","1Y","2Y","3Y","All"],
        value="1Y",
    )

    LOOKBACK = {"1M":30,"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":99999}
    cutoff = datetime.today() - timedelta(days=LOOKBACK[date_range])
    nav_filt = nav_df[
        (nav_df["scheme_name"].isin(selected_funds)) &
        (nav_df["date"] >= cutoff)
    ]

    if not USE_DB:
        st.markdown("""
        <div style="margin-top:1.5rem; padding:0.8rem 1rem;
                    background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2);
                    border-radius:8px; font-size:0.75rem; color:#f59e0b;">
            ⚠ Demo mode — connect your SQLite DB to load real data.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.68rem;color:#505c72;'>Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def make_fig(fig, height=380):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    return fig

def badge(text, kind="gold"):
    return f'<span class="bf-badge bf-badge-{kind}">{text}</span>'

def section_header(label, title, subtitle=""):
    sub = f'<p style="color:#505c72;font-size:0.82rem;margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1.2rem;">
        <div class="bf-section-label">{label}</div>
        <h2 style="margin:0 0 2px;">{title}</h2>
        {sub}
    </div>
    """, unsafe_allow_html=True)

def kpi_row(metrics_list):
    """metrics_list = [(label, value, delta, delta_type), ...]"""
    cols = st.columns(len(metrics_list))
    for col, (lbl, val, dlt, dlt_t) in zip(cols, metrics_list):
        with col:
            st.metric(lbl, val, dlt, delta_color=dlt_t)

# ──────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ──────────────────────────────────────────────
if page == "🏠  Overview":
    # Hero header
    st.markdown("""
    <div style="padding:2rem 0 1.5rem;">
        <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.14em;
                    text-transform:uppercase;color:#c9a84c;margin-bottom:0.5rem;">
            Bluestock Fintech · Capstone 2026
        </div>
        <h1 style="margin:0 0 0.4rem;font-size:2.4rem;">Mutual Fund Intelligence</h1>
        <p style="color:#8892a4;font-size:0.95rem;max-width:520px;line-height:1.6;">
            End-to-end analytics platform covering NAV tracking, risk metrics,
            Monte Carlo simulations, and AI-powered fund recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Industry KPIs
    total_aum = aum_df.groupby("fund_house")["aum_cr"].last().sum() if not aum_df.empty else 52_000_000
    total_sip = sip_df["sip_amount_cr"].iloc[-1] if not sip_df.empty else 19_000
    sip_delta = sip_df["sip_amount_cr"].pct_change().iloc[-1] * 100 if not sip_df.empty else 3.2

    kpi_row([
        ("Total AUM (₹ Cr)", f"₹{total_aum/1e5:.2f}L Cr", "+4.3%", "normal"),
        ("Monthly SIP Flows", f"₹{total_sip/100:.1f}K Cr", f"+{sip_delta:.1f}%", "normal"),
        ("Active Schemes", f"{len(fund_list)}", None, "off"),
        ("Data Points", f"{len(nav_df):,}", None, "off"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # NAV sparklines grid
    section_header("Portfolio Pulse", "Fund Performance at a Glance",
                   f"Showing {len(selected_funds)} selected funds · {date_range} lookback")

    n = len(selected_funds)
    cols = st.columns(min(n, 4))
    for i, fund in enumerate(selected_funds[:8]):
        col = cols[i % min(n, 4)]
        with col:
            fd = nav_df[nav_df["scheme_name"] == fund].sort_values("date").tail(365)
            if fd.empty: continue
            chg = (fd["nav"].iloc[-1] / fd["nav"].iloc[0] - 1) * 100
            color = "#10b981" if chg >= 0 else "#ef4444"
            fig = go.Figure(go.Scatter(
                x=fd["date"], y=fd["nav"],
                mode="lines",
                line=dict(color=color, width=1.5),
                fill="tozeroy",
                fillcolor=f"rgba{tuple(int(color.lstrip('#')[j:j+2],16) for j in (0,2,4))}".replace(")", ",0.06)"),
                hovertemplate="%{x|%d %b %Y}<br>₹%{y:.2f}<extra></extra>",
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT, height=100,
                margin=dict(l=0,r=0,t=0,b=0),
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                showlegend=False,
            )
            st.markdown(f"""
            <div class="bf-card" style="margin-bottom:0.8rem;padding:1rem 1.2rem 0.6rem;">
                <div style="font-size:0.72rem;color:#8892a4;font-weight:500;margin-bottom:2px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{fund}</div>
                <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:4px;">
                    <span style="font-family:'DM Mono',monospace;font-size:1.25rem;
                                 font-weight:700;color:#f0f2f8;">₹{fd['nav'].iloc[-1]:.2f}</span>
                    <span style="font-size:0.78rem;color:{color};font-weight:600;">
                        {'▲' if chg>=0 else '▼'} {abs(chg):.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Industry AUM chart + SIP trend
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Industry Landscape", "AUM & SIP Ecosystem")
    col_a, col_b = st.columns([3, 2])

    with col_a:
        if not aum_df.empty:
            latest_aum = aum_df.groupby("fund_house")["aum_cr"].last().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=latest_aum.values, y=latest_aum.index,
                orientation="h",
                marker=dict(
                    color=latest_aum.values,
                    colorscale=[[0,"#1a1f2e"],[0.5,"#3b82f6"],[1,"#c9a84c"]],
                    showscale=False,
                    line=dict(width=0),
                ),
                hovertemplate="%{y}<br>₹%{x:,.0f} Cr<extra></extra>",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=300,
                              title="AUM by Fund House (₹ Cr)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        if not sip_df.empty:
            fig2 = go.Figure(go.Scatter(
                x=sip_df["month"], y=sip_df["sip_amount_cr"],
                mode="lines", fill="tozeroy",
                line=dict(color="#c9a84c", width=2),
                fillcolor="rgba(201,168,76,0.07)",
                hovertemplate="%{x|%b %Y}<br>₹%{y:,.0f} Cr<extra></extra>",
            ))
            fig2.update_layout(**PLOTLY_LAYOUT, height=300,
                               title="Monthly SIP Inflows (₹ Cr)")
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ──────────────────────────────────────────────
# PAGE 2 — NAV EXPLORER
# ──────────────────────────────────────────────
elif page == "📊  NAV Explorer":
    section_header("NAV Explorer", "Historical Price & Return Analysis",
                   "Indexed performance, rolling returns, and correlation heatmap")

    tab1, tab2, tab3 = st.tabs(["  Indexed Returns  ", "  Rolling Returns  ", "  Correlation  "])

    with tab1:
        pivot = nav_filt.pivot_table(index="date", columns="scheme_name", values="nav")
        if pivot.empty:
            st.info("No data for selected filters.")
        else:
            indexed = (pivot / pivot.iloc[0]) * 100
            fig = go.Figure()
            for i, col in enumerate(indexed.columns):
                fig.add_trace(go.Scatter(
                    x=indexed.index, y=indexed[col],
                    name=col, mode="lines",
                    line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=1.8),
                    hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>",
                ))
            fig.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.15)")
            fig.update_layout(**PLOTLY_LAYOUT, height=460,
                              title=f"Indexed NAV Performance (Base = 100, {date_range})",
                              hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Return table
            st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
            summary = []
            for f in indexed.columns:
                s = indexed[f].dropna()
                total = s.iloc[-1] - 100 if len(s) > 1 else 0
                summary.append({
                    "Fund": f,
                    "Current NAV": f"₹{pivot[f].dropna().iloc[-1]:.2f}",
                    "Total Return %": f"{'+' if total>=0 else ''}{total:.1f}%",
                    "Peak NAV": f"₹{pivot[f].max():.2f}",
                    "Trough NAV": f"₹{pivot[f].min():.2f}",
                })
            st.dataframe(
                pd.DataFrame(summary).set_index("Fund"),
                use_container_width=True, height=220,
            )

    with tab2:
        col_f, col_w = st.columns([2,1])
        with col_f:
            roll_fund = st.selectbox("Fund", selected_funds, key="roll_fund")
        with col_w:
            window = st.select_slider("Window", [21,63,126,252], value=63, key="roll_w",
                                      format_func=lambda x: {21:"1M",63:"3M",126:"6M",252:"1Y"}[x])
        fd = nav_filt[nav_filt["scheme_name"]==roll_fund].sort_values("date")
        if not fd.empty:
            fd = fd.set_index("date")
            fd["roll_ret"] = fd["nav"].pct_change(window) * 100
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fd.index, y=fd["roll_ret"],
                mode="lines", name="Rolling Return",
                line=dict(width=1.5),
                fill="tozeroy",
                marker=dict(color=np.where(fd["roll_ret"]>=0,"#10b981","#ef4444")),
            ))
            pos = fd["roll_ret"].clip(lower=0)
            neg = fd["roll_ret"].clip(upper=0)
            fig.add_trace(go.Scatter(x=fd.index, y=pos, fill="tozeroy",
                                     fillcolor="rgba(16,185,129,0.12)",
                                     line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=fd.index, y=neg, fill="tozeroy",
                                     fillcolor="rgba(239,68,68,0.12)",
                                     line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_dash="dot")
            fig.update_layout(**PLOTLY_LAYOUT, height=400,
                              title=f"{roll_fund} — {window}-Day Rolling Returns (%)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab3:
        pivot2 = nav_filt.pivot_table(index="date", columns="scheme_name", values="nav")
        if pivot2.shape[1] < 2:
            st.info("Select at least 2 funds to see correlation.")
        else:
            rets = pivot2.pct_change().dropna()
            corr = rets.corr()
            names = [n[:22]+"…" if len(n)>22 else n for n in corr.columns]
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=names, y=names,
                colorscale=[[0,"#ef4444"],[0.5,"#1a1f2e"],[1,"#10b981"]],
                zmid=0, text=np.round(corr.values, 2), texttemplate="%{text}",
                hovertemplate="%{x} × %{y}<br>ρ = %{z:.3f}<extra></extra>",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=500,
                              title="Return Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ──────────────────────────────────────────────
# PAGE 3 — PERFORMANCE METRICS
# ──────────────────────────────────────────────
elif page == "⚡  Performance":
    section_header("Risk & Return Engine", "Performance Metrics Dashboard",
                   "Sharpe, Sortino, Max Drawdown, Alpha, Beta and CAGR comparison")

    if perf_df.empty:
        st.info("Performance metrics not available.")
    else:
        tab_r, tab_risk, tab_dd, tab_table = st.tabs(
            ["  CAGR Comparison  ", "  Risk Metrics  ", "  Drawdown  ", "  Full Table  "]
        )

        pf = perf_df[perf_df["scheme_name"].isin(selected_funds)] if "scheme_name" in perf_df.columns else perf_df
        if pf.empty: pf = perf_df

        with tab_r:
            if all(c in pf.columns for c in ["cagr_1y","cagr_3y","cagr_5y"]):
                fig = go.Figure()
                periods = ["cagr_1y","cagr_3y","cagr_5y"]
                labels  = ["1 Year","3 Year","5 Year"]
                for i, (per, lbl) in enumerate(zip(periods, labels)):
                    fig.add_trace(go.Bar(
                        name=lbl, x=pf["scheme_name"], y=pf[per],
                        marker_color=COLOR_PALETTE[i],
                        text=pf[per].round(1).astype(str)+"%",
                        textposition="outside",
                        hovertemplate=f"<b>%{{x}}</b><br>{lbl} CAGR: %{{y:.2f}}%<extra></extra>",
                    ))
                fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=440,
                                  title="CAGR Comparison (%)",
                                  xaxis_tickangle=-25)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with tab_risk:
            if "sharpe" in pf.columns and "sortino" in pf.columns:
                fig = make_subplots(rows=1, cols=2,
                                    subplot_titles=("Sharpe Ratio", "Sortino Ratio"))
                fig.add_trace(go.Bar(x=pf["scheme_name"], y=pf["sharpe"],
                                     marker_color="#c9a84c",
                                     hovertemplate="<b>%{x}</b><br>Sharpe: %{y:.3f}<extra></extra>"),
                              row=1, col=1)
                fig.add_trace(go.Bar(x=pf["scheme_name"], y=pf["sortino"],
                                     marker_color="#3b82f6",
                                     hovertemplate="<b>%{x}</b><br>Sortino: %{y:.3f}<extra></extra>"),
                              row=1, col=2)
                fig.update_layout(**PLOTLY_LAYOUT, height=400,
                                  showlegend=False,
                                  xaxis_tickangle=-25, xaxis2_tickangle=-25)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # Scatter: risk vs return
                if "cagr_3y" in pf.columns and "max_dd" in pf.columns:
                    fig2 = go.Figure(go.Scatter(
                        x=abs(pf["max_dd"]), y=pf["cagr_3y"],
                        mode="markers+text",
                        text=pf["scheme_name"].str[:15],
                        textposition="top center",
                        textfont=dict(size=9, color="#8892a4"),
                        marker=dict(
                            size=pf["sharpe"]*12 if "sharpe" in pf.columns else 12,
                            color=pf["sharpe"] if "sharpe" in pf.columns else "#c9a84c",
                            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                            showscale=True,
                            colorbar=dict(title="Sharpe", tickfont=dict(color="#8892a4")),
                            line=dict(width=0.5, color="rgba(255,255,255,0.2)"),
                        ),
                        hovertemplate="<b>%{text}</b><br>Max DD: -%{x:.1f}%<br>3Y CAGR: %{y:.1f}%<extra></extra>",
                    ))
                    fig2.update_layout(**PLOTLY_LAYOUT, height=380,
                                       title="Risk vs Return (bubble = Sharpe ratio)",
                                       xaxis_title="Max Drawdown (%)",
                                       yaxis_title="3Y CAGR (%)")
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        with tab_dd:
            for fund in selected_funds[:5]:
                fd = nav_filt[nav_filt["scheme_name"]==fund].sort_values("date")
                if fd.empty: continue
                prices = fd["nav"].values
                roll_max = np.maximum.accumulate(prices)
                dd = (prices - roll_max) / roll_max * 100
                fig = go.Figure(go.Scatter(
                    x=fd["date"], y=dd, mode="lines", fill="tozeroy",
                    name=fund,
                    line=dict(color="#ef4444", width=1.2),
                    fillcolor="rgba(239,68,68,0.08)",
                    hovertemplate=f"<b>{fund}</b><br>%{{x|%d %b %Y}}<br>DD: %{{y:.2f}}%<extra></extra>",
                ))
                fig.update_layout(**PLOTLY_LAYOUT, height=160, showlegend=False,
                                  title=fund, margin=dict(l=12,r=12,t=32,b=8))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with tab_table:
            display_cols = [c for c in ["scheme_name","category","cagr_1y","cagr_3y","cagr_5y",
                                         "sharpe","sortino","max_dd","beta","alpha","expense_ratio","aum_cr"]
                            if c in pf.columns]
            st.dataframe(pf[display_cols].set_index("scheme_name") if "scheme_name" in display_cols else pf,
                         use_container_width=True, height=360)


# ──────────────────────────────────────────────
# PAGE 4 — SIMULATIONS
# ──────────────────────────────────────────────
elif page == "🧪  Simulations":
    section_header("Quantitative Lab", "Monte Carlo & Efficient Frontier",
                   "Forward-looking probabilistic simulations and portfolio optimisation")

    tab_mc, tab_ef, tab_var = st.tabs(["  Monte Carlo  ", "  Efficient Frontier  ", "  VaR Analysis  "])

    with tab_mc:
        c1, c2, c3 = st.columns(3)
        with c1: mc_fund = st.selectbox("Fund", selected_funds, key="mc_f")
        with c2: n_sims  = st.select_slider("Simulations", [100,500,1000,2000,5000], value=500)
        with c3: horizon = st.select_slider("Horizon (days)", [30,90,180,252,504], value=252)

        fd = nav_df[nav_df["scheme_name"]==mc_fund].sort_values("date")
        if not fd.empty:
            rets = fd["nav"].pct_change().dropna()
            mu, sigma = rets.mean(), rets.std()
            last_nav = fd["nav"].iloc[-1]

            np.random.seed(0)
            sims = np.zeros((horizon, n_sims))
            for i in range(n_sims):
                daily = np.random.normal(mu, sigma, horizon)
                sims[:, i] = last_nav * np.cumprod(1 + daily)

            fig = go.Figure()
            # Fan chart — percentile bands
            p_levels = [(5,95,"rgba(201,168,76,0.04)"),
                        (15,85,"rgba(201,168,76,0.07)"),
                        (25,75,"rgba(201,168,76,0.11)")]
            x_axis = list(range(horizon))
            for lo, hi, col in p_levels:
                lower = np.percentile(sims, lo, axis=1)
                upper = np.percentile(sims, hi, axis=1)
                fig.add_trace(go.Scatter(
                    x=x_axis+x_axis[::-1], y=list(upper)+list(lower[::-1]),
                    fill="toself", fillcolor=col, line=dict(width=0),
                    showlegend=False, hoverinfo="skip",
                ))
            # Median + extremes
            median = np.percentile(sims, 50, axis=1)
            p10 = np.percentile(sims, 10, axis=1)
            p90 = np.percentile(sims, 90, axis=1)
            fig.add_trace(go.Scatter(x=x_axis, y=median, name="Median",
                                     line=dict(color="#c9a84c", width=2)))
            fig.add_trace(go.Scatter(x=x_axis, y=p10, name="10th %ile",
                                     line=dict(color="#ef4444", width=1.2, dash="dot")))
            fig.add_trace(go.Scatter(x=x_axis, y=p90, name="90th %ile",
                                     line=dict(color="#10b981", width=1.2, dash="dot")))
            # Sample paths
            idx = np.random.choice(n_sims, min(80, n_sims), replace=False)
            for i in idx:
                fig.add_trace(go.Scatter(
                    x=x_axis, y=sims[:, i],
                    mode="lines", line=dict(color="rgba(201,168,76,0.04)", width=0.8),
                    showlegend=False, hoverinfo="skip",
                ))
            fig.update_layout(**PLOTLY_LAYOUT, height=460,
                              title=f"Monte Carlo — {mc_fund} ({n_sims} paths, {horizon}d)",
                              yaxis_title="NAV (₹)", xaxis_title="Days Forward")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Stats
            final = sims[-1, :]
            kpi_row([
                ("Median Final NAV", f"₹{np.median(final):.2f}", None, "off"),
                ("Best Case (90th)", f"₹{np.percentile(final,90):.2f}", None, "off"),
                ("Worst Case (10th)", f"₹{np.percentile(final,10):.2f}", None, "off"),
                ("Prob. of Profit", f"{(final>last_nav).mean()*100:.1f}%", None, "normal"),
            ])

    with tab_ef:
        if len(selected_funds) >= 3:
            pivot_ef = nav_df[nav_df["scheme_name"].isin(selected_funds)]\
                        .pivot_table(index="date", columns="scheme_name", values="nav")\
                        .pct_change().dropna()

            n_ports = 4000
            np.random.seed(1)
            n_assets = pivot_ef.shape[1]
            mu_v = pivot_ef.mean().values * 252
            cov   = pivot_ef.cov().values * 252

            port_rets, port_vols, port_sharpe, port_weights = [], [], [], []
            for _ in range(n_ports):
                w = np.random.dirichlet(np.ones(n_assets))
                r = w @ mu_v
                v = np.sqrt(w @ cov @ w)
                port_rets.append(r)
                port_vols.append(v)
                port_sharpe.append(r / v if v > 0 else 0)
                port_weights.append(w)

            port_rets = np.array(port_rets) * 100
            port_vols = np.array(port_vols) * 100
            port_sharpe = np.array(port_sharpe)
            best = np.argmax(port_sharpe)

            fig = go.Figure(go.Scatter(
                x=port_vols, y=port_rets,
                mode="markers",
                marker=dict(
                    color=port_sharpe, colorscale="Viridis", size=3.5, opacity=0.7,
                    colorbar=dict(title="Sharpe", tickfont=dict(color="#8892a4")),
                ),
                hovertemplate="Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
                showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=[port_vols[best]], y=[port_rets[best]],
                mode="markers+text",
                text=["★ Max Sharpe"],
                textposition="top right",
                textfont=dict(color="#c9a84c", size=11),
                marker=dict(color="#c9a84c", size=14, symbol="star"),
                name="Max Sharpe",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=460,
                              title="Markowitz Efficient Frontier",
                              xaxis_title="Annualised Volatility (%)",
                              yaxis_title="Annualised Return (%)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Optimal weights
            opt_w = port_weights[best]
            wt_df = pd.DataFrame({"Fund": list(pivot_ef.columns), "Weight %": (opt_w*100).round(2)})
            wt_df = wt_df.sort_values("Weight %", ascending=False)
            fig2 = go.Figure(go.Pie(
                labels=wt_df["Fund"], values=wt_df["Weight %"],
                hole=0.65,
                marker=dict(colors=COLOR_PALETTE[:len(wt_df)],
                            line=dict(color="#07090f", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11, color="#f0f2f8"),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            ))
            fig2.update_layout(**PLOTLY_LAYOUT, height=320,
                               title="Max-Sharpe Optimal Portfolio Weights",
                               showlegend=False,
                               annotations=[dict(text=f"Sharpe<br>{port_sharpe[best]:.2f}",
                                                 x=0.5, y=0.5, showarrow=False,
                                                 font=dict(size=14, color="#c9a84c"))])
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Select at least 3 funds in the sidebar for Efficient Frontier.")

    with tab_var:
        var_fund = st.selectbox("Fund", selected_funds, key="var_f")
        fd = nav_filt[nav_filt["scheme_name"]==var_fund].sort_values("date")
        if not fd.empty:
            rets_v = fd["nav"].pct_change().dropna() * 100
            var_95 = np.percentile(rets_v, 5)
            var_99 = np.percentile(rets_v, 1)
            cvar_95 = rets_v[rets_v <= var_95].mean()

            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=rets_v, nbinsx=80,
                marker_color="#3b82f6",
                marker_line=dict(width=0),
                opacity=0.7,
                name="Daily Returns",
                hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>",
            ))
            for v, lbl, col in [(var_95,"VaR 95%","#f59e0b"),(var_99,"VaR 99%","#ef4444")]:
                fig.add_vline(x=v, line_dash="dot", line_color=col, line_width=1.5,
                              annotation_text=f" {lbl}: {v:.2f}%",
                              annotation_font=dict(color=col, size=11))
            fig.update_layout(**PLOTLY_LAYOUT, height=360,
                              title=f"{var_fund} — Daily Return Distribution",
                              xaxis_title="Daily Return (%)", yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            kpi_row([
                ("VaR 95% (1-day)", f"{var_95:.2f}%", None, "off"),
                ("VaR 99% (1-day)", f"{var_99:.2f}%", None, "off"),
                ("CVaR 95%",        f"{cvar_95:.2f}%", None, "off"),
                ("Annualised Vol",  f"{rets_v.std()*np.sqrt(252):.1f}%", None, "off"),
            ])


# ──────────────────────────────────────────────
# PAGE 5 — RECOMMENDER
# ──────────────────────────────────────────────
elif page == "💡  Recommender":
    section_header("Fund Recommender", "Personalised Fund Discovery",
                   "Set your preferences and find the best-fit schemes")

    with st.expander("⚙  Set Your Investment Profile", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            goal = st.selectbox("Investment Goal",
                                ["Wealth Creation","Capital Preservation","Regular Income","Tax Saving"])
            horizon_inv = st.select_slider("Investment Horizon",
                                           ["< 1 Year","1–3 Years","3–5 Years","5+ Years"], value="3–5 Years")
        with col2:
            risk_app = st.select_slider("Risk Appetite",
                                        ["Very Low","Low","Medium","High","Very High"], value="Medium")
            min_sharpe = st.slider("Min Sharpe Ratio", 0.0, 3.0, 0.8, 0.1)
        with col3:
            max_expense = st.slider("Max Expense Ratio (%)", 0.1, 2.5, 1.5, 0.05)
            pref_category = st.multiselect("Preferred Categories",
                                           ["Large Cap","Mid Cap","Small Cap","Flexi Cap","Index","Value","Growth","ELSS"],
                                           default=["Large Cap","Flexi Cap","Index"])

    if st.button("  🔍  Find Best Funds  "):
        risk_map = {"Very Low":0,"Low":0.25,"Medium":0.5,"High":0.75,"Very High":1.0}
        risk_score = risk_map[risk_app]

        df = perf_df.copy()
        if "sharpe" in df.columns:
            df = df[df["sharpe"] >= min_sharpe]
        if "expense_ratio" in df.columns:
            df = df[df["expense_ratio"] <= max_expense]
        if pref_category and "category" in df.columns:
            df = df[df["category"].isin(pref_category)]

        # Score
        score_weights = {"sharpe":0.3,"cagr_3y":0.25,"sortino":0.2,"max_dd":0.15,"alpha":0.1}
        df["score"] = 0.0
        for col_name, w in score_weights.items():
            if col_name in df.columns:
                s = df[col_name]
                if col_name == "max_dd":
                    s = -s
                norm = (s - s.min()) / (s.max() - s.min() + 1e-9)
                df["score"] += w * norm

        df = df.sort_values("score", ascending=False).head(6)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#f0f2f8;margin-bottom:1rem;'>Top Recommendations for <span style='color:#c9a84c;'>{goal}</span></h3>", unsafe_allow_html=True)

        cols = st.columns(3)
        rank_colors = ["#c9a84c","#8892a4","#b45309"]
        for i, (_, row) in enumerate(df.iterrows()):
            col = cols[i % 3]
            with col:
                rank = i + 1
                rc = rank_colors[min(i,2)]
                sharpe_v = f"{row['sharpe']:.2f}" if "sharpe" in row else "N/A"
                cagr_v   = f"{row['cagr_3y']:.1f}%" if "cagr_3y" in row else "N/A"
                dd_v     = f"{row['max_dd']:.1f}%" if "max_dd" in row else "N/A"
                cat      = row.get("category","—")
                st.markdown(f"""
                <div class="bf-card" style="margin-bottom:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.7rem;">
                        <span style="font-size:1.2rem;font-weight:700;color:{rc};">#{rank}</span>
                        <span class="bf-badge bf-badge-gold">{cat}</span>
                    </div>
                    <div style="font-weight:600;font-size:0.88rem;color:#f0f2f8;
                                line-height:1.35;margin-bottom:0.8rem;">{row['scheme_name']}</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;
                                        letter-spacing:0.08em;color:#505c72;">Sharpe</div>
                            <div style="font-family:'DM Mono',monospace;font-size:1rem;
                                        font-weight:600;color:#c9a84c;">{sharpe_v}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;
                                        letter-spacing:0.08em;color:#505c72;">3Y CAGR</div>
                            <div style="font-family:'DM Mono',monospace;font-size:1rem;
                                        font-weight:600;color:#10b981;">{cagr_v}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;
                                        letter-spacing:0.08em;color:#505c72;">Max DD</div>
                            <div style="font-family:'DM Mono',monospace;font-size:1rem;
                                        font-weight:600;color:#ef4444;">{dd_v}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;text-transform:uppercase;
                                        letter-spacing:0.08em;color:#505c72;">Score</div>
                            <div style="font-family:'DM Mono',monospace;font-size:1rem;
                                        font-weight:600;color:#f0f2f8;">{row['score']:.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if df.empty:
            st.warning("No funds match your filters. Try relaxing Sharpe / Expense Ratio.")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:0.5rem 0; color:#505c72; font-size:0.72rem;">
    <span>© 2026 <strong style="color:#8892a4;">Bluestock Fintech Pvt. Ltd.</strong> — For educational purposes only.</span>
    <span>All data sourced from AMFI India · mfapi.in · NSE/BSE</span>
</div>
""", unsafe_allow_html=True)
# Sat Jun  6 11:31:02 IST 2026
