"""Load all 10 local CSVs into SQLite DB (bypasses live API - uses generated data)"""
import sqlite3, pandas as pd, numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
DB   = BASE / "data" / "db" / "bluestock_mf.db"
SQL  = BASE / "sql" / "schema.sql"
PROC.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA foreign_keys=OFF;")  # allow bulk load

# Apply schema
conn.executescript(SQL.read_text())
print("Schema applied ✓")

# 1. dim_fund
df_fund = pd.read_csv(RAW/"01_fund_master.csv").drop_duplicates("amfi_code")
df_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
print(f"dim_fund: {len(df_fund)} rows")

# 2. dim_date
dates = pd.date_range("2022-01-01","2026-05-31")
dim_date = pd.DataFrame({
    "date_id":     dates.strftime("%Y-%m-%d"),
    "year":        dates.year,
    "quarter":     dates.quarter,
    "month":       dates.month,
    "month_name":  dates.strftime("%B"),
    "week":        dates.isocalendar().week.values,
    "day_of_week": dates.dayofweek,
    "is_weekday":  (dates.dayofweek < 5).astype(int),
    "is_month_end":(dates.is_month_end).astype(int),
})
dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
print(f"dim_date: {len(dim_date)} rows")

# 3. fact_nav
df_nav = pd.read_csv(RAW/"02_nav_history.csv", parse_dates=["date"])
df_nav = df_nav[df_nav["amfi_code"].isin(df_fund["amfi_code"])]
df_nav = df_nav.sort_values(["amfi_code","date"])
df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()
df_nav["nav_52w_high"] = df_nav.groupby("amfi_code")["nav"].transform(lambda x: x.rolling(252,min_periods=1).max())
df_nav["nav_52w_low"]  = df_nav.groupby("amfi_code")["nav"].transform(lambda x: x.rolling(252,min_periods=1).min())
df_nav["rolling_30d_vol"] = df_nav.groupby("amfi_code")["daily_return"].transform(
    lambda x: x.rolling(30,min_periods=5).std() * np.sqrt(252))
df_nav_db = df_nav.rename(columns={"date":"nav_date","nav":"nav_inr"})
df_nav_db["nav_date"] = df_nav_db["nav_date"].dt.strftime("%Y-%m-%d")
df_nav_db[["amfi_code","nav_date","nav_inr","daily_return","nav_52w_high","nav_52w_low","rolling_30d_vol"]].to_sql(
    "fact_nav", conn, if_exists="replace", index=False)
# Save processed master CSV
df_nav_db.to_csv(PROC/"nav_master.csv", index=False)
print(f"fact_nav: {len(df_nav_db)} rows")

# 4. fact_transactions
df_tx = pd.read_csv(RAW/"08_investor_transactions.csv")
df_tx = df_tx[df_tx["amfi_code"].isin(df_fund["amfi_code"])]
df_tx.to_sql("fact_transactions", conn, if_exists="replace", index=False)
print(f"fact_transactions: {len(df_tx)} rows")

# 5. fact_aum
df_aum = pd.read_csv(RAW/"03_aum_by_fund_house.csv")
df_aum.to_sql("fact_aum", conn, if_exists="replace", index=False)
print(f"fact_aum: {len(df_aum)} rows")

# 6. fact_sip_industry
df_sip = pd.read_csv(RAW/"04_monthly_sip_inflows.csv")
df_sip.to_sql("fact_sip_industry", conn, if_exists="replace", index=False)
print(f"fact_sip_industry: {len(df_sip)} rows")

# 7. fact_benchmark
df_bench = pd.read_csv(RAW/"10_benchmark_indices.csv")
df_bench.to_sql("fact_benchmark", conn, if_exists="replace", index=False)
print(f"fact_benchmark: {len(df_bench)} rows")

# 8. fact_portfolio
df_port = pd.read_csv(RAW/"09_portfolio_holdings.csv")
df_port = df_port[df_port["amfi_code"].isin(df_fund["amfi_code"])]
df_port.to_sql("fact_portfolio", conn, if_exists="replace", index=False)
print(f"fact_portfolio: {len(df_port)} rows")

# 9. fact_performance (compute & load)
from scipy import stats as scipy_stats
RF_DAILY = 0.065/252
perf_rows = []
for code, grp in df_nav.groupby("amfi_code"):
    grp = grp.sort_values("date")
    nav = grp["nav"].values
    ret = pd.Series(nav).pct_change().dropna()
    if len(ret) < 60: continue
    n = len(grp)
    def cagr(years):
        nd = int(years*252)
        if n < nd: return np.nan
        s = nav[-nd]; e = nav[-1]
        return (e/s)**(252/nd)-1
    sharpe = (ret.mean()-RF_DAILY)/ret.std()*np.sqrt(252) if ret.std()>0 else np.nan
    dd_ret = ret[ret<0]
    sortino = (ret.mean()-RF_DAILY)*252/(dd_ret.std()*np.sqrt(252)) if len(dd_ret)>2 else np.nan
    mdd = float(((pd.Series(nav)/pd.Series(nav).cummax())-1).min())*100
    var95 = float(np.percentile(ret,5))*100
    cvar95 = float(ret[ret<=np.percentile(ret,5)].mean())*100
    perf_rows.append({
        "amfi_code":code,"as_of_date":"2026-05-30",
        "cagr_1yr_pct":round(cagr(1)*100,2) if not np.isnan(cagr(1)) else None,
        "cagr_3yr_pct":round(cagr(3)*100,2) if not np.isnan(cagr(3)) else None,
        "cagr_5yr_pct":round(cagr(5)*100,2) if not np.isnan(cagr(5)) else None,
        "sharpe_ratio":round(sharpe,2),"sortino_ratio":round(sortino,2) if not np.isnan(sortino) else None,
        "alpha_annualised":None,"beta":None,
        "max_drawdown_pct":round(mdd,2),"std_dev_ann_pct":round(ret.std()*np.sqrt(252)*100,2),
        "var_95_daily_pct":round(var95,3),"cvar_95_daily_pct":round(cvar95,3),
        "tracking_error_pct":None,"composite_score":None,"score_rank":None,
    })
df_perf = pd.DataFrame(perf_rows)
# composite score
df_perf["composite_score"] = (
    df_perf["cagr_3yr_pct"].rank(pct=True,na_option="bottom")*0.30 +
    df_perf["sharpe_ratio"].rank(pct=True,na_option="bottom")*0.25 +
    df_perf["max_drawdown_pct"].rank(pct=True,na_option="bottom")*0.15
)*100
df_perf["score_rank"] = df_perf["composite_score"].rank(ascending=False).astype(int)
df_perf.to_sql("fact_performance", conn, if_exists="replace", index=False)
df_perf.to_csv(PROC/"fund_metrics.csv", index=False)
print(f"fact_performance: {len(df_perf)} rows")

# agg_monthly_nav
monthly = df_nav_db.copy()
monthly["year_month"] = monthly["nav_date"].str[:7]
agg = monthly.groupby(["amfi_code","year_month"]).agg(
    open_nav=("nav_inr","first"), close_nav=("nav_inr","last"),
    high_nav=("nav_inr","max"),  low_nav=("nav_inr","min"),
    trading_days=("nav_inr","count")).reset_index()
agg["monthly_return"] = (agg["close_nav"]-agg["open_nav"])/agg["open_nav"]
agg.to_sql("agg_monthly_nav", conn, if_exists="replace", index=False)
print(f"agg_monthly_nav: {len(agg)} rows")

conn.commit()
conn.close()
print(f"\n✅ Database ready: {DB}")
