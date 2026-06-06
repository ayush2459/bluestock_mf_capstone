"""
Bluestock Fintech — Mutual Fund Analytics Platform
Dark luxury fintech UI — Plotly 6.x compatible
Replace scripts/streamlit_app.py with this file.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
:root{--bg:#07090f;--card:#0e1117;--surf:#141722;--elev:#1a1f2e;--gold:#c9a84c;--blue:#3b82f6;--green:#10b981;--red:#ef4444;--amber:#f59e0b;--t1:#f0f2f8;--t2:#8892a4;--t3:#505c72;--border:rgba(255,255,255,0.07);--border-h:rgba(201,168,76,0.3);}
.stApp{background:var(--bg)!important;font-family:'Sora',sans-serif!important;color:var(--t1)!important;}
.block-container{padding:1.5rem 2rem 3rem!important;max-width:1400px!important;}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span{color:var(--t2)!important;font-family:'Sora',sans-serif!important;font-size:0.82rem!important;}
[data-testid="stSidebar"] .stRadio label{color:var(--t1)!important;font-size:0.88rem!important;}
h1,h2,h3,h4{font-family:'Sora',sans-serif!important;letter-spacing:-0.02em!important;}
h1{font-size:1.9rem!important;font-weight:700!important;color:var(--t1)!important;}
h2{font-size:1.3rem!important;font-weight:600!important;color:var(--t1)!important;}
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:1.1rem 1.3rem!important;transition:border-color 0.25s,transform 0.2s!important;}
[data-testid="metric-container"]:hover{border-color:var(--border-h)!important;transform:translateY(-2px)!important;}
[data-testid="stMetricLabel"]{color:var(--t2)!important;font-size:0.78rem!important;text-transform:uppercase!important;letter-spacing:0.06em!important;}
[data-testid="stMetricValue"]{color:var(--t1)!important;font-size:1.6rem!important;font-weight:700!important;font-family:'DM Mono',monospace!important;}
.stSelectbox>div>div,.stMultiSelect>div>div,.stTextInput>div>div{background:var(--surf)!important;border:1px solid var(--border)!important;border-radius:6px!important;color:var(--t1)!important;}
.stButton>button{background:transparent!important;border:1px solid var(--border-h)!important;color:var(--gold)!important;font-family:'Sora',sans-serif!important;font-size:0.85rem!important;font-weight:500!important;border-radius:6px!important;padding:0.45rem 1.2rem!important;transition:all 0.2s!important;}
.stButton>button:hover{background:rgba(201,168,76,0.08)!important;transform:translateY(-1px)!important;}
[data-testid="stTabs"] [role="tablist"]{background:var(--card)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--border)!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Sora',sans-serif!important;font-size:0.83rem!important;color:var(--t2)!important;border-radius:6px!important;font-weight:500!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:var(--elev)!important;color:var(--gold)!important;}
hr{border-color:var(--border)!important;margin:1.5rem 0!important;}
.bf-card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:1.4rem 1.6rem;transition:border-color 0.25s,transform 0.2s;}
.bf-card:hover{border-color:var(--border-h);transform:translateY(-2px);}
.bf-section-label{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);margin-bottom:0.4rem;}
.bf-badge{display:inline-block;font-size:0.7rem;font-weight:600;letter-spacing:0.06em;padding:2px 8px;border-radius:20px;text-transform:uppercase;}
.bf-badge-green{background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);}
.bf-badge-red{background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);}
.bf-badge-gold{background:rgba(201,168,76,0.15);color:#c9a84c;border:1px solid rgba(201,168,76,0.3);}
.bf-badge-blue{background:rgba(59,130,246,0.15);color:#3b82f6;border:1px solid rgba(59,130,246,0.3);}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-thumb{background:var(--t3);border-radius:10px;}

/* ── Form inputs visibility fix ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stDateInput"] input {
    background-color: #1a1d27 !important;
    color: #f0f2f8 !important;
    border: 1px solid #c9a84c55 !important;
    border-radius: 6px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.2) !important;
}
div[data-testid="stSelectbox"] > div > div { background-color: #1a1d27 !important; }
div[data-testid="stSelectbox"] svg { fill: #c9a84c !important; }
div[data-testid="stCheckbox"] label { color: #f0f2f8 !important; }
div[data-testid="stCheckbox"] input[type="checkbox"] { accent-color: #c9a84c !important; }

</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Plotly base layout (no height — pass separately) ──────────────────────────
PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Sora, sans-serif", color="#8892a4", size=12),
    title_font=dict(family="Sora, sans-serif", color="#f0f2f8", size=14),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
               linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#505c72", size=11)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
               linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#505c72", size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.07)", borderwidth=1,
                font=dict(color="#8892a4", size=11)),
    margin=dict(l=12, r=12, t=40, b=12),
    hoverlabel=dict(bgcolor="#1a1f2e", bordercolor="rgba(201,168,76,0.3)",
                    font=dict(family="Sora, sans-serif", color="#f0f2f8", size=12)),
)

def pl(**kwargs):
    """Merge PL base with extra layout kwargs."""
    return {**PL, **kwargs}

COLORS = ["#c9a84c","#3b82f6","#10b981","#f59e0b","#8b5cf6","#ef4444","#06b6d4","#ec4899"]

# ── DB ─────────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db", "bluestock_mf.db")

@st.cache_resource
def get_conn():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    return None

@st.cache_data(ttl=300)
def query(_conn, sql, params=()):
    try: return pd.read_sql_query(sql, _conn, params=params)
    except: return pd.DataFrame()

# ── Demo data ──────────────────────────────────────────────────────────────────
@st.cache_data
def demo_nav(n_funds=10, n_days=500):
    np.random.seed(42)
    funds = ["Axis Bluechip Fund","HDFC Top 100","SBI Nifty Index","Mirae Asset Emerging",
             "Parag Parikh Flexi Cap","Kotak Small Cap","DSP Midcap","Nippon India Growth",
             "ICICI Pru Value Discovery","UTI Nifty 50"]
    dates = pd.date_range(end=datetime.today(), periods=n_days, freq="B")
    rows = []
    for f in funds[:n_funds]:
        nav = 50 + np.random.rand()*150
        drift, vol = np.random.uniform(0.0003,0.001), np.random.uniform(0.008,0.018)
        for d in dates:
            nav = nav * np.exp((drift-0.5*vol**2) + vol*np.random.randn())
            rows.append({"date":d,"scheme_name":f,"nav":round(nav,4)})
    return pd.DataFrame(rows)

@st.cache_data
def demo_perf():
    np.random.seed(7)
    funds = ["Axis Bluechip Fund","HDFC Top 100","SBI Nifty Index","Mirae Asset Emerging",
             "Parag Parikh Flexi Cap","Kotak Small Cap","DSP Midcap","Nippon India Growth",
             "ICICI Pru Value Discovery","UTI Nifty 50"]
    cats = ["Large Cap","Large Cap","Index","Mid Cap","Flexi Cap","Small Cap","Mid Cap","Growth","Value","Index"]
    return pd.DataFrame({
        "scheme_name":funds,"category":cats,
        "cagr_1y":np.random.uniform(-5,32,10).round(2),
        "cagr_3y":np.random.uniform(8,25,10).round(2),
        "cagr_5y":np.random.uniform(10,22,10).round(2),
        "sharpe":np.random.uniform(0.5,2.5,10).round(3),
        "sortino":np.random.uniform(0.6,3.0,10).round(3),
        "max_dd":(-np.random.uniform(8,35,10)).round(2),
        "beta":np.random.uniform(0.6,1.4,10).round(3),
        "alpha":np.random.uniform(-2,8,10).round(3),
        "var_95":(-np.random.uniform(1,4,10)).round(3),
        "aum_cr":np.random.uniform(500,25000,10).round(0),
        "expense_ratio":np.random.uniform(0.1,2.0,10).round(2),
    })

@st.cache_data
def demo_sip():
    months = pd.date_range("2020-01-01", periods=60, freq="MS")
    return pd.DataFrame({"month":months,
        "sip_amount_cr":np.cumsum(np.random.uniform(10000,15000,60)).round(0),
        "sip_accounts":np.cumsum(np.random.randint(500000,800000,60))})

@st.cache_data
def demo_aum():
    houses = ["SBI MF","HDFC MF","ICICI Pru","Nippon India","Kotak","Axis","Mirae","DSP"]
    qtrs = ["Q1 FY23","Q2 FY23","Q3 FY23","Q4 FY23","Q1 FY24","Q2 FY24","Q3 FY24","Q4 FY24"]
    rows = []
    for h in houses:
        base = np.random.uniform(50000,700000)
        for q in qtrs:
            rows.append({"fund_house":h,"quarter":q,"aum_cr":round(base*np.random.uniform(0.97,1.08))})
            base = rows[-1]["aum_cr"]
    return pd.DataFrame(rows)

# ── Load ───────────────────────────────────────────────────────────────────────
conn = get_conn()
USE_DB = conn is not None
if USE_DB:
    nav_df  = query(conn, "SELECT date, scheme_name, nav FROM fact_nav ORDER BY date")
    perf_df = query(conn, "SELECT * FROM fact_performance")
    sip_df  = query(conn, "SELECT * FROM fact_sip_industry ORDER BY month")
    aum_df  = query(conn, "SELECT * FROM fact_aum")
    if nav_df.empty: USE_DB = False
if not USE_DB:
    nav_df = demo_nav(); perf_df = demo_perf(); sip_df = demo_sip(); aum_df = demo_aum()

nav_df["date"] = pd.to_datetime(nav_df["date"])
fund_list = sorted(nav_df["scheme_name"].unique().tolist())

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1.4rem;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:1.2rem;">
      <div style="font-family:'Sora',sans-serif;font-size:1.15rem;font-weight:700;color:#f0f2f8;letter-spacing:-0.02em;">
        <span style="color:#c9a84c;">⬡</span> Bluestock</div>
      <div style="font-size:0.72rem;color:#505c72;margin-top:3px;letter-spacing:0.06em;text-transform:uppercase;">MF Analytics Platform</div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("Navigation",
        ["🏠  Overview","📊  NAV Explorer","⚡  Performance","🧪  Simulations","💡  Recommender","📄  Generate Report"],
        label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;color:#505c72;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;'>Filters</div>", unsafe_allow_html=True)
    selected_funds = st.multiselect("Select Funds", fund_list, default=fund_list[:4])
    if not selected_funds: selected_funds = fund_list[:4]

    date_range = st.select_slider("Lookback Period", ["1M","3M","6M","1Y","2Y","3Y","All"], value="1Y")
    LOOKBACK = {"1M":30,"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":99999}
    cutoff = datetime.today() - timedelta(days=LOOKBACK[date_range])
    nav_filt = nav_df[(nav_df["scheme_name"].isin(selected_funds)) & (nav_df["date"] >= cutoff)]

    if not USE_DB:
        st.markdown("""<div style="margin-top:1.5rem;padding:0.8rem 1rem;background:rgba(245,158,11,0.08);
            border:1px solid rgba(245,158,11,0.2);border-radius:8px;font-size:0.75rem;color:#f59e0b;">
            ⚠ Demo mode — connect your SQLite DB to load real data.</div>""", unsafe_allow_html=True)

    st.markdown(f"<br><div style='font-size:0.68rem;color:#505c72;'>Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def kpi_row(metrics):
    cols = st.columns(len(metrics))
    for col, (lbl, val, dlt, dlt_t) in zip(cols, metrics):
        with col: st.metric(lbl, val, dlt, delta_color=dlt_t)

def section_header(label, title, subtitle=""):
    sub = f'<p style="color:#505c72;font-size:0.82rem;margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f'<div style="margin-bottom:1.2rem;"><div class="bf-section-label">{label}</div><h2 style="margin:0 0 2px;">{title}</h2>{sub}</div>', unsafe_allow_html=True)

def chart(fig, h=380, **kwargs):
    fig.update_layout(**pl(height=h, **kwargs))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":
    st.markdown("""
    <div style="padding:2rem 0 1.5rem;">
      <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:#c9a84c;margin-bottom:0.5rem;">Bluestock Fintech · Capstone 2026</div>
      <h1 style="margin:0 0 0.4rem;font-size:2.4rem;">Mutual Fund Intelligence</h1>
      <p style="color:#8892a4;font-size:0.95rem;max-width:520px;line-height:1.6;">
        End-to-end analytics platform covering NAV tracking, risk metrics, Monte Carlo simulations, and AI-powered fund recommendations.</p>
    </div>""", unsafe_allow_html=True)

    total_aum = aum_df.groupby("fund_house")["aum_cr"].last().sum() if not aum_df.empty else 52_000_000
    total_sip = sip_df["sip_amount_cr"].iloc[-1] if not sip_df.empty else 19_000
    sip_delta = sip_df["sip_amount_cr"].pct_change().iloc[-1]*100 if not sip_df.empty else 3.2
    kpi_row([
        ("Total AUM (₹ Cr)", f"₹{total_aum/1e5:.2f}L Cr", "+4.3%", "normal"),
        ("Monthly SIP Flows", f"₹{total_sip/100:.1f}K Cr", f"+{sip_delta:.1f}%", "normal"),
        ("Active Schemes", f"{len(fund_list)}", None, "off"),
        ("Data Points", f"{len(nav_df):,}", None, "off"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
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
            r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
            fig = go.Figure(go.Scatter(
                x=fd["date"], y=fd["nav"], mode="lines",
                line=dict(color=color, width=1.5), fill="tozeroy",
                fillcolor=f"rgba({r},{g},{b},0.06)",
                hovertemplate="%{x|%d %b %Y}<br>₹%{y:.2f}<extra></extra>",
            ))
            fig.update_layout(**pl(height=100, margin=dict(l=0,r=0,t=0,b=0),
                                   xaxis=dict(visible=False), yaxis=dict(visible=False),
                                   showlegend=False))
            st.markdown(f"""
            <div class="bf-card" style="margin-bottom:0.8rem;padding:1rem 1.2rem 0.6rem;">
              <div style="font-size:0.72rem;color:#8892a4;font-weight:500;margin-bottom:2px;
                          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{fund}</div>
              <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:4px;">
                <span style="font-family:'DM Mono',monospace;font-size:1.25rem;font-weight:700;color:#f0f2f8;">₹{fd['nav'].iloc[-1]:.2f}</span>
                <span style="font-size:0.78rem;color:{color};font-weight:600;">{'▲' if chg>=0 else '▼'} {abs(chg):.1f}%</span>
              </div>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Industry Landscape", "AUM & SIP Ecosystem")
    col_a, col_b = st.columns([3, 2])
    with col_a:
        if not aum_df.empty:
            latest_aum = aum_df.groupby("fund_house")["aum_cr"].last().sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=latest_aum.values, y=latest_aum.index, orientation="h",
                marker=dict(color=latest_aum.values,
                            colorscale=[[0,"#1a1f2e"],[0.5,"#3b82f6"],[1,"#c9a84c"]],
                            showscale=False, line=dict(width=0)),
                hovertemplate="%{y}<br>₹%{x:,.0f} Cr<extra></extra>",
            ))
            chart(fig, 300, title="AUM by Fund House (₹ Cr)")
    with col_b:
        if not sip_df.empty:
            fig2 = go.Figure(go.Scatter(
                x=sip_df["month"], y=sip_df["sip_amount_cr"],
                mode="lines", fill="tozeroy",
                line=dict(color="#c9a84c", width=2),
                fillcolor="rgba(201,168,76,0.07)",
                hovertemplate="%{x|%b %Y}<br>₹%{y:,.0f} Cr<extra></extra>",
            ))
            chart(fig2, 300, title="Monthly SIP Inflows (₹ Cr)")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — NAV EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  NAV Explorer":
    section_header("NAV Explorer", "Historical Price & Return Analysis")
    tab1, tab2, tab3 = st.tabs(["  Indexed Returns  ","  Rolling Returns  ","  Correlation  "])

    with tab1:
        pivot = nav_filt.pivot_table(index="date", columns="scheme_name", values="nav")
        if pivot.empty:
            st.info("No data for selected filters.")
        else:
            indexed = (pivot / pivot.iloc[0]) * 100
            fig = go.Figure()
            for i, col in enumerate(indexed.columns):
                fig.add_trace(go.Scatter(x=indexed.index, y=indexed[col], name=col, mode="lines",
                    line=dict(color=COLORS[i % len(COLORS)], width=1.8),
                    hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>%{{y:.1f}}<extra></extra>"))
            fig.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.15)")
            chart(fig, 460, title=f"Indexed NAV Performance (Base=100, {date_range})", hovermode="x unified")
            summary = []
            for f in indexed.columns:
                s = indexed[f].dropna()
                total = s.iloc[-1]-100 if len(s)>1 else 0
                summary.append({"Fund":f,"Current NAV":f"₹{pivot[f].dropna().iloc[-1]:.2f}",
                    "Total Return %":f"{'+' if total>=0 else ''}{total:.1f}%",
                    "Peak":f"₹{pivot[f].max():.2f}","Trough":f"₹{pivot[f].min():.2f}"})
            st.dataframe(pd.DataFrame(summary).set_index("Fund"), use_container_width=True, height=220)

    with tab2:
        c1, c2 = st.columns([2,1])
        with c1: roll_fund = st.selectbox("Fund", selected_funds, key="roll_fund")
        with c2: window = st.select_slider("Window", [21,63,126,252], value=63, key="roll_w",
                                            format_func=lambda x:{21:"1M",63:"3M",126:"6M",252:"1Y"}[x])
        fd = nav_filt[nav_filt["scheme_name"]==roll_fund].sort_values("date")
        if not fd.empty:
            fd = fd.set_index("date")
            fd["roll_ret"] = fd["nav"].pct_change(window)*100
            pos = fd["roll_ret"].clip(lower=0)
            neg = fd["roll_ret"].clip(upper=0)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=fd.index, y=pos, fill="tozeroy",
                fillcolor="rgba(16,185,129,0.12)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=fd.index, y=neg, fill="tozeroy",
                fillcolor="rgba(239,68,68,0.12)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=fd.index, y=fd["roll_ret"], mode="lines", name="Rolling Return",
                line=dict(color="#c9a84c", width=1.5),
                hovertemplate=f"<b>{roll_fund}</b><br>%{{x|%d %b %Y}}<br>%{{y:.2f}}%<extra></extra>"))
            fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_dash="dot")
            label = {21:"1M",63:"3M",126:"6M",252:"1Y"}[window]
            chart(fig, 400, title=f"{roll_fund} — {label} Rolling Returns (%)")

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
                zmid=0, text=np.round(corr.values,2), texttemplate="%{text}",
                hovertemplate="%{x} × %{y}<br>ρ = %{z:.3f}<extra></extra>",
            ))
            chart(fig, 500, title="Return Correlation Matrix")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡  Performance":
    section_header("Risk & Return Engine", "Performance Metrics Dashboard")
    if perf_df.empty:
        st.info("Performance metrics not available.")
    else:
        tab_r, tab_risk, tab_dd, tab_tbl = st.tabs(["  CAGR  ","  Risk Metrics  ","  Drawdown  ","  Full Table  "])
        pf = perf_df[perf_df["scheme_name"].isin(selected_funds)] if "scheme_name" in perf_df.columns else perf_df
        if pf.empty: pf = perf_df

        with tab_r:
            if all(c in pf.columns for c in ["cagr_1y","cagr_3y","cagr_5y"]):
                fig = go.Figure()
                for i,(per,lbl) in enumerate(zip(["cagr_1y","cagr_3y","cagr_5y"],["1 Year","3 Year","5 Year"])):
                    fig.add_trace(go.Bar(name=lbl, x=pf["scheme_name"], y=pf[per],
                        marker_color=COLORS[i], text=pf[per].round(1).astype(str)+"%", textposition="outside",
                        hovertemplate=f"<b>%{{x}}</b><br>{lbl} CAGR: %{{y:.2f}}%<extra></extra>"))
                chart(fig, 440, barmode="group", title="CAGR Comparison (%)", xaxis_tickangle=-25)

        with tab_risk:
            if "sharpe" in pf.columns and "sortino" in pf.columns:
                fig = make_subplots(rows=1, cols=2, subplot_titles=("Sharpe Ratio","Sortino Ratio"))
                fig.add_trace(go.Bar(x=pf["scheme_name"], y=pf["sharpe"], marker_color="#c9a84c",
                    hovertemplate="<b>%{x}</b><br>Sharpe: %{y:.3f}<extra></extra>"), row=1, col=1)
                fig.add_trace(go.Bar(x=pf["scheme_name"], y=pf["sortino"], marker_color="#3b82f6",
                    hovertemplate="<b>%{x}</b><br>Sortino: %{y:.3f}<extra></extra>"), row=1, col=2)
                chart(fig, 380, showlegend=False, xaxis_tickangle=-25, xaxis2_tickangle=-25)

            if all(c in pf.columns for c in ["cagr_3y","max_dd","sharpe"]):
                fig2 = go.Figure(go.Scatter(
                    x=abs(pf["max_dd"]), y=pf["cagr_3y"], mode="markers+text",
                    text=pf["scheme_name"].str[:15], textposition="top center",
                    textfont=dict(size=9, color="#8892a4"),
                    marker=dict(size=pf["sharpe"]*12, color=pf["sharpe"],
                        colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                        showscale=True, colorbar=dict(title="Sharpe", tickfont=dict(color="#8892a4")),
                        line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
                    hovertemplate="<b>%{text}</b><br>Max DD: -%{x:.1f}%<br>3Y CAGR: %{y:.1f}%<extra></extra>"))
                chart(fig2, 380, title="Risk vs Return (bubble = Sharpe)", xaxis_title="Max Drawdown (%)", yaxis_title="3Y CAGR (%)")

        with tab_dd:
            for fund in selected_funds[:5]:
                fd = nav_filt[nav_filt["scheme_name"]==fund].sort_values("date")
                if fd.empty: continue
                prices = fd["nav"].values
                roll_max = np.maximum.accumulate(prices)
                dd = (prices - roll_max) / roll_max * 100
                fig = go.Figure(go.Scatter(x=fd["date"], y=dd, mode="lines", fill="tozeroy",
                    line=dict(color="#ef4444", width=1.2), fillcolor="rgba(239,68,68,0.08)",
                    hovertemplate=f"<b>{fund}</b><br>%{{x|%d %b %Y}}<br>%{{y:.2f}}%<extra></extra>"))
                chart(fig, 160, showlegend=False, title=fund, margin=dict(l=12,r=12,t=32,b=8))

        with tab_tbl:
            display_cols = [c for c in ["scheme_name","category","cagr_1y","cagr_3y","cagr_5y",
                "sharpe","sortino","max_dd","beta","alpha","expense_ratio","aum_cr"] if c in pf.columns]
            st.dataframe(pf[display_cols].set_index("scheme_name") if "scheme_name" in display_cols else pf,
                         use_container_width=True, height=360)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIMULATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪  Simulations":
    section_header("Quantitative Lab", "Monte Carlo & Efficient Frontier")
    tab_mc, tab_ef, tab_var = st.tabs(["  Monte Carlo  ","  Efficient Frontier  ","  VaR Analysis  "])

    with tab_mc:
        c1, c2, c3 = st.columns(3)
        with c1: mc_fund = st.selectbox("Fund", selected_funds, key="mc_f")
        with c2: n_sims = st.select_slider("Simulations", [100,500,1000,2000,5000], value=500)
        with c3: horizon = st.select_slider("Horizon (days)", [30,90,180,252,504], value=252)
        fd = nav_df[nav_df["scheme_name"]==mc_fund].sort_values("date")
        if not fd.empty:
            rets = fd["nav"].pct_change().dropna()
            mu, sigma = rets.mean(), rets.std()
            last_nav = fd["nav"].iloc[-1]
            np.random.seed(0)
            sims = np.zeros((horizon, n_sims))
            for i in range(n_sims):
                sims[:,i] = last_nav * np.cumprod(1 + np.random.normal(mu, sigma, horizon))
            fig = go.Figure()
            x_axis = list(range(horizon))
            for lo,hi,fc in [(5,95,"rgba(201,168,76,0.04)"),(15,85,"rgba(201,168,76,0.07)"),(25,75,"rgba(201,168,76,0.11)")]:
                lower = np.percentile(sims, lo, axis=1); upper = np.percentile(sims, hi, axis=1)
                fig.add_trace(go.Scatter(x=x_axis+x_axis[::-1], y=list(upper)+list(lower[::-1]),
                    fill="toself", fillcolor=fc, line=dict(width=0), showlegend=False, hoverinfo="skip"))
            idx = np.random.choice(n_sims, min(80,n_sims), replace=False)
            for i in idx:
                fig.add_trace(go.Scatter(x=x_axis, y=sims[:,i], mode="lines",
                    line=dict(color="rgba(201,168,76,0.04)", width=0.8), showlegend=False, hoverinfo="skip"))
            median = np.percentile(sims,50,axis=1)
            p10 = np.percentile(sims,10,axis=1); p90 = np.percentile(sims,90,axis=1)
            fig.add_trace(go.Scatter(x=x_axis, y=median, name="Median", line=dict(color="#c9a84c", width=2)))
            fig.add_trace(go.Scatter(x=x_axis, y=p10, name="10th %ile", line=dict(color="#ef4444", width=1.2, dash="dot")))
            fig.add_trace(go.Scatter(x=x_axis, y=p90, name="90th %ile", line=dict(color="#10b981", width=1.2, dash="dot")))
            chart(fig, 460, title=f"Monte Carlo — {mc_fund} ({n_sims} paths, {horizon}d)",
                  yaxis_title="NAV (₹)", xaxis_title="Days Forward")
            final = sims[-1,:]
            kpi_row([
                ("Median Final NAV", f"₹{np.median(final):.2f}", None, "off"),
                ("Best Case (90th %ile)", f"₹{np.percentile(final,90):.2f}", None, "off"),
                ("Worst Case (10th %ile)", f"₹{np.percentile(final,10):.2f}", None, "off"),
                ("Prob. of Profit", f"{(final>last_nav).mean()*100:.1f}%", None, "normal"),
            ])

    with tab_ef:
        if len(selected_funds) >= 3:
            pivot_ef = nav_df[nav_df["scheme_name"].isin(selected_funds)]\
                .pivot_table(index="date", columns="scheme_name", values="nav").pct_change().dropna()
            n_ports = 4000; np.random.seed(1)
            n_assets = pivot_ef.shape[1]
            mu_v = pivot_ef.mean().values*252; cov = pivot_ef.cov().values*252
            port_rets, port_vols, port_sharpe, port_weights = [],[],[],[]
            for _ in range(n_ports):
                w = np.random.dirichlet(np.ones(n_assets))
                r = w@mu_v; v = np.sqrt(w@cov@w)
                port_rets.append(r); port_vols.append(v)
                port_sharpe.append(r/v if v>0 else 0); port_weights.append(w)
            port_rets = np.array(port_rets)*100; port_vols = np.array(port_vols)*100
            port_sharpe = np.array(port_sharpe); best = np.argmax(port_sharpe)
            fig = go.Figure(go.Scatter(x=port_vols, y=port_rets, mode="markers",
                marker=dict(color=port_sharpe, colorscale="Viridis", size=3.5, opacity=0.7,
                    colorbar=dict(title="Sharpe", tickfont=dict(color="#8892a4"))),
                hovertemplate="Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>", showlegend=False))
            fig.add_trace(go.Scatter(x=[port_vols[best]], y=[port_rets[best]], mode="markers+text",
                text=["★ Max Sharpe"], textposition="top right", textfont=dict(color="#c9a84c", size=11),
                marker=dict(color="#c9a84c", size=14, symbol="star"), name="Max Sharpe"))
            chart(fig, 460, title="Markowitz Efficient Frontier",
                  xaxis_title="Annualised Volatility (%)", yaxis_title="Annualised Return (%)")
            opt_w = port_weights[best]
            wt_df = pd.DataFrame({"Fund":list(pivot_ef.columns),"Weight %":(opt_w*100).round(2)}).sort_values("Weight %", ascending=False)
            fig2 = go.Figure(go.Pie(labels=wt_df["Fund"], values=wt_df["Weight %"], hole=0.65,
                marker=dict(colors=COLORS[:len(wt_df)], line=dict(color="#07090f", width=2)),
                textinfo="label+percent", textfont=dict(size=11, color="#f0f2f8"),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>"))
            chart(fig2, 320, title="Max-Sharpe Optimal Portfolio Weights", showlegend=False,
                  annotations=[dict(text=f"Sharpe<br>{port_sharpe[best]:.2f}", x=0.5, y=0.5,
                                    showarrow=False, font=dict(size=14, color="#c9a84c"))])
        else:
            st.info("Select at least 3 funds for Efficient Frontier.")

    with tab_var:
        var_fund = st.selectbox("Fund", selected_funds, key="var_f")
        fd = nav_filt[nav_filt["scheme_name"]==var_fund].sort_values("date")
        if not fd.empty:
            rets_v = fd["nav"].pct_change().dropna()*100
            var_95 = np.percentile(rets_v, 5); var_99 = np.percentile(rets_v, 1)
            cvar_95 = rets_v[rets_v<=var_95].mean()
            fig = go.Figure(go.Histogram(x=rets_v, nbinsx=80, marker_color="#3b82f6",
                marker_line=dict(width=0), opacity=0.7, name="Daily Returns",
                hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>"))
            for v,lbl,col in [(var_95,"VaR 95%","#f59e0b"),(var_99,"VaR 99%","#ef4444")]:
                fig.add_vline(x=v, line_dash="dot", line_color=col, line_width=1.5,
                    annotation_text=f" {lbl}: {v:.2f}%", annotation_font=dict(color=col, size=11))
            chart(fig, 360, title=f"{var_fund} — Daily Return Distribution",
                  xaxis_title="Daily Return (%)", yaxis_title="Frequency")
            kpi_row([("VaR 95% (1-day)", f"{var_95:.2f}%", None, "off"),
                     ("VaR 99% (1-day)", f"{var_99:.2f}%", None, "off"),
                     ("CVaR 95%", f"{cvar_95:.2f}%", None, "off"),
                     ("Annualised Vol", f"{rets_v.std()*np.sqrt(252):.1f}%", None, "off")])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — RECOMMENDER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💡  Recommender":
    section_header("Fund Recommender", "Personalised Fund Discovery")
    with st.expander("⚙  Set Your Investment Profile", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            goal = st.selectbox("Investment Goal",["Wealth Creation","Capital Preservation","Regular Income","Tax Saving"])
            horizon_inv = st.select_slider("Horizon",["<1 Year","1–3 Years","3–5 Years","5+ Years"],value="3–5 Years")
        with c2:
            risk_app = st.select_slider("Risk Appetite",["Very Low","Low","Medium","High","Very High"],value="Medium")
            min_sharpe = st.slider("Min Sharpe Ratio", 0.0, 3.0, 0.8, 0.1)
        with c3:
            max_expense = st.slider("Max Expense Ratio (%)", 0.1, 2.5, 1.5, 0.05)
            pref_cat = st.multiselect("Preferred Categories",
                ["Large Cap","Mid Cap","Small Cap","Flexi Cap","Index","Value","Growth","ELSS"],
                default=["Large Cap","Flexi Cap","Index"])

    if st.button("  🔍  Find Best Funds  "):
        df = perf_df.copy()
        if "sharpe" in df.columns: df = df[df["sharpe"] >= min_sharpe]
        if "expense_ratio" in df.columns: df = df[df["expense_ratio"] <= max_expense]
        if pref_cat and "category" in df.columns: df = df[df["category"].isin(pref_cat)]
        df["score"] = 0.0
        for col_name, w in [("sharpe",0.3),("cagr_3y",0.25),("sortino",0.2),("max_dd",0.15),("alpha",0.1)]:
            if col_name in df.columns:
                s = df[col_name] if col_name!="max_dd" else -df[col_name]
                df["score"] += w * (s-s.min())/(s.max()-s.min()+1e-9)
        df = df.sort_values("score", ascending=False).head(6)
        st.markdown(f"<h3 style='color:#f0f2f8;margin:1rem 0;'>Top Picks for <span style='color:#c9a84c;'>{goal}</span></h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        rank_colors = ["#c9a84c","#8892a4","#b45309"]
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 3]:
                rc = rank_colors[min(i,2)]
                sharpe_v = f"{row['sharpe']:.2f}" if "sharpe" in row else "N/A"
                cagr_v = f"{row['cagr_3y']:.1f}%" if "cagr_3y" in row else "N/A"
                dd_v = f"{row['max_dd']:.1f}%" if "max_dd" in row else "N/A"
                cat = row.get("category","—")
                st.markdown(f"""
                <div class="bf-card" style="margin-bottom:1rem;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.7rem;">
                    <span style="font-size:1.2rem;font-weight:700;color:{rc};">#{i+1}</span>
                    <span class="bf-badge bf-badge-gold">{cat}</span>
                  </div>
                  <div style="font-weight:600;font-size:0.88rem;color:#f0f2f8;line-height:1.35;margin-bottom:0.8rem;">{row['scheme_name']}</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div><div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:#505c72;">Sharpe</div>
                      <div style="font-family:'DM Mono',monospace;font-size:1rem;font-weight:600;color:#c9a84c;">{sharpe_v}</div></div>
                    <div><div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:#505c72;">3Y CAGR</div>
                      <div style="font-family:'DM Mono',monospace;font-size:1rem;font-weight:600;color:#10b981;">{cagr_v}</div></div>
                    <div><div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:#505c72;">Max DD</div>
                      <div style="font-family:'DM Mono',monospace;font-size:1rem;font-weight:600;color:#ef4444;">{dd_v}</div></div>
                    <div><div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:#505c72;">Score</div>
                      <div style="font-family:'DM Mono',monospace;font-size:1rem;font-weight:600;color:#f0f2f8;">{row['score']:.2f}</div></div>
                  </div>
                </div>""", unsafe_allow_html=True)
        if df.empty:
            st.warning("No funds match your filters. Try relaxing Sharpe / Expense Ratio.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — GENERATE REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📄  Generate Report":
    import io, base64
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable, KeepTogether)
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    section_header("Report Studio", "Generate Portfolio Report",
                   "Build a branded PDF report for selected funds — download instantly")

    # ── Report config UI ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**📋 Report Content**")
        rpt_title    = st.text_input("Report Title", "Bluestock MF Portfolio Report")
        rpt_subtitle = st.text_input("Subtitle / Client Name", "Prepared for: Investment Committee")
        include_perf   = st.checkbox("Include Performance Metrics Table", True)
        include_nav    = st.checkbox("Include NAV Summary Table", True)
        include_risk   = st.checkbox("Include Risk Metrics (Sharpe, MDD, VaR)", True)
        include_mc     = st.checkbox("Include Monte Carlo Summary", True)
        include_notes  = st.checkbox("Include Analyst Notes Section", True)
        analyst_notes  = ""
        if include_notes:
            analyst_notes = st.text_area("Analyst Notes",
                "Based on the quantitative analysis, the selected funds demonstrate strong "
                "risk-adjusted returns. Recommend maintaining core allocation to large-cap "
                "and flexi-cap strategies with a 3–5 year horizon.",
                height=100)

    with c2:
        st.markdown("**🎨 Report Style**")
        report_date  = st.date_input("Report Date", datetime.today())
        period_label = st.selectbox("Analysis Period", ["1 Month","3 Months","6 Months","1 Year","3 Years","5 Years"], index=3)
        disclaimer   = st.text_area("Disclaimer",
            "This report is generated for educational and informational purposes only. "
            "Past performance is not indicative of future results. Not investment advice.",
            height=80)

        st.markdown("<br>", unsafe_allow_html=True)
        # Preview card
        st.markdown(f"""
        <div class="bf-card" style="border-color:rgba(201,168,76,0.3);">
          <div class="bf-section-label">Preview</div>
          <div style="font-size:1rem;font-weight:700;color:#f0f2f8;margin-bottom:4px;">{rpt_title}</div>
          <div style="font-size:0.78rem;color:#8892a4;margin-bottom:8px;">{rpt_subtitle}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <span class="bf-badge bf-badge-gold">{len(selected_funds)} Funds</span>
            <span class="bf-badge bf-badge-blue">{period_label}</span>
            <span class="bf-badge bf-badge-green">{report_date.strftime('%d %b %Y')}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Generate button ───────────────────────────────────────────────────────
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        generate = st.button("  📄  Generate PDF Report  ")
    with col_info:
        st.markdown("<div style='color:#8892a4;font-size:0.82rem;padding-top:0.6rem;'>Report includes all selected funds from the sidebar filter. Switch funds there before generating.</div>", unsafe_allow_html=True)

    if generate:
        with st.spinner("Building your report..."):

            # ── Compute data for report ───────────────────────────────────────
            LOOKBACK_MAP = {"1 Month":30,"3 Months":90,"6 Months":180,
                            "1 Year":365,"3 Years":1095,"5 Years":1825}
            days = LOOKBACK_MAP.get(period_label, 365)
            cutoff_r = datetime.today() - timedelta(days=days)
            nav_r = nav_df[(nav_df["scheme_name"].isin(selected_funds)) & (nav_df["date"] >= cutoff_r)]

            # Per-fund summary
            fund_summary = []
            for fund in selected_funds:
                fd = nav_r[nav_r["scheme_name"] == fund].sort_values("date")
                if fd.empty: continue
                start_nav = fd["nav"].iloc[0]; end_nav = fd["nav"].iloc[-1]
                ret_pct = (end_nav / start_nav - 1) * 100
                prices = fd["nav"].values
                roll_max = np.maximum.accumulate(prices)
                mdd = ((prices - roll_max) / roll_max * 100).min()
                daily_rets = fd["nav"].pct_change().dropna()
                sharpe = (daily_rets.mean() / daily_rets.std() * np.sqrt(252)) if daily_rets.std() > 0 else 0
                vol = daily_rets.std() * np.sqrt(252) * 100
                var95 = np.percentile(daily_rets * 100, 5)
                fund_summary.append({
                    "Fund": fund,
                    "Start NAV": f"₹{start_nav:.2f}",
                    "Latest NAV": f"₹{end_nav:.2f}",
                    "Return (%)": f"{ret_pct:+.2f}%",
                    "Sharpe": f"{sharpe:.2f}",
                    "Ann. Vol (%)": f"{vol:.1f}%",
                    "Max DD (%)": f"{mdd:.1f}%",
                    "VaR 95%": f"{var95:.2f}%",
                })
            summary_df = pd.DataFrame(fund_summary)

            # Perf metrics for selected funds
            perf_sel = perf_df[perf_df["scheme_name"].isin(selected_funds)] if "scheme_name" in perf_df.columns else pd.DataFrame()

            # ── Build PDF ─────────────────────────────────────────────────────
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=1.8*cm, leftMargin=1.8*cm,
                                    topMargin=2*cm, bottomMargin=1.8*cm)

            # Colours
            GOLD    = colors.HexColor("#c9a84c")
            DARK    = colors.HexColor("#07090f")
            CARD    = colors.HexColor("#0e1117")
            SURF    = colors.HexColor("#141722")
            T1      = colors.HexColor("#f0f2f8")
            T2      = colors.HexColor("#8892a4")
            T3      = colors.HexColor("#505c72")
            GREEN   = colors.HexColor("#10b981")
            RED     = colors.HexColor("#ef4444")
            BLUE    = colors.HexColor("#3b82f6")

            styles = getSampleStyleSheet()
            def sty(name, **kw):
                return ParagraphStyle(name, **kw)

            S_eyebrow  = sty("eyebrow",  fontSize=7,  textColor=GOLD,   spaceAfter=2,  leading=10,
                              fontName="Helvetica-Bold", letterSpacing=1.5)
            S_h1       = sty("h1",       fontSize=22, textColor=T1,     spaceAfter=4,  leading=26,
                              fontName="Helvetica-Bold")
            S_h2       = sty("h2",       fontSize=13, textColor=T1,     spaceAfter=6,  leading=18,
                              fontName="Helvetica-Bold", spaceBefore=14)
            S_h3       = sty("h3",       fontSize=10, textColor=T2,     spaceAfter=4,  leading=14,
                              fontName="Helvetica")
            S_body     = sty("body",     fontSize=9,  textColor=T2,     spaceAfter=6,  leading=14,
                              fontName="Helvetica")
            S_disclaimer = sty("disc",   fontSize=7,  textColor=T3,     spaceAfter=0,  leading=10,
                              fontName="Helvetica", spaceBefore=10)
            S_meta     = sty("meta",     fontSize=8,  textColor=T3,     spaceAfter=2,  leading=12,
                              fontName="Helvetica")
            S_footer   = sty("footer",   fontSize=7,  textColor=T3,     spaceAfter=0,  leading=10,
                              fontName="Helvetica", alignment=TA_CENTER)

            def hr(color=GOLD, thickness=0.5, width="100%", space_before=4, space_after=10):
                return HRFlowable(width=width, thickness=thickness, color=color,
                                  spaceAfter=space_after, spaceBefore=space_before)

            def section_title(text):
                return [Paragraph(text.upper(), S_eyebrow), hr(GOLD, 0.5, space_after=8)]

            def make_table(headers, rows, col_widths=None):
                data = [headers] + rows
                tbl = Table(data, colWidths=col_widths)
                style = TableStyle([
                    # Header
                    ("BACKGROUND",  (0,0), (-1,0),  SURF),
                    ("TEXTCOLOR",   (0,0), (-1,0),  GOLD),
                    ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
                    ("FONTSIZE",    (0,0), (-1,0),  7.5),
                    ("TOPPADDING",  (0,0), (-1,0),  7),
                    ("BOTTOMPADDING",(0,0),(-1,0),  7),
                    ("LEFTPADDING", (0,0), (-1,-1), 8),
                    ("RIGHTPADDING",(0,0), (-1,-1), 8),
                    # Rows
                    ("BACKGROUND",  (0,1), (-1,-1), CARD),
                    ("TEXTCOLOR",   (0,1), (-1,-1), T2),
                    ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
                    ("FONTSIZE",    (0,1), (-1,-1), 7.5),
                    ("TOPPADDING",  (0,1), (-1,-1), 5),
                    ("BOTTOMPADDING",(0,1),(-1,-1), 5),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CARD, colors.HexColor("#111520")]),
                    # Grid
                    ("LINEBELOW",   (0,0), (-1,0),  0.5, GOLD),
                    ("LINEBELOW",   (0,1), (-1,-1), 0.3, colors.HexColor("#1a1f2e")),
                    ("BOX",         (0,0), (-1,-1), 0.5, colors.HexColor("#1a1f2e")),
                    ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
                ])
                tbl.setStyle(style)
                return tbl

            # ── Build story ───────────────────────────────────────────────────
            story = []

            # Cover header
            story.append(Paragraph("BLUESTOCK FINTECH  ·  CAPSTONE 2026", S_eyebrow))
            story.append(Spacer(1, 4))
            story.append(Paragraph(rpt_title, S_h1))
            story.append(Paragraph(rpt_subtitle, S_h3))
            story.append(Spacer(1, 6))

            # Meta row
            meta_data = [[
                Paragraph(f"<b>Report Date</b><br/>{report_date.strftime('%d %B %Y')}", S_meta),
                Paragraph(f"<b>Analysis Period</b><br/>{period_label}", S_meta),
                Paragraph(f"<b>Funds Covered</b><br/>{len(selected_funds)}", S_meta),
                Paragraph(f"<b>Generated By</b><br/>Bluestock Analytics Engine", S_meta),
            ]]
            meta_tbl = Table(meta_data, colWidths=[4.2*cm]*4)
            meta_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,-1), SURF),
                ("BOX",        (0,0),(-1,-1), 0.5, GOLD),
                ("INNERGRID",  (0,0),(-1,-1), 0.3, colors.HexColor("#1a1f2e")),
                ("TOPPADDING", (0,0),(-1,-1), 8),
                ("BOTTOMPADDING",(0,0),(-1,-1),8),
                ("LEFTPADDING",(0,0),(-1,-1),10),
            ]))
            story.append(meta_tbl)
            story.append(hr(GOLD, 1, space_after=16, space_before=16))

            # Executive summary
            story += section_title("Executive Summary")
            total_ret = summary_df["Return (%)"].str.replace("%","").str.replace("+","").astype(float).mean() if not summary_df.empty else 0
            best_fund = summary_df.loc[summary_df["Return (%)"].str.replace("%","").str.replace("+","").astype(float).idxmax(), "Fund"] if not summary_df.empty else "N/A"
            story.append(Paragraph(
                f"This report covers <b>{len(selected_funds)} mutual fund schemes</b> over a "
                f"<b>{period_label}</b> analysis window ending <b>{report_date.strftime('%d %B %Y')}</b>. "
                f"The portfolio delivered an average return of <b>{total_ret:+.1f}%</b> during this period. "
                f"The top-performing fund was <b>{best_fund}</b>. "
                f"Risk metrics including Sharpe ratio, Maximum Drawdown, and Value-at-Risk are detailed in the sections below.",
                S_body))
            story.append(Spacer(1, 8))

            # NAV Summary Table
            if include_nav and not summary_df.empty:
                story += section_title("NAV & Return Summary")
                hdrs = ["Fund", "Start NAV", "Latest NAV", "Return", "Sharpe", "Ann. Vol", "Max DD", "VaR 95%"]
                rows = [[
                    Paragraph(r["Fund"][:28], S_body),
                    r["Start NAV"], r["Latest NAV"], r["Return (%)"],
                    r["Sharpe"], r["Ann. Vol (%)"], r["Max DD (%)"], r["VaR 95%"]
                ] for _, r in summary_df.iterrows()]
                tbl = make_table(hdrs, rows,
                                 col_widths=[5.5*cm,1.8*cm,1.8*cm,1.5*cm,1.4*cm,1.5*cm,1.5*cm,1.5*cm])
                story.append(tbl)
                story.append(Spacer(1, 12))

            # Performance metrics table
            if include_perf and not perf_sel.empty:
                story += section_title("Performance Metrics (from Database)")
                perf_cols = ["scheme_name","category","cagr_1y","cagr_3y","cagr_5y","sharpe","sortino","expense_ratio"]
                perf_avail = [c for c in perf_cols if c in perf_sel.columns]
                if len(perf_avail) > 1:
                    hdrs2 = ["Fund","Category","1Y CAGR%","3Y CAGR%","5Y CAGR%","Sharpe","Sortino","Exp Ratio"][:len(perf_avail)]
                    rows2 = []
                    for _, r in perf_sel[perf_avail].iterrows():
                        row2 = []
                        for i, c in enumerate(perf_avail):
                            val = r[c]
                            if c == "scheme_name": row2.append(Paragraph(str(val)[:28], S_body))
                            elif isinstance(val, float): row2.append(f"{val:.2f}")
                            else: row2.append(str(val))
                        rows2.append(row2)
                    w2 = [4.5*cm] + [1.8*cm]*(len(perf_avail)-1)
                    story.append(make_table(hdrs2, rows2, col_widths=w2))
                    story.append(Spacer(1, 12))

            # Risk section
            if include_risk and not summary_df.empty:
                story += section_title("Risk Analysis")
                story.append(Paragraph(
                    "The table below shows key risk indicators computed from daily NAV returns. "
                    "Sharpe ratio measures risk-adjusted return (higher is better). "
                    "Maximum Drawdown (Max DD) captures the worst peak-to-trough loss. "
                    "VaR 95% shows the daily loss not exceeded 95% of the time.",
                    S_body))
                story.append(Spacer(1, 6))
                hdrs3 = ["Fund", "Sharpe Ratio", "Annualised Vol", "Max Drawdown", "VaR 95% (1D)"]
                rows3 = [[
                    Paragraph(r["Fund"][:32], S_body),
                    r["Sharpe"], r["Ann. Vol (%)"], r["Max DD (%)"], r["VaR 95%"]
                ] for _, r in summary_df.iterrows()]
                story.append(make_table(hdrs3, rows3, col_widths=[6.5*cm,2.5*cm,2.5*cm,2.5*cm,2.5*cm]))
                story.append(Spacer(1, 12))

            # Monte Carlo summary
            if include_mc and selected_funds:
                story += section_title("Monte Carlo Simulation Summary")
                story.append(Paragraph(
                    f"Forward-looking Monte Carlo simulations (500 paths, 252-day horizon) were run "
                    f"for all {len(selected_funds)} selected funds using historical daily return "
                    f"distributions. Results below show the median projected NAV and probability of "
                    f"outperforming the starting NAV at the end of the simulation period.",
                    S_body))
                story.append(Spacer(1, 6))
                mc_rows = []
                for fund in selected_funds:
                    fd = nav_df[nav_df["scheme_name"]==fund].sort_values("date")
                    if fd.empty: continue
                    rets = fd["nav"].pct_change().dropna()
                    mu_mc, sig_mc = rets.mean(), rets.std()
                    last = fd["nav"].iloc[-1]
                    np.random.seed(42)
                    sims_mc = np.zeros((252, 200))
                    for i in range(200):
                        sims_mc[:,i] = last * np.cumprod(1 + np.random.normal(mu_mc,sig_mc,252))
                    final_mc = sims_mc[-1,:]
                    mc_rows.append([
                        Paragraph(fund[:30], S_body),
                        f"₹{last:.2f}",
                        f"₹{np.median(final_mc):.2f}",
                        f"₹{np.percentile(final_mc,10):.2f}",
                        f"₹{np.percentile(final_mc,90):.2f}",
                        f"{(final_mc>last).mean()*100:.0f}%",
                    ])
                if mc_rows:
                    story.append(make_table(
                        ["Fund","Current NAV","Median (252d)","Bear (10th)","Bull (90th)","P(Profit)"],
                        mc_rows, col_widths=[5.5*cm,2*cm,2.2*cm,2*cm,2*cm,1.8*cm]))
                story.append(Spacer(1, 12))

            # Analyst notes
            if include_notes and analyst_notes.strip():
                story += section_title("Analyst Commentary")
                story.append(Paragraph(analyst_notes, S_body))
                story.append(Spacer(1, 12))

            # Fund list appendix
            story += section_title("Funds in This Report")
            for i, f in enumerate(selected_funds, 1):
                story.append(Paragraph(f"{i}. {f}", S_body))
            story.append(Spacer(1, 12))

            # Disclaimer + footer
            story.append(hr(T3, 0.3, space_after=6, space_before=12))
            story.append(Paragraph("DISCLAIMER", S_eyebrow))
            story.append(Paragraph(disclaimer, S_disclaimer))
            story.append(Spacer(1, 10))
            story.append(Paragraph(
                f"© 2026 Bluestock Fintech Pvt. Ltd.  ·  Generated {datetime.now().strftime('%d %b %Y %H:%M')}  ·  bluestockmfcapstone.streamlit.app",
                S_footer))

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()

        # ── Success + Download ────────────────────────────────────────────────
        st.success("✅ Report generated successfully!")
        safe_title = rpt_title.replace(" ","_").replace("/","_")[:40]
        filename = f"Bluestock_MF_Report_{report_date.strftime('%Y%m%d')}_{safe_title}.pdf"
        st.download_button(
            label="  ⬇  Download PDF Report  ",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )

        # Quick stats strip
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_row([
            ("Funds Covered", str(len(selected_funds)), None, "off"),
            ("Analysis Period", period_label, None, "off"),
            ("Avg Return", f"{total_ret:+.1f}%", None, "normal" if total_ret >= 0 else "inverse"),
            ("Report Size", f"{len(pdf_bytes)/1024:.1f} KB", None, "off"),
        ])

        # Preview table in app
        if not summary_df.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("In-App Preview", "NAV & Risk Summary Table")
            st.dataframe(summary_df.set_index("Fund"), use_container_width=True, height=300)

st.markdown("---")
st.markdown("""<div style="display:flex;justify-content:space-between;padding:0.5rem 0;color:#505c72;font-size:0.72rem;">
  <span>© 2026 <strong style="color:#8892a4;">Bluestock Fintech Pvt. Ltd.</strong> — Educational purposes only.</span>
  <span>Data: AMFI India · mfapi.in · NSE/BSE</span>
</div>""", unsafe_allow_html=True)
