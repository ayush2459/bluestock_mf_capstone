# Bluestock Mutual Fund Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Tag](https://img.shields.io/badge/release-v1.0-green)](https://github.com/ayush2459/bluestock_mf_capstone/releases/tag/v1.0)

An end-to-end data engineering and analytics platform that systematically evaluates the performance of **40 actively managed Indian equity mutual fund schemes** over a 3-year period (2021–2024). Built as a capstone internship project for **Bluestock Fintech**.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Dataset Descriptions](#dataset-descriptions)
4. [Setup & Installation](#setup--installation)
5. [How to Run the ETL Pipeline](#how-to-run-the-etl-pipeline)
6. [How to Open the Dashboard](#how-to-open-the-dashboard)
7. [Performance Metrics Computed](#performance-metrics-computed)
8. [Key Findings](#key-findings)
9. [Deliverables](#deliverables)
10. [Author](#author)

---

## Project Overview

This platform automates the entire workflow from raw NAV ingestion to interactive visualisation:

```
AMFI / MFAPI APIs  ──►  extract_nav.py  ──►  transform.py  ──►  metrics.py
                                                                      │
                                                                 load_db.py
                                                                      │
                                                              mutual_funds.db
                                                                      │
                                                           Streamlit Dashboard
```

**What it does:**
- Fetches daily NAV data for 40 equity schemes from AMFI India and MFAPI.in
- Cleans, forward-fills, and computes daily returns
- Calculates 8 institutional-grade performance metrics
- Benchmarks all funds against the Nifty 100 TRI
- Scores funds via a weighted composite scorecard
- Surfaces all insights on a dark-themed 5-page Streamlit dashboard

---

## Repository Structure

```
bluestock_mf_capstone/
├── src/
│   ├── extract_nav.py        # Data extraction (AMFI + MFAPI REST)
│   ├── transform.py          # Cleaning, return calculation, benchmark merge
│   ├── metrics.py            # 8 performance metric computations
│   ├── load_db.py            # SQLite upsert with WAL mode
│   ├── validate.py           # 12-check data quality suite
│   └── scorecard.py          # Weighted composite rank computation
├── dashboard/
│   ├── app.py                # Streamlit main entry point
│   └── pages/
│       ├── overview.py       # KPI cards + fund leaderboard
│       ├── comparison.py     # Multi-fund radar chart comparison
│       ├── metrics.py        # Full metrics table + scatter plots
│       ├── sector.py         # Sector allocation stacked charts
│       └── risk.py           # Drawdown, VaR, rolling Sharpe
├── data/
│   ├── raw/                  # Raw JSON/CSV from APIs
│   └── processed/            # Cleaned CSVs + parquet cache
├── notebooks/
│   └── eda_analysis.ipynb    # Exploratory Data Analysis notebook
├── docs/
│   ├── Final_Report.pdf      # 17-page capstone report
│   └── Bluestock_MF_Presentation.pptx  # 12-slide presentation
├── mutual_funds.db           # SQLite database (main data store)
├── run_pipeline.py           # Master orchestrator CLI
├── requirements.txt          # Pinned Python dependencies
└── README.md                 # This file
```

---

## Dataset Descriptions

### Funds Covered
- **40 equity mutual fund schemes** across 5 categories: Small Cap (8), Mid Cap (9), Flexi Cap (10), Large Cap (8), ELSS Tax Saver (5)
- All schemes are **Direct Plan – Growth** variants
- Date range: **01 January 2021 – 31 December 2024** (3 years, ~756 trading days)

### Data Sources

| Source | Data Type | Format | Volume |
|--------|-----------|--------|--------|
| [MFAPI.in](https://mfapi.in) | Historical NAV per scheme | JSON REST API | ~30K rows |
| [AMFI India](https://amfiindia.com) | Daily NAV bulk file | CSV/HTTP | ~800K rows |
| [NSE India](https://nseindia.com) | Nifty 100 TRI benchmark | CSV | ~756 rows |
| SEBI AMFI Disclosures | Portfolio holdings (quarterly) | PDF → CSV | 4 quarters |

### SQLite Database Schema (`mutual_funds.db`)

| Table | Rows | Description |
|-------|------|-------------|
| `funds` | 40 | Static scheme metadata (ISIN, AMC, category, inception date) |
| `nav_data` | ~30,240 | Daily NAV observations per scheme |
| `performance_metrics` | 40 | Computed metric values (8 metrics per fund) |
| `benchmark_returns` | 756 | Nifty 100 TRI daily values |
| `portfolio_holdings` | ~640 | Quarterly sector allocations |
| `validation_log` | — | Data quality check results |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- pip 23+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ayush2459/bluestock_mf_capstone.git
cd bluestock_mf_capstone
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# OR
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify installation

```bash
python -c "import pandas, streamlit, plotly; print('All dependencies OK')"
```

---

## How to Run the ETL Pipeline

The master orchestrator `run_pipeline.py` accepts a `--stage` flag to run individual stages or the full pipeline.

### Run full pipeline (recommended)

```bash
python run_pipeline.py --stage all
```

Expected output:
```
[EXTRACT]   Fetching NAV data for 40 schemes... done (38.2s)
[TRANSFORM] Cleaning and computing returns... done (4.1s)
[ENRICH]    Computing 8 metrics per fund... done (0.8s)
[LOAD]      Writing to mutual_funds.db... done (1.2s)
[VALIDATE]  Running 12 quality checks... 38/40 passed
Pipeline complete. Exit code: 0
```

### Run individual stages

```bash
python run_pipeline.py --stage extract     # Data fetch only
python run_pipeline.py --stage transform   # Clean + returns
python run_pipeline.py --stage metrics     # Compute metrics
python run_pipeline.py --stage load        # Write to DB
python run_pipeline.py --stage validate    # Quality checks
python run_pipeline.py --stage scorecard   # Compute composite ranks
```

### CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--stage` | `all` | Pipeline stage to run |
| `--funds` | `all` | Comma-separated scheme codes, or `all` |
| `--start-date` | `2021-01-01` | Data start date (YYYY-MM-DD) |
| `--end-date` | `2024-12-31` | Data end date (YYYY-MM-DD) |
| `--db-path` | `mutual_funds.db` | SQLite database path |
| `--log-level` | `INFO` | Logging verbosity (DEBUG/INFO/WARNING) |

### Example: re-run only for specific funds

```bash
python run_pipeline.py --stage all --funds 119551,118989,120503
```

---

## How to Open the Dashboard

### Start the Streamlit app

```bash
streamlit run dashboard/app.py
```

The dashboard opens automatically at `http://localhost:8501`.

### Dashboard Pages

| Page | Description |
|------|-------------|
| **Overview** | KPI cards (Avg CAGR, Sharpe, Max Drawdown), fund leaderboard, NAV trend chart |
| **Fund Comparison** | Multi-select funds; radar chart + side-by-side bar comparisons |
| **Performance Metrics** | Full 40-fund sortable table, scatter plot (CAGR vs Sharpe), correlation heatmap |
| **Sector Analysis** | Stacked bar chart of sector allocations with quarter selector |
| **Risk Analysis** | Drawdown waterfall, VaR histogram, rolling 90-day Sharpe, equity curves |

### Dashboard features
- **Dark theme** via custom CSS overlay (`dashboard/style.css`)
- **Real-time DB reads** — no CSV export required
- **Cached queries** — `@st.cache_data(ttl=3600)` for <200ms response time
- **Responsive filters** — category, date range, fund multi-select in sidebar

---

## Performance Metrics Computed

| Metric | Formula | Risk-free rate |
|--------|---------|---------------|
| **Sharpe Ratio** | (Rp – Rf) / σp | 6.5% (RBI repo avg) |
| **Sortino Ratio** | (Rp – Rf) / σd | 6.5% |
| **Jensen's Alpha** | Rp – [Rf + β(Rm – Rf)] | — |
| **Beta** | Cov(Rp, Rm) / Var(Rm) | — |
| **Treynor Ratio** | (Rp – Rf) / β | 6.5% |
| **Max Drawdown** | Min(Pt / Ppeak – 1) | — |
| **VaR (95%)** | 5th percentile of daily returns | — |
| **CAGR** | (VT / V0)^(1/T) – 1 | — |

All rolling metrics use a **252-day (1-year) window**. Benchmark: **Nifty 100 TRI**.

---

## Key Findings

1. **70% of funds (28/40) outperformed Nifty 100 TRI** (16.2% CAGR) on raw return basis
2. Only **30% outperformed on Sharpe ratio** — highlights alpha-erosion from volatility
3. **Best risk-adjusted fund:** Parag Parikh Flexi Cap (Sortino 1.68, Alpha +8.7%, MDD –19.2%)
4. **Highest CAGR:** Quant Small Cap (34.7%) — but also highest Max Drawdown (–34.1%)
5. **Financial Services + IT = 48%** of average allocation across all 40 funds
6. The **composite scorecard re-ranks** funds significantly vs pure CAGR — crucial for retail investors

---

## Deliverables

| # | Deliverable | Status |
|---|-------------|--------|
| D1 | `docs/Final_Report.pdf` (17 pages) | ✅ Complete |
| D2 | `docs/Bluestock_MF_Presentation.pptx` (12 slides) | ✅ Complete |
| D3 | Clean GitHub repo with README | ✅ Complete |
| D4 | Git tag `v1.0` on main | ✅ Complete |
| D5 | `mutual_funds.db` SQLite database | ✅ Complete |
| D6 | `notebooks/eda_analysis.ipynb` | ✅ Complete |
| D7 | `dashboard/app.py` Streamlit app | ✅ Complete |

---

## Author

**Ayush**
B.Tech CSE (2023–27) · Maharaja Agrasen Institute of Technology, Delhi · GGSIPU
- GitHub: [github.com/ayush2459](https://github.com/ayush2459)
- Capstone Repo: [bluestock_mf_capstone](https://github.com/ayush2459/bluestock_mf_capstone)
- Internship: Bluestock Fintech · June 2025

---

*Built with Python 3.11 · Pandas · NumPy · SQLite · Streamlit · Plotly · Matplotlib*
