"""
Bluestock Fintech — Fund Recommender (D6 / B4)
Input: investor risk appetite → Output: Top 3 funds by Sharpe within risk grade
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"


RISK_MAP = {
    "Low":      ["Low", "Moderately Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}

HORIZON_MAP = {
    "short":  (1, "cagr_1yr_pct"),
    "medium": (3, "cagr_3yr_pct"),
    "long":   (5, "cagr_5yr_pct"),
}


def recommend(risk_appetite: str = "Moderate",
              horizon: str = "long",
              top_n: int = 3) -> pd.DataFrame:
    """
    Returns top_n fund recommendations.

    Parameters
    ----------
    risk_appetite : 'Low' | 'Moderate' | 'High'
    horizon       : 'short' (1yr) | 'medium' (3yr) | 'long' (5yr)
    top_n         : number of recommendations
    """
    risk_appetite = risk_appetite.capitalize()
    horizon       = horizon.lower()

    if risk_appetite not in RISK_MAP:
        raise ValueError(f"risk_appetite must be one of {list(RISK_MAP.keys())}")
    if horizon not in HORIZON_MAP:
        raise ValueError(f"horizon must be one of {list(HORIZON_MAP.keys())}")

    # Load data
    df_fund = pd.read_csv(RAW / "01_fund_master.csv")
    df_fund = df_fund.drop_duplicates(subset=["amfi_code"])

    metrics_path = PROC / "fund_metrics.csv"
    if metrics_path.exists():
        df_m = pd.read_csv(metrics_path)
    else:
        df_m = pd.read_csv(RAW / "07_scheme_performance.csv")
        df_m = df_m.rename(columns={
            "return_1yr_pct": "cagr_1yr_pct",
            "return_3yr_pct": "cagr_3yr_pct",
            "return_5yr_pct": "cagr_5yr_pct",
        })

    df = df_fund.merge(df_m, on="amfi_code", how="inner")

    # Filter by risk
    allowed_risk = RISK_MAP[risk_appetite]
    df = df[df["risk_category"].isin(allowed_risk)]

    # Score: 50% Sharpe + 30% CAGR for horizon + 20% low expense
    _, cagr_col = HORIZON_MAP[horizon]
    if cagr_col not in df.columns:
        cagr_col = "cagr_3yr_pct"

    df = df.dropna(subset=["sharpe_ratio", cagr_col])
    if df.empty:
        print(f"No funds found for risk={risk_appetite}, horizon={horizon}")
        return pd.DataFrame()

    df["_score"] = (
        df["sharpe_ratio"].rank(pct=True) * 0.50 +
        df[cagr_col].rank(pct=True) * 0.30 +
        df["expense_ratio_pct"].rank(pct=True, ascending=False) * 0.20
    )

    top = df.nlargest(top_n, "_score")[
        ["amfi_code", "scheme_name", "fund_house", "sub_category",
         "risk_category", "sharpe_ratio", cagr_col,
         "expense_ratio_pct", "max_drawdown_pct"]
    ].reset_index(drop=True)
    top.index += 1

    return top


def herfindahl_hirschman_index(df_port: pd.DataFrame) -> pd.DataFrame:
    """Compute sector HHI per fund (concentration risk)"""
    def hhi(weights):
        w = np.array(weights) / 100.0
        return round(float((w ** 2).sum()), 4)

    result = (
        df_port.groupby(["amfi_code", "sector"])["weight_pct"]
        .sum()
        .reset_index()
        .groupby("amfi_code")["weight_pct"]
        .apply(hhi)
        .reset_index()
        .rename(columns={"weight_pct": "sector_hhi"})
    )
    result["concentration"] = pd.cut(
        result["sector_hhi"],
        bins=[0, 0.10, 0.18, 1.0],
        labels=["Diversified", "Moderate", "Concentrated"]
    )
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("BLUESTOCK FINTECH — FUND RECOMMENDER")
    print("=" * 60)

    for risk in ["Low", "Moderate", "High"]:
        print(f"\n📊 Risk Appetite: {risk} | Horizon: Long (5yr)")
        print("-" * 60)
        recs = recommend(risk_appetite=risk, horizon="long", top_n=3)
        if not recs.empty:
            print(recs.to_string())

    # Sector HHI
    port_path = RAW / "09_portfolio_holdings.csv"
    if port_path.exists():
        df_port = pd.read_csv(port_path)
        hhi_df = herfindahl_hirschman_index(df_port)
        hhi_df.to_csv(PROC / "sector_hhi.csv", index=False)
        print(f"\n✅ Sector HHI saved → {PROC / 'sector_hhi.csv'}")
        print(hhi_df.to_string(index=False))
