"""
Bluestock Fintech — Performance & Risk Metrics Engine (D4)
Computes CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR, CVaR
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

BASE     = Path(__file__).resolve().parent.parent
PROC     = BASE / "data" / "processed"
RAW      = BASE / "data" / "raw"
PROC.mkdir(parents=True, exist_ok=True)

RF_ANNUAL   = 0.065          # RBI repo rate proxy
RF_DAILY    = RF_ANNUAL / 252
TRADING_DAYS = 252


def load_nav() -> pd.DataFrame:
    """Load processed NAV or fall back to raw"""
    p = PROC / "nav_master.csv"
    if p.exists():
        df = pd.read_csv(p, parse_dates=["date"])
    else:
        df = pd.read_csv(RAW / "02_nav_history.csv", parse_dates=["date"])
        df = df.rename(columns={"nav": "nav_inr"})
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    return df


def load_benchmark() -> pd.DataFrame:
    df = pd.read_csv(RAW / "10_benchmark_indices.csv", parse_dates=["date"])
    nifty = df[df["index_name"] == "Nifty100"].copy()
    nifty = nifty.sort_values("date").set_index("date")["close_value"]
    nifty_ret = nifty.pct_change().dropna()
    return nifty_ret


def compute_cagr(nav_series: pd.Series, n_trading_days: int) -> float:
    """CAGR using actual trading days, not calendar days"""
    if len(nav_series) < 2 or nav_series.iloc[0] <= 0:
        return np.nan
    years = n_trading_days / TRADING_DAYS
    return (nav_series.iloc[-1] / nav_series.iloc[0]) ** (1 / years) - 1


def compute_sharpe(returns: pd.Series) -> float:
    excess = returns - RF_DAILY
    if returns.std() == 0:
        return np.nan
    return float(excess.mean() / returns.std() * np.sqrt(TRADING_DAYS))


def compute_sortino(returns: pd.Series) -> float:
    excess = returns - RF_DAILY
    downside = returns[returns < 0]
    if len(downside) < 2:
        return np.nan
    downside_std = downside.std() * np.sqrt(TRADING_DAYS)
    if downside_std == 0:
        return np.nan
    return float(excess.mean() * TRADING_DAYS / downside_std)


def compute_max_drawdown(nav_series: pd.Series) -> float:
    roll_max = nav_series.cummax()
    drawdown = (nav_series - roll_max) / roll_max
    return float(drawdown.min())


def compute_alpha_beta(fund_ret: pd.Series, bench_ret: pd.Series):
    aligned = pd.concat([fund_ret, bench_ret], axis=1).dropna()
    if len(aligned) < 30:
        return np.nan, np.nan
    slope, intercept, *_ = stats.linregress(aligned.iloc[:, 1], aligned.iloc[:, 0])
    alpha = intercept * TRADING_DAYS   # annualised
    beta  = slope
    return round(alpha, 4), round(beta, 4)


def compute_var_cvar(returns: pd.Series, confidence: float = 0.95):
    """Historical VaR and CVaR at given confidence level"""
    threshold = np.percentile(returns.dropna(), (1 - confidence) * 100)
    cvar = returns[returns <= threshold].mean()
    return float(threshold), float(cvar)


def compute_tracking_error(fund_ret: pd.Series, bench_ret: pd.Series) -> float:
    aligned = pd.concat([fund_ret, bench_ret], axis=1).dropna()
    diff = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    return float(diff.std() * np.sqrt(TRADING_DAYS))


def run_all_metrics():
    print("Loading data …")
    df_nav   = load_nav()
    bench_ret = load_benchmark()

    nav_col = "nav_inr" if "nav_inr" in df_nav.columns else "nav"

    records = []
    for code, grp in df_nav.groupby("amfi_code"):
        grp = grp.sort_values("date").dropna(subset=[nav_col])
        if len(grp) < 60:
            continue

        nav    = grp[nav_col]
        ret    = nav.pct_change().dropna()
        dates  = grp["date"]
        n_days = len(grp)

        # 1-year, 3-year, 5-year windows
        def _cagr_window(years):
            n = int(years * TRADING_DAYS)
            if len(grp) < n:
                return np.nan
            sub = grp.tail(n)[nav_col]
            return compute_cagr(sub, n)

        cagr_1y = _cagr_window(1)
        cagr_3y = _cagr_window(3)
        cagr_5y = _cagr_window(5)

        sharpe  = compute_sharpe(ret)
        sortino = compute_sortino(ret)
        mdd     = compute_max_drawdown(nav)
        alpha, beta = compute_alpha_beta(ret.set_axis(grp["date"].iloc[1:]), bench_ret)
        var95, cvar95 = compute_var_cvar(ret)
        te = compute_tracking_error(ret.set_axis(grp["date"].iloc[1:]), bench_ret)

        records.append({
            "amfi_code":          code,
            "n_trading_days":     n_days,
            "cagr_1yr_pct":       round(cagr_1y * 100, 2) if not np.isnan(cagr_1y) else np.nan,
            "cagr_3yr_pct":       round(cagr_3y * 100, 2) if not np.isnan(cagr_3y) else np.nan,
            "cagr_5yr_pct":       round(cagr_5y * 100, 2) if not np.isnan(cagr_5y) else np.nan,
            "sharpe_ratio":       round(sharpe,   2),
            "sortino_ratio":      round(sortino,  2) if not np.isnan(sortino) else np.nan,
            "alpha_annualised":   round(alpha,    4) if not np.isnan(alpha) else np.nan,
            "beta":               round(beta,     3) if not np.isnan(beta) else np.nan,
            "max_drawdown_pct":   round(mdd * 100, 2),
            "std_dev_ann_pct":    round(ret.std() * np.sqrt(TRADING_DAYS) * 100, 2),
            "var_95_daily_pct":   round(var95  * 100, 3),
            "cvar_95_daily_pct":  round(cvar95 * 100, 3),
            "tracking_error_pct": round(te * 100, 2),
        })
        print(f"  ✓ {code}: Sharpe={round(sharpe,2)}, MDD={round(mdd*100,1)}%, "
              f"Alpha={round(alpha,3) if not np.isnan(alpha) else 'N/A'}")

    df_metrics = pd.DataFrame(records)

    # Fund scorecard (composite 0-100)
    rank_cols = {
        "cagr_3yr_pct":       ("max", 0.30),
        "sharpe_ratio":       ("max", 0.25),
        "alpha_annualised":   ("max", 0.20),
        "max_drawdown_pct":   ("max", 0.15),   # less negative = better
    }
    score = pd.Series(0.0, index=df_metrics.index)
    for col, (direction, weight) in rank_cols.items():
        s = df_metrics[col].rank(pct=True, na_option="bottom")
        score += s * weight
    # expense ratio (lower = better) - merge from fund master
    try:
        df_fm = pd.read_csv(RAW / "01_fund_master.csv")
        er_map = df_fm.groupby("amfi_code")["expense_ratio_pct"].mean()
        df_metrics["expense_ratio_pct"] = df_metrics["amfi_code"].map(er_map)
        er_rank = df_metrics["expense_ratio_pct"].rank(pct=True, ascending=False, na_option="bottom")
        score += er_rank * 0.10
    except Exception:
        pass
    df_metrics["composite_score"] = (score * 100).round(1)
    df_metrics["score_rank"] = df_metrics["composite_score"].rank(ascending=False).astype(int)

    # Save outputs
    df_metrics.to_csv(PROC / "fund_metrics.csv", index=False)
    df_metrics[["amfi_code","cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct"]].to_csv(
        PROC / "cagr_report.csv", index=False)
    df_metrics[["amfi_code","sharpe_ratio","sortino_ratio","std_dev_ann_pct"]].to_csv(
        PROC / "sharpe_sortino.csv", index=False)
    df_metrics[["amfi_code","alpha_annualised","beta","tracking_error_pct"]].to_csv(
        PROC / "alpha_beta.csv", index=False)
    df_metrics[["amfi_code","max_drawdown_pct"]].to_csv(PROC / "max_drawdown.csv", index=False)
    df_metrics[["amfi_code","var_95_daily_pct","cvar_95_daily_pct"]].to_csv(
        PROC / "var_cvar_report.csv", index=False)
    df_metrics[["amfi_code","composite_score","score_rank"]].to_csv(
        PROC / "fund_scorecard.csv", index=False)

    print(f"\n✅ Metrics computed for {len(df_metrics)} schemes")
    print(f"   Outputs saved to {PROC}")
    return df_metrics


if __name__ == "__main__":
    run_all_metrics()
