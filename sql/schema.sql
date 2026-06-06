-- Dimension: Scheme master
    CREATE TABLE IF NOT EXISTS dim_scheme (
        scheme_code     TEXT PRIMARY KEY,
        scheme_name     TEXT NOT NULL,
        fund_house      TEXT,
        scheme_type     TEXT,
        scheme_category TEXT,
        created_at      TEXT DEFAULT (datetime('now'))
    );

    -- Fact: Daily NAV
    CREATE TABLE IF NOT EXISTS fact_nav (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code     TEXT NOT NULL REFERENCES dim_scheme(scheme_code),
        nav_date        TEXT NOT NULL,
        nav_inr         REAL NOT NULL,
        daily_return    REAL,
        nav_52w_high    REAL,
        nav_52w_low     REAL,
        rolling_30d_vol REAL,
        is_trading_day  INTEGER DEFAULT 1,
        loaded_at       TEXT DEFAULT (datetime('now')),
        UNIQUE(scheme_code, nav_date)
    );

    -- Aggregate: Monthly summary
    CREATE TABLE IF NOT EXISTS agg_monthly (
        scheme_code     TEXT NOT NULL REFERENCES dim_scheme(scheme_code),
        year_month      TEXT NOT NULL,
        open_nav        REAL,
        close_nav       REAL,
        high_nav        REAL,
        low_nav         REAL,
        monthly_return  REAL,
        trading_days    INTEGER,
        PRIMARY KEY (scheme_code, year_month)
    );

    -- Metadata: ETL runs
    CREATE TABLE IF NOT EXISTS etl_runs (
        run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_at          TEXT DEFAULT (datetime('now')),
        schemes_fetched INTEGER,
        rows_inserted   INTEGER,
        status          TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_nav_date   ON fact_nav(nav_date);
    CREATE INDEX IF NOT EXISTS idx_nav_scheme ON fact_nav(scheme_code);