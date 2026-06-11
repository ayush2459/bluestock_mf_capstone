#!/usr/bin/env python3
"""
run_pipeline.py — Master ETL Orchestrator for Bluestock MF Analytics Platform
===============================================================================
Entry point for the complete Extract → Transform → Enrich → Load → Validate
pipeline for 40 Indian equity mutual fund schemes.

Usage
-----
    python run_pipeline.py --stage all
    python run_pipeline.py --stage extract --funds 119551,118989
    python run_pipeline.py --stage metrics --start-date 2022-01-01

Exit Codes
----------
    0  — All stages completed successfully, all validation checks passed
    1  — One or more validation checks failed (data quality issue)
    2  — Network error during extraction (API unreachable)
    3  — Database error (write failure, schema mismatch)
    10 — Invalid CLI arguments
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Logging setup ────────────────────────────────────────────────────────────
def configure_logging(level: str) -> logging.Logger:
    """
    Configure the root logger with a timestamped formatter.

    Parameters
    ----------
    level : str
        Logging verbosity — one of DEBUG, INFO, WARNING, ERROR.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("pipeline")


# ── CLI argument parser ──────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for run_pipeline.py.

    Returns
    -------
    argparse.ArgumentParser
        Fully configured parser with all supported flags.
    """
    parser = argparse.ArgumentParser(
        prog="run_pipeline.py",
        description="Bluestock MF Analytics — Master ETL Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  Run full pipeline:
    python run_pipeline.py --stage all

  Extract only:
    python run_pipeline.py --stage extract

  Re-run metrics for specific schemes:
    python run_pipeline.py --stage metrics --funds 119551,118989,120503

  Custom date range:
    python run_pipeline.py --stage all --start-date 2022-01-01 --end-date 2023-12-31

  Verbose debug output:
    python run_pipeline.py --stage validate --log-level DEBUG
        """,
    )
    parser.add_argument(
        "--stage",
        choices=["extract", "transform", "metrics", "load", "validate", "scorecard", "all"],
        default="all",
        help="Pipeline stage to execute. Default: all",
    )
    parser.add_argument(
        "--funds",
        default="all",
        help="Comma-separated AMFI scheme codes to process, or 'all'. Default: all",
    )
    parser.add_argument(
        "--start-date",
        default="2021-01-01",
        metavar="YYYY-MM-DD",
        help="Data start date. Default: 2021-01-01",
    )
    parser.add_argument(
        "--end-date",
        default="2024-12-31",
        metavar="YYYY-MM-DD",
        help="Data end date. Default: 2024-12-31",
    )
    parser.add_argument(
        "--db-path",
        default="mutual_funds.db",
        metavar="PATH",
        help="Path to SQLite database. Default: mutual_funds.db",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        metavar="DIR",
        help="Directory for raw API output. Default: data/raw",
    )
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        metavar="DIR",
        help="Directory for cleaned CSV/parquet files. Default: data/processed",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be executed without actually running any stage.",
    )
    return parser


# ── Stage runners ────────────────────────────────────────────────────────────
def run_extract(args, logger: logging.Logger) -> None:
    """
    Execute the extraction stage: fetch raw NAV data from AMFI and MFAPI.in.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (funds, start_date, end_date, raw_dir).
    logger : logging.Logger
        Logger instance for status output.

    Raises
    ------
    SystemExit
        Exit code 2 if any network request fails after retries.
    """
    logger.info("[EXTRACT] Starting NAV data extraction...")
    t0 = time.time()
    try:
        from src.extract_nav import extract_all_funds
        fund_list = None if args.funds == "all" else args.funds.split(",")
        result = extract_all_funds(
            fund_codes=fund_list,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=Path(args.raw_dir),
        )
        elapsed = time.time() - t0
        logger.info("[EXTRACT] Done — %d schemes fetched in %.1fs", result["schemes"], elapsed)
    except ConnectionError as exc:
        logger.error("[EXTRACT] Network error: %s", exc)
        sys.exit(2)


def run_transform(args, logger: logging.Logger) -> None:
    """
    Execute the transform stage: clean raw data, compute daily returns, merge benchmark.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (raw_dir, processed_dir).
    logger : logging.Logger
        Logger instance for status output.
    """
    logger.info("[TRANSFORM] Cleaning and computing returns...")
    t0 = time.time()
    from src.transform import transform_all
    result = transform_all(
        raw_dir=Path(args.raw_dir),
        output_dir=Path(args.processed_dir),
    )
    elapsed = time.time() - t0
    logger.info(
        "[TRANSFORM] Done — %d rows processed, %d imputed gaps in %.1fs",
        result["rows"], result["imputed"], elapsed,
    )


def run_metrics(args, logger: logging.Logger) -> None:
    """
    Execute the metric computation stage: calculate 8 performance metrics.

    Metrics computed: Sharpe, Sortino, Jensen's Alpha, Beta, Treynor,
    Max Drawdown, VaR (95%), CAGR.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (processed_dir).
    logger : logging.Logger
        Logger instance for status output.
    """
    logger.info("[METRICS] Computing 8 performance metrics per fund...")
    t0 = time.time()
    from src.metrics import compute_all_metrics
    result = compute_all_metrics(data_dir=Path(args.processed_dir))
    elapsed = time.time() - t0
    logger.info(
        "[METRICS] Done — %d funds × 8 metrics computed in %.2fs",
        result["funds"], elapsed,
    )


def run_load(args, logger: logging.Logger) -> None:
    """
    Execute the load stage: upsert all processed data into SQLite.

    Uses WAL (Write-Ahead Logging) mode for concurrent read support.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (db_path, processed_dir).
    logger : logging.Logger
        Logger instance for status output.

    Raises
    ------
    SystemExit
        Exit code 3 if database write fails.
    """
    logger.info("[LOAD] Writing to %s...", args.db_path)
    t0 = time.time()
    try:
        from src.load_db import load_to_sqlite
        result = load_to_sqlite(
            data_dir=Path(args.processed_dir),
            db_path=Path(args.db_path),
        )
        elapsed = time.time() - t0
        logger.info(
            "[LOAD] Done — %d tables updated, %d total rows in %.1fs",
            result["tables"], result["total_rows"], elapsed,
        )
    except Exception as exc:
        logger.error("[LOAD] Database error: %s", exc)
        sys.exit(3)


def run_validate(args, logger: logging.Logger) -> None:
    """
    Execute the validation stage: run 12 data quality checks.

    Checks include: NAV continuity, return outliers, metric boundaries,
    referential integrity, benchmark correlation sanity.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (db_path).
    logger : logging.Logger
        Logger instance for status output.

    Raises
    ------
    SystemExit
        Exit code 1 if any validation check fails.
    """
    logger.info("[VALIDATE] Running 12 quality checks...")
    from src.validate import run_all_checks
    result = run_all_checks(db_path=Path(args.db_path))
    passed = result["passed"]
    total  = result["total"]
    if passed < total:
        logger.warning(
            "[VALIDATE] %d/%d checks passed — see validation_log table for details",
            passed, total,
        )
        sys.exit(1)
    logger.info("[VALIDATE] All %d/%d checks passed.", passed, total)


def run_scorecard(args, logger: logging.Logger) -> None:
    """
    Execute the scorecard stage: compute composite weighted ranks for all funds.

    Scoring weights: CAGR 25%, Sharpe 25%, Sortino 20%, Alpha 15%,
    Max Drawdown 10%, VaR 5%. Metrics normalised [0, 1] before weighting.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments (db_path).
    logger : logging.Logger
        Logger instance for status output.
    """
    logger.info("[SCORECARD] Computing composite fund rankings...")
    t0 = time.time()
    from src.scorecard import compute_scorecard
    result = compute_scorecard(db_path=Path(args.db_path))
    elapsed = time.time() - t0
    logger.info(
        "[SCORECARD] Done — top fund: %s (score %.1f) in %.2fs",
        result["top_fund"], result["top_score"], elapsed,
    )


# ── Main orchestrator ────────────────────────────────────────────────────────
STAGE_RUNNERS = {
    "extract":   run_extract,
    "transform": run_transform,
    "metrics":   run_metrics,
    "load":      run_load,
    "validate":  run_validate,
    "scorecard": run_scorecard,
}

FULL_PIPELINE = ["extract", "transform", "metrics", "load", "validate", "scorecard"]


def main() -> None:
    """
    Parse CLI arguments and dispatch the requested pipeline stage(s).

    This is the single entry point for all pipeline operations. In --dry-run
    mode, stages are printed without execution.
    """
    parser = build_parser()
    args = parser.parse_args()
    logger = configure_logging(args.log_level)

    # Validate date arguments
    for attr, flag in [("start_date", "--start-date"), ("end_date", "--end-date")]:
        val = getattr(args, attr.replace("-", "_"))
        try:
            datetime.strptime(val, "%Y-%m-%d")
        except ValueError:
            logger.error("Invalid date for %s: '%s'. Expected YYYY-MM-DD.", flag, val)
            sys.exit(10)

    stages = FULL_PIPELINE if args.stage == "all" else [args.stage]

    logger.info("=" * 60)
    logger.info("Bluestock MF Analytics Platform — Pipeline v1.0")
    logger.info("Stages: %s", " → ".join(s.upper() for s in stages))
    logger.info("DB: %s | Funds: %s | %s → %s", args.db_path, args.funds, args.start_date, args.end_date)
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("[DRY RUN] Would execute: %s", stages)
        return

    pipeline_start = time.time()
    for stage in stages:
        STAGE_RUNNERS[stage](args, logger)

    total_elapsed = time.time() - pipeline_start
    logger.info("=" * 60)
    logger.info("Pipeline complete — total time: %.1fs | Exit code: 0", total_elapsed)
    logger.info("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
