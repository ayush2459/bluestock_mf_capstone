📊 Bluestock MF Analytics Platform

### Mutual Fund Intelligence & Portfolio Analytics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite)
![Plotly](https://img.shields.io/badge/Visualization-Plotly-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A comprehensive Mutual Fund Analytics Platform built as part of the Bluestock Fintech Capstone Program, helping investors make smarter, data-driven investment decisions through advanced analytics, portfolio insights, risk assessment, and interactive dashboards.**

---

## 🌟 Overview

The **Bluestock MF Analytics Platform** is an end-to-end fintech analytics solution designed to provide meaningful insights into mutual fund performance and portfolio management. The platform combines data engineering, financial analytics, business intelligence, and visualisation techniques to transform raw financial datasets into actionable investment insights.

This project demonstrates practical applications of:

- Data Analytics
- Financial Analysis
- Business Intelligence
- Data Engineering
- Dashboard Development
- FinTech Solutions

---

## 🚀 Key Features

### 📈 Mutual Fund Performance Analysis

- Historical NAV trend visualization
- Fund performance comparison
- CAGR calculation
- Benchmark comparison
- Multi-period return analysis

### 💼 Portfolio Analytics

- Portfolio diversification analysis
- Asset allocation insights
- Sector-wise exposure tracking
- Portfolio risk assessment
- Investment distribution visualization

### ⚠️ Risk Assessment Metrics

- Sharpe Ratio
- Sortino Ratio
- Alpha
- Beta
- Maximum Drawdown
- Value at Risk (VaR)
- Conditional Value at Risk (CVaR)

### 🎯 Recommendation Engine

- Risk-profile based recommendations
- Goal-oriented fund suggestions
- Investment horizon analysis
- Personalized fund discovery

### 📊 Interactive Dashboard

- Dynamic charts
- KPI dashboards
- Advanced filters
- Interactive visualizations
- User-friendly interface

### 📄 Automated Reporting

- PDF report generation
- Portfolio summaries
- Fund performance reports
- Downloadable analytics reports

---

## 🏗️ System Architecture

```text
Raw Data Sources
       │
       ▼
Data Ingestion Layer
       │
       ▼
Data Cleaning & Transformation
       │
       ▼
SQLite Database
       │
       ▼
Analytics Engine
       │
       ├── Performance Metrics
       ├── Risk Metrics
       ├── Portfolio Analytics
       └── Recommendation Engine
       │
       ▼
Streamlit Dashboard
       │
       ▼
Reports & Insights
```

---

## 📂 Project Structure

```text
bluestock_mf_capstone/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
│
├── scripts/
│   ├── generate_datasets.py
│   ├── load_from_local.py
│   ├── compute_metrics.py
│   ├── recommender.py
│   ├── generate_report.py
│   ├── streamlit_app.py
│   └── etl_pipeline.py
│
├── reports/
│   ├── Final_Report.pdf
│   ├── Presentation.pptx
│   └── Weekly_Report.html
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── requirements.txt
└── README.md
```

---

## 📊 Dataset Overview

The platform processes multiple datasets covering different aspects of mutual fund analytics.

| Dataset | Description |
|----------|------------|
| Fund Master | Fund metadata and classifications |
| NAV History | Daily Net Asset Value records |
| AUM Data | Assets Under Management |
| SIP Inflows | Monthly SIP contributions |
| Category Inflows | Fund category performance |
| Investor Transactions | Investor activity data |
| Portfolio Holdings | Sector allocation details |
| Benchmark Indices | Market benchmark performance |

### Data Statistics

- 100,000+ Records Processed
- Multiple Financial Datasets
- Portfolio Holdings Data
- Historical Market Data
- Mutual Fund Performance Records

---

## 📉 Financial Metrics Implemented

| Metric | Description |
|----------|-------------|
| CAGR | Annualized growth rate |
| Sharpe Ratio | Risk-adjusted return measurement |
| Sortino Ratio | Downside-risk adjusted returns |
| Alpha | Excess return over benchmark |
| Beta | Market sensitivity indicator |
| Maximum Drawdown | Largest portfolio decline |
| VaR | Expected loss estimation |
| CVaR | Tail-risk measurement |

---

## 🛠️ Technology Stack

### Programming

- Python 3.11

### Data Analytics

- Pandas
- NumPy
- SciPy

### Data Visualization

- Plotly
- Matplotlib

### Dashboard Development

- Streamlit

### Database

- SQLite

### Reporting

- ReportLab
- python-pptx

### Development Tools

- Jupyter Notebook
- Git
- GitHub

---

## ⚡ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/ayush2459/bluestock_mf_capstone.git

cd bluestock_mf_capstone
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Datasets

```bash
python scripts/generate_datasets.py
```

### 4. Load Database

```bash
python scripts/load_from_local.py
```

### 5. Compute Analytics Metrics

```bash
python scripts/compute_metrics.py
```

### 6. Launch Dashboard

```bash
streamlit run scripts/streamlit_app.py
```

Open the application:

```text
http://localhost:8501
```

---

## 📸 Dashboard Modules

### 🏠 Overview Dashboard

- Key Performance Indicators
- Industry Insights
- Market Overview
- Fund Summary

### 📊 NAV Explorer

- Historical NAV Trends
- Fund Comparisons
- Performance Visualization

### 📈 Performance Analytics

- Return Analysis
- Risk-Adjusted Performance
- Fund Rankings

### 🧪 Risk & Simulation

- Monte Carlo Simulations
- VaR Analysis
- CVaR Analysis

### 💡 Recommendation Engine

- Personalized Fund Suggestions
- Goal-Based Recommendations
- Risk-Based Filtering

### 📄 Report Generator

- PDF Reports
- Performance Summaries
- Portfolio Analytics Reports

---

## 📈 Project Outcomes

- Developed an end-to-end financial analytics platform
- Built interactive business intelligence dashboards
- Implemented advanced financial risk metrics
- Designed a recommendation engine for investors
- Automated reporting workflows
- Demonstrated practical fintech analytics applications
- Improved investment decision support through data-driven insights

---

## 🎯 Future Enhancements

- Live Mutual Fund API Integration
- Real-Time NAV Tracking
- Machine Learning Recommendation Models
- Portfolio Optimization Algorithms
- User Authentication System
- Mobile Responsive Dashboard
- Cloud Deployment
- Advanced Portfolio Simulation

---

## 👨‍💻 Author

### Ayush Gupta

**Data Analyst | Aspiring Data Scientist | FinTech Enthusiast**

GitHub: https://github.com/ayush2459

LinkedIn: https://linkedin.com/in/ayush2459

---

## 🏆 Skills Demonstrated

- Data Analytics
- Financial Analytics
- Business Intelligence
- Dashboard Development
- Data Visualization
- Database Management
- Python Programming
- Statistical Analysis
- FinTech Solutions
- Report Automation

---

## 📜 License

This project was developed for educational and portfolio purposes as part of the Bluestock Fintech Capstone Program.

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.

**Built with Python, Data Analytics, Financial Intelligence, and FinTech Innovation 🚀**
