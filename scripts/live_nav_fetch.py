"""
Bluestock Fintech — Live NAV Fetcher (B1 Bonus)
Designed to run daily as a cron job at 8 PM weekdays.
Cron line: 0 20 * * 1-5 /usr/bin/python3 /path/to/scripts/live_nav_fetch.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.etl_pipeline import run_etl, FUND_UNIVERSE, log

if __name__ == "__main__":
    today = datetime.today()
    if today.weekday() >= 5:
        log.info(f"Today is {today.strftime('%A')} — skipping (weekend).")
        sys.exit(0)

    log.info(f"Live NAV fetch triggered at {today.strftime('%Y-%m-%d %H:%M')}")
    run_etl(list(FUND_UNIVERSE.keys()))
