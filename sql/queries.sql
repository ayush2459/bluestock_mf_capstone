-- ============================================================
-- Bluestock Fintech — Analytical SQL Queries (queries.sql)
-- ============================================================

-- Q1: Top 10 funds by latest composite score
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.expense_ratio_pct,
    p.cagr_3yr_pct,
    p.sharpe_ratio,
    p.composite_score,
    p.score_rank
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.score_rank
LIMIT 10;

-- Q2: Monthly average NAV trend per category
SELECT
    strftime('%Y-%m', n.nav_date)   AS year_month,
    f.sub_category,
    ROUND(AVG(n.nav_inr), 2)        AS avg_nav,
    COUNT(DISTINCT n.amfi_code)     AS num_funds
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY year_month, f.sub_category
ORDER BY year_month, f.sub_category;

-- Q3: SIP inflow YoY growth
SELECT
    month,
    sip_inflow_crore,
    LAG(sip_inflow_crore, 12) OVER (ORDER BY month) AS prev_year_inflow,
    ROUND(
        (sip_inflow_crore - LAG(sip_inflow_crore, 12) OVER (ORDER BY month))
        / LAG(sip_inflow_crore, 12) OVER (ORDER BY month) * 100, 1
    ) AS yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- Q4: Total SIP transaction volume by state (T30 vs B30)
SELECT
    state,
    city_tier,
    COUNT(*)                        AS num_transactions,
    ROUND(SUM(amount_inr)/1e7, 2)  AS total_amount_crore,
    ROUND(AVG(amount_inr), 0)       AS avg_sip_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY state, city_tier
ORDER BY total_amount_crore DESC;

-- Q5: Funds with expense ratio below 0.50% and Sharpe > 0.5
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.expense_ratio_pct,
    p.sharpe_ratio,
    p.cagr_3yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.expense_ratio_pct < 0.50
  AND p.sharpe_ratio > 0.50
ORDER BY p.sharpe_ratio DESC;

-- Q6: AUM market share by fund house (latest quarter)
SELECT
    fund_house,
    aum_lakh_crore,
    ROUND(aum_lakh_crore / SUM(aum_lakh_crore) OVER () * 100, 2) AS market_share_pct
FROM fact_aum
WHERE quarter = (SELECT MAX(quarter) FROM fact_aum)
ORDER BY aum_lakh_crore DESC;

-- Q7: Best performing fund per category (3yr CAGR)
SELECT
    f.sub_category,
    f.scheme_name,
    f.fund_house,
    p.cagr_3yr_pct,
    p.sharpe_ratio,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.cagr_3yr_pct = (
    SELECT MAX(p2.cagr_3yr_pct)
    FROM fact_performance p2
    JOIN dim_fund f2 ON p2.amfi_code = f2.amfi_code
    WHERE f2.sub_category = f.sub_category
)
ORDER BY p.cagr_3yr_pct DESC;

-- Q8: Investor age group vs average SIP amount and fund preference
SELECT
    age_group,
    COUNT(DISTINCT investor_id)     AS num_investors,
    ROUND(AVG(amount_inr), 0)       AS avg_sip_amount,
    ROUND(SUM(amount_inr)/1e7, 2)  AS total_invested_crore,
    COUNT(*)                        AS num_transactions
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY age_group;

-- Q9: Rolling 3-month alpha vs Nifty 100 per fund
WITH monthly_nav AS (
    SELECT
        amfi_code,
        strftime('%Y-%m', nav_date) AS ym,
        AVG(nav_inr)                AS avg_nav
    FROM fact_nav
    GROUP BY amfi_code, ym
),
monthly_ret AS (
    SELECT
        amfi_code,
        ym,
        (avg_nav - LAG(avg_nav) OVER (PARTITION BY amfi_code ORDER BY ym))
            / LAG(avg_nav) OVER (PARTITION BY amfi_code ORDER BY ym) AS monthly_return
    FROM monthly_nav
)
SELECT
    amfi_code,
    ym,
    ROUND(monthly_return * 100, 2) AS monthly_return_pct,
    ROUND(AVG(monthly_return) OVER (
        PARTITION BY amfi_code ORDER BY ym
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) * 100, 2) AS rolling_3m_return_pct
FROM monthly_ret
WHERE monthly_return IS NOT NULL
ORDER BY amfi_code, ym;

-- Q10: Max drawdown funds with worst risk-adjusted returns (flag for review)
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.risk_category,
    p.max_drawdown_pct,
    p.sharpe_ratio,
    p.cagr_3yr_pct,
    p.var_95_daily_pct,
    CASE
        WHEN p.sharpe_ratio < 0.3 AND p.max_drawdown_pct < -25 THEN 'HIGH RISK - REVIEW'
        WHEN p.sharpe_ratio < 0.5 AND p.max_drawdown_pct < -20 THEN 'MODERATE RISK'
        ELSE 'ACCEPTABLE'
    END AS risk_flag
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.max_drawdown_pct ASC
LIMIT 15;
