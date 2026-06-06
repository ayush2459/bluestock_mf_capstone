"""
Bluestock Fintech — Streamlit Dashboard (B2 Bonus)
Run: streamlit run scripts/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
DB   = BASE / "data" / "db" / "bluestock_mf.db"

st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {background:#1e3a5f;padding:16px;border-radius:10px;color:white;text-align:center;margin:4px;}
.metric-value {font-size:26px;font-weight:bold;color:#64B5F6;}
.metric-label {font-size:12px;color:#90CAF9;margin-top:4px;}
.stSelectbox>div>div {border-color:#1e3a5f;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    nav   = pd.read_csv(RAW/"02_nav_history.csv", parse_dates=["date"])
    fund  = pd.read_csv(RAW/"01_fund_master.csv").drop_duplicates("amfi_code")
    sip   = pd.read_csv(RAW/"04_monthly_sip_inflows.csv")
    aum   = pd.read_csv(RAW/"03_aum_by_fund_house.csv")
    tx    = pd.read_csv(RAW/"08_investor_transactions.csv", parse_dates=["transaction_date"])
    bench = pd.read_csv(RAW/"10_benchmark_indices.csv", parse_dates=["date"])
    folio = pd.read_csv(RAW/"06_industry_folio_count.csv")
    cat   = pd.read_csv(RAW/"05_category_inflows.csv")
    if (PROC/"fund_metrics.csv").exists():
        perf = pd.read_csv(PROC/"fund_metrics.csv")
    else:
        perf = pd.read_csv(RAW/"07_scheme_performance.csv")
    nav = nav.merge(fund[["amfi_code","scheme_name","sub_category","fund_house"]], on="amfi_code", how="left")
    return nav, fund, sip, aum, tx, bench, folio, cat, perf


nav, fund, sip, aum, tx, bench, folio, cat, perf = load_data()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.image("https://via.placeholder.com/200x60/1e3a5f/ffffff?text=BLUESTOCK+MF", use_column_width=True)
st.sidebar.title("🔍 Filters")

page = st.sidebar.radio("Navigate", ["🏠 Industry Overview", "📈 Fund Performance",
                                      "👥 Investor Analytics", "📊 SIP & Trends"])
fund_houses = ["All"] + sorted(fund["fund_house"].dropna().unique().tolist())
sel_house   = st.sidebar.selectbox("Fund House", fund_houses)
categories  = ["All"] + sorted(fund["sub_category"].dropna().unique().tolist())
sel_cat     = st.sidebar.selectbox("Category", categories)
date_range  = st.sidebar.date_input("Date Range",
    value=[nav["date"].min(), nav["date"].max()],
    min_value=nav["date"].min(), max_value=nav["date"].max())

# Filter nav
nav_f = nav.copy()
if sel_house != "All":
    nav_f = nav_f[nav_f["fund_house"] == sel_house]
if sel_cat != "All":
    nav_f = nav_f[nav_f["sub_category"] == sel_cat]
if len(date_range) == 2:
    nav_f = nav_f[(nav_f["date"] >= pd.Timestamp(date_range[0])) &
                  (nav_f["date"] <= pd.Timestamp(date_range[1]))]

# ══════════════════════════════════════════════════════════════
if page == "🏠 Industry Overview":
    st.title("🏠 Industry Overview — Bluestock MF Platform")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="metric-card"><div class="metric-value">Rs.81L Cr</div><div class="metric-label">Industry AUM (Dec 2025)</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><div class="metric-value">Rs.31,002 Cr</div><div class="metric-label">SIP Inflow (Dec 2025)</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><div class="metric-value">26.12 Cr</div><div class="metric-label">Total Folios (Dec 2025)</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="metric-card"><div class="metric-value">1,908</div><div class="metric-label">Active Schemes</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 SIP Inflow Trend")
        sip["month_dt"] = pd.to_datetime(sip["month"])
        fig = px.area(sip, x="month_dt", y="sip_inflow_crore",
                      title="Monthly SIP Inflow (Rs. Crore)",
                      color_discrete_sequence=["#1565C0"])
        fig.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏦 AUM by Fund House")
        latest_q = aum["quarter"].max()
        aum_latest = aum[aum["quarter"]==latest_q].sort_values("aum_lakh_crore",ascending=False)
        fig = px.bar(aum_latest, x="fund_house", y="aum_lakh_crore",
                     color="aum_lakh_crore", color_continuous_scale="Blues",
                     title=f"AUM by Fund House ({latest_q})")
        fig.update_layout(showlegend=False, height=320, xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📂 Folio Count Growth")
    folio["month_dt"] = pd.to_datetime(folio["month"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=folio["month_dt"], y=folio["equity_folios_crore"],
                             fill="tozeroy", name="Equity", line_color="#1565C0"))
    fig.add_trace(go.Scatter(x=folio["month_dt"], y=folio["debt_folios_crore"],
                             fill="tozeroy", name="Debt", line_color="#F57F17"))
    fig.add_trace(go.Scatter(x=folio["month_dt"], y=folio["hybrid_folios_crore"],
                             fill="tozeroy", name="Hybrid", line_color="#2E7D32"))
    fig.update_layout(title="Mutual Fund Folio Count (Crore)", height=320)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
elif page == "📈 Fund Performance":
    st.title("📈 Fund Performance Analytics")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Fund Scorecard")
        perf_m = perf.merge(fund[["amfi_code","scheme_name","sub_category","fund_house","expense_ratio_pct"]],
                             on="amfi_code", how="left")
        disp_cols = ["scheme_name","sub_category","cagr_3yr_pct","sharpe_ratio",
                     "max_drawdown_pct","composite_score","score_rank"]
        disp_cols = [c for c in disp_cols if c in perf_m.columns]
        st.dataframe(perf_m[disp_cols].sort_values("score_rank").head(15)
                     .reset_index(drop=True), use_container_width=True)

    with col2:
        st.subheader("🔵 Risk vs Return")
        if "cagr_3yr_pct" in perf_m.columns and "std_dev_ann_pct" in perf_m.columns:
            fig = px.scatter(perf_m.dropna(subset=["cagr_3yr_pct","std_dev_ann_pct"]),
                             x="std_dev_ann_pct", y="cagr_3yr_pct",
                             color="sub_category", hover_name="scheme_name",
                             size=[10]*len(perf_m),
                             title="Risk (Std Dev) vs Return (3yr CAGR)")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 NAV Performance")
    codes_avail = nav_f["amfi_code"].unique().tolist()
    if len(codes_avail) > 0:
        sel_codes = st.multiselect("Select Funds to Compare", codes_avail[:20],
                                    default=codes_avail[:3])
        if sel_codes:
            fig = go.Figure()
            for code in sel_codes:
                sub = nav_f[nav_f["amfi_code"]==code].sort_values("date")
                if sub.empty: continue
                norm = sub["nav"] / sub["nav"].iloc[0] * 100
                name = sub["scheme_name"].iloc[0] if "scheme_name" in sub.columns else str(code)
                fig.add_trace(go.Scatter(x=sub["date"], y=norm, name=name[:30], mode="lines"))
            fig.update_layout(title="NAV Performance (Indexed to 100)",
                              xaxis_title="Date", yaxis_title="Indexed NAV", height=380)
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
elif page == "👥 Investor Analytics":
    st.title("👥 Investor Analytics")

    states = ["All"] + sorted(tx["state"].dropna().unique().tolist())
    sel_state = st.selectbox("Filter by State", states)
    age_groups = ["All"] + sorted(tx["age_group"].dropna().unique().tolist())
    sel_age   = st.selectbox("Filter by Age Group", age_groups)

    tx_f = tx.copy()
    if sel_state != "All": tx_f = tx_f[tx_f["state"]==sel_state]
    if sel_age   != "All": tx_f = tx_f[tx_f["age_group"]==sel_age]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Investment by State")
        state_data = tx_f.groupby("state")["amount_inr"].sum().sort_values(ascending=False).reset_index()
        state_data["amount_crore"] = state_data["amount_inr"]/1e7
        fig = px.bar(state_data, x="amount_crore", y="state", orientation="h",
                     color="amount_crore", color_continuous_scale="Blues",
                     title="Total Investment by State (Rs. Crore)")
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 Transaction Type Split")
        tx_type = tx_f["transaction_type"].value_counts()
        fig = px.pie(values=tx_type.values, names=tx_type.index,
                     color_discrete_sequence=["#1565C0","#2E7D32","#C62828"],
                     title="SIP vs Lumpsum vs Redemption")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("👶 Age Group Analysis")
    age_data = tx_f[tx_f["transaction_type"]=="Sip"].groupby("age_group").agg(
        avg_sip=("amount_inr","mean"), total=("amount_inr","sum"), count=("investor_id","nunique")
    ).reset_index()
    fig = px.bar(age_data, x="age_group", y="avg_sip", color="count",
                 title="Avg SIP Amount by Age Group",
                 color_continuous_scale="Viridis")
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
elif page == "📊 SIP & Trends":
    st.title("📊 SIP Industry Trends & Market Analysis")

    col1, col2 = st.columns(2)
    sip["month_dt"] = pd.to_datetime(sip["month"])

    with col1:
        st.subheader("📈 SIP vs Active Accounts")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=sip["month_dt"], y=sip["sip_inflow_crore"],
                             name="SIP Inflow (Cr)", marker_color="#1565C0", opacity=0.8))
        fig.add_trace(go.Scatter(x=sip["month_dt"], y=sip["active_sip_accounts_crore"]*3000,
                                  name="Active Accounts (Cr)×3000",
                                  line=dict(color="orange", width=2), yaxis="y2"))
        fig.update_layout(
            title="SIP Inflow & Active Accounts", height=360,
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🗺️ Category Inflows Heatmap")
        cat["month_dt"] = pd.to_datetime(cat["month"])
        pivot_cat = cat.pivot_table(index="category", columns="month",
                                    values="net_inflow_crore", aggfunc="sum")
        fig = px.imshow(pivot_cat, color_continuous_scale="RdYlGn",
                        title="Category Net Inflows (Rs. Crore)", aspect="auto")
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 Benchmark Index Comparison")
    idx_sel = st.multiselect("Select Indices",
        bench["index_name"].unique().tolist(),
        default=["Nifty50","Nifty100","NiftyMidcap150"])
    bench_f = bench[bench["index_name"].isin(idx_sel)].copy()
    fig = px.line(bench_f, x="date", y="close_value", color="index_name",
                  title="Benchmark Index Values 2022–2026")
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Bluestock Fintech Pvt. Ltd. | For educational use only.")
