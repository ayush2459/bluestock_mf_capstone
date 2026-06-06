"""
Bluestock Fintech — Mutual Fund Analytics Platform
D1: ETL Pipeline Script
Fetches NAV data from mfapi.in, cleans it, and loads into SQLite
"""

import os
import sys
import time
import logging
import sqlite3
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
from typing import Optional

# ── Paths (no hard-coding) ───────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw"
PROC_DIR   = BASE_DIR / "data" / "processed"
DB_DIR     = BASE_DIR / "data" / "db"
SQL_DIR    = BASE_DIR / "sql"

for d in (RAW_DIR, PROC_DIR, DB_DIR, SQL_DIR):
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "bluestock_mf.db"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "etl.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

# ── Fund universe (scheme codes from mfapi.in) ───────────────────────────────
FUND_UNIVERSE = {
    "120503": "Mirae Asset Large Cap Fund - Direct Growth",
    "119598": "Axis Bluechip Fund - Direct Growth",
    "120465": "Parag Parikh Flexi Cap Fund - Direct Growth",
    "120716": "Mirae Asset Emerging Bluechip - Direct Growth",
    "118834": "SBI Small Cap Fund - Direct Growth",
    "125497": "HDFC Mid-Cap Opportunities - Direct Growth",
    "120847": "Kotak Emerging Equity - Direct Growth",
    "119775": "Nippon India Small Cap - Direct Growth",
    "125354": "ICICI Pru Technology Fund - Direct Growth",
    "120586": "Axis Long Term Equity (ELSS) - Direct Growth",
}

MFAPI_BASE = "https://api.mfapi.in/mf"


# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_nav_history(scheme_code: str, retries: int = 3) -> Optional[pd.DataFrame]:
    """Fetch complete NAV history for one scheme from mfapi.in"""
    url = f"{MFAPI_BASE}/{scheme_code}"
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            meta = payload.get("meta", {})
            nav_data = payload.get("data", [])

            if not nav_data:
                log.warning(f"No NAV data returned for {scheme_code}")
                return None

            df = pd.DataFrame(nav_data)
            df["scheme_code"]   = scheme_code
            df["scheme_name"]   = meta.get("scheme_name", FUND_UNIVERSE.get(scheme_code, ""))
            df["fund_house"]    = meta.get("fund_house", "")
            df["scheme_type"]   = meta.get("scheme_type", "")
            df["scheme_category"] = meta.get("scheme_category", "")
            df["date"]          = pd.to_datetime(df["date"], format="%d-%m-%Y", dayfirst=True)
            df["nav"]           = pd.to_numeric(df["nav"], errors="coerce")
            df = df.dropna(subset=["nav"])
            df = df.sort_values("date").reset_index(drop=True)
            log.info(f"  ✓ {scheme_code}: {len(df):,} rows fetched")
            return df

        except requests.exceptions.RequestException as exc:
            log.warning(f"  Attempt {attempt}/{retries} failed for {scheme_code}: {exc}")
            if attempt < retries:
                time.sleep(2 ** attempt)

    log.error(f"  ✗ All retries exhausted for {scheme_code}")
    return None


def build_full_date_range(df: pd.DataFrame) -> pd.DataFrame:
    """Reindex to full calendar range and forward-fill NAV (handles holidays/weekends)"""
    df = df.set_index("date")
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_idx)
    # forward fill NAV only (not categorical cols)
    df["nav"] = df["nav"].ffill()
    # back-fill metadata cols
    meta_cols = ["scheme_code", "scheme_name", "fund_house", "scheme_type", "scheme_category"]
    df[meta_cols] = df[meta_cols].bfill().ffill()
    df.index.name = "date"
    df = df.reset_index()
    df["is_trading_day"] = df["date"].isin(df[df["nav"].notna()]["date"])  # approximate flag
    return df


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily returns, rolling metrics per scheme"""
    df = df.sort_values(["scheme_code", "date"])
    df["daily_return"]   = df.groupby("scheme_code")["nav"].pct_change()
    df["nav_52w_high"]   = df.groupby("scheme_code")["nav"].transform(lambda x: x.rolling(252, min_periods=1).max())
    df["nav_52w_low"]    = df.groupby("scheme_code")["nav"].transform(lambda x: x.rolling(252, min_periods=1).min())
    df["rolling_30d_vol"]= df.groupby("scheme_code")["daily_return"].transform(
                               lambda x: x.rolling(30, min_periods=10).std() * np.sqrt(252))
    return df


# ── Database ──────────────────────────────────────────────────────────────────
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    schema_sql = """
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
    """
    conn.executescript(schema_sql)
    conn.commit()
    log.info("Schema created / verified ✓")

    # Also write schema.sql for version control
    schema_file = SQL_DIR / "schema.sql"
    schema_file.write_text(schema_sql.strip())


def upsert_scheme(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute("""
        INSERT INTO dim_scheme (scheme_code, scheme_name, fund_house, scheme_type, scheme_category)
        VALUES (:scheme_code, :scheme_name, :fund_house, :scheme_type, :scheme_category)
        ON CONFLICT(scheme_code) DO UPDATE SET
            scheme_name     = excluded.scheme_name,
            fund_house      = excluded.fund_house,
            scheme_type     = excluded.scheme_type,
            scheme_category = excluded.scheme_category
    """, row)


def bulk_insert_nav(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    records = []
    for _, r in df.iterrows():
        records.append({
            "scheme_code":     r["scheme_code"],
            "nav_date":        r["date"].strftime("%Y-%m-%d"),
            "nav_inr":         r["nav"],
            "daily_return":    r.get("daily_return"),
            "nav_52w_high":    r.get("nav_52w_high"),
            "nav_52w_low":     r.get("nav_52w_low"),
            "rolling_30d_vol": r.get("rolling_30d_vol"),
            "is_trading_day":  int(r.get("is_trading_day", 1)),
        })
    conn.executemany("""
        INSERT OR IGNORE INTO fact_nav
            (scheme_code, nav_date, nav_inr, daily_return, nav_52w_high,
             nav_52w_low, rolling_30d_vol, is_trading_day)
        VALUES
            (:scheme_code, :nav_date, :nav_inr, :daily_return, :nav_52w_high,
             :nav_52w_low, :rolling_30d_vol, :is_trading_day)
    """, records)
    return len(records)


def rebuild_monthly_agg(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM agg_monthly;")
    conn.execute("""
        INSERT INTO agg_monthly (scheme_code, year_month, open_nav, close_nav,
                                  high_nav, low_nav, monthly_return, trading_days)
        SELECT
            scheme_code,
            strftime('%Y-%m', nav_date)          AS year_month,
            FIRST_VALUE(nav_inr) OVER w           AS open_nav,
            LAST_VALUE(nav_inr)  OVER w           AS close_nav,
            MAX(nav_inr)         OVER w           AS high_nav,
            MIN(nav_inr)         OVER w           AS low_nav,
            (LAST_VALUE(nav_inr) OVER w - FIRST_VALUE(nav_inr) OVER w)
                / FIRST_VALUE(nav_inr) OVER w     AS monthly_return,
            COUNT(*)             OVER w           AS trading_days
        FROM fact_nav
        WHERE is_trading_day = 1
        WINDOW w AS (PARTITION BY scheme_code, strftime('%Y-%m', nav_date)
                     ORDER BY nav_date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
        GROUP BY scheme_code, year_month
    """)
    conn.commit()
    log.info("Monthly aggregates rebuilt ✓")


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_etl(scheme_codes: Optional[list] = None) -> None:
    start = datetime.now()
    log.info("=" * 60)
    log.info("Bluestock MF ETL Pipeline started")
    log.info(f"Target DB: {DB_PATH}")

    codes = scheme_codes or list(FUND_UNIVERSE.keys())
    conn = get_connection()

    try:
        create_schema(conn)

        all_dfs, schemes_ok, total_rows = [], 0, 0

        for code in codes:
            log.info(f"Fetching scheme {code} …")
            raw = fetch_nav_history(code)
            if raw is None:
                continue

            # Save raw CSV
            raw.to_csv(RAW_DIR / f"nav_{code}_raw.csv", index=False)

            # Clean & enrich
            cleaned = build_full_date_range(raw)
            all_dfs.append(cleaned)
            schemes_ok += 1

            # Upsert dimension
            upsert_scheme(conn, {
                "scheme_code":     cleaned["scheme_code"].iloc[0],
                "scheme_name":     cleaned["scheme_name"].iloc[0],
                "fund_house":      cleaned["fund_house"].iloc[0],
                "scheme_type":     cleaned["scheme_type"].iloc[0],
                "scheme_category": cleaned["scheme_category"].iloc[0],
            })

        if not all_dfs:
            log.error("No data fetched — aborting.")
            return

        # Combine, compute metrics, save processed CSV
        master = pd.concat(all_dfs, ignore_index=True)
        master = compute_derived_metrics(master)
        master.to_csv(PROC_DIR / "nav_master.csv", index=False)
        log.info(f"Processed CSV saved → {PROC_DIR / 'nav_master.csv'}")

        # Load into DB
        for code, grp in master.groupby("scheme_code"):
            rows = bulk_insert_nav(conn, grp)
            total_rows += rows
        conn.commit()
        log.info(f"Inserted {total_rows:,} NAV rows into fact_nav ✓")

        rebuild_monthly_agg(conn)

        # Log ETL run
        elapsed = (datetime.now() - start).seconds
        conn.execute("""
            INSERT INTO etl_runs (schemes_fetched, rows_inserted, status)
            VALUES (?, ?, ?)
        """, (schemes_ok, total_rows, "SUCCESS"))
        conn.commit()

        log.info(f"ETL complete — {schemes_ok} schemes, {total_rows:,} rows, {elapsed}s elapsed")

    except Exception as exc:
        log.exception(f"ETL FAILED: {exc}")
        conn.execute("INSERT INTO etl_runs (schemes_fetched, rows_inserted, status) VALUES (0,0,'FAILED')")
        conn.commit()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_etl()
