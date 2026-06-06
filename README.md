# 📈 Bluestock Fintech — Mutual Fund Analytics Platform

> End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard  
> Individual Capstone Project | June 2026 | Bluestock Fintech Pvt. Ltd.

---

## 🚀 Quick Start

```bash
# 1. Clone repo
git clone https://github.com/[your-username]/bluestock_mf_capstone.git
cd bluestock_mf_capstone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate datasets + load DB
python scripts/generate_datasets.py
python scripts/load_from_local.py

# 4. Run Streamlit dashboard
streamlit run scripts/streamlit_app.py

# 5. Generate reports
python scripts/generate_report.py

# 6. Email report
python scripts/email_report.py
```

---

## 📁 Folder Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/           ← 10 original CSV datasets
│   ├── processed/     ← cleaned CSVs + chart PNGs
│   └── db/            ← bluestock_mf.db (SQLite, gitignored)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py        ← D1: Master ETL
│   ├── live_nav_fetch.py      ← B1: Cron NAV fetcher
│   ├── load_from_local.py     ← DB loader (offline)
│   ├── compute_metrics.py     ← D4: Risk metrics engine
│   ├── recommender.py         ← D6: Fund recommender
│   ├── streamlit_app.py       ← B2: Web dashboard
│   ├── email_report.py        ← B5: HTML email
│   ├── generate_datasets.py   ← Data generator
│   └── generate_report.py     ← D7: PDF + PPTX
├── sql/
│   ├── schema.sql             ← D2: CREATE TABLE statements
│   └── queries.sql            ← D2: 10 analytical queries
├── reports/
│   ├── Final_Report.pdf       ← D7
│   ├── Presentation.pptx      ← D7
│   └── weekly_report.html     ← B5
└── README.md
```

---

## 📊 Deliverables

| ID | Deliverable | Status |
|----|-------------|--------|
| D1 | ETL Pipeline (`etl_pipeline.py`) | ✅ |
| D2 | SQLite Database + SQL queries | ✅ |
| D3 | EDA Notebook (15+ charts) | ✅ |
| D4 | Performance Metrics (7 CSVs) | ✅ |
| D5 | Streamlit Dashboard (4 pages) | ✅ |
| D6 | Advanced Analytics (VaR, Monte Carlo) | ✅ |
| D7 | Final Report PDF + PPTX | ✅ |
| B1 | Cron job NAV fetcher | ✅ |
| B2 | Streamlit web app | ✅ |
| B3 | Monte Carlo simulation | ✅ |
| B4 | Markowitz Efficient Frontier | ✅ |
| B5 | HTML email report generator | ✅ |

---

## ⚙️ Cron Job Setup (B1)

```bash
# Add to crontab (runs at 8 PM every weekday)
crontab -e
# Add this line:
0 20 * * 1-5 /usr/bin/python3 /path/to/scripts/live_nav_fetch.py
```

---

## 🗄️ Database Schema

8 tables in star schema:
- `dim_fund` — 40 AMFI schemes
- `dim_date` — 1,612 dates
- `fact_nav` — 42,550 daily NAV rows
- `fact_transactions` — 63,451 investor transactions
- `fact_performance` — risk metrics per scheme
- `fact_aum` — quarterly AUM by fund house
- `fact_sip_industry` — monthly SIP data
- `fact_benchmark` — 6 index time series

---

## ⚠️ Disclaimer

All data sourced from publicly available AMFI India, mfapi.in, NSE/BSE.  
This project is for **educational purposes only** and does not constitute financial advice.

© 2026 Bluestock Fintech Pvt. Ltd.
