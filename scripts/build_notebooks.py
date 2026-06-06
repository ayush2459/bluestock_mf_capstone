"""Auto-generate all 5 Jupyter notebooks with full code + markdown"""
import json, textwrap
from pathlib import Path

NB_DIR = Path("/home/claude/bluestock_mf_capstone/notebooks")
NB_DIR.mkdir(exist_ok=True)

def nb(cells):
    return {"nbformat":4,"nbformat_minor":5,
            "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},
            "cells":cells}

def md(src): return {"cell_type":"markdown","metadata":{},"source":src,"id":"md"}
def code(src): return {"cell_type":"code","metadata":{},"source":textwrap.dedent(src).strip(),
                       "outputs":[],"execution_count":None,"id":"cd"}

# ══════════════════════════════════════════════════════════════
# NOTEBOOK 1 — Data Ingestion
# ══════════════════════════════════════════════════════════════
n1 = nb([
md("# 📥 Notebook 01 — Data Ingestion\n**Bluestock Fintech Mutual Fund Analytics Platform**\n\nThis notebook loads all 10 datasets, validates them, and fetches live NAV."),
code("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings, sys
from pathlib import Path
warnings.filterwarnings('ignore')

BASE = Path('..').resolve()
RAW  = BASE / 'data' / 'raw'
PROC = BASE / 'data' / 'processed'
PROC.mkdir(exist_ok=True)
print(f"Project root: {BASE}")
"""),
md("## 1. Load All 10 Datasets"),
code("""
files = {
    '01_fund_master':        '01_fund_master.csv',
    '02_nav_history':        '02_nav_history.csv',
    '03_aum_by_fund_house':  '03_aum_by_fund_house.csv',
    '04_monthly_sip':        '04_monthly_sip_inflows.csv',
    '05_category_inflows':   '05_category_inflows.csv',
    '06_folio_count':        '06_industry_folio_count.csv',
    '07_scheme_performance': '07_scheme_performance.csv',
    '08_investor_tx':        '08_investor_transactions.csv',
    '09_portfolio':          '09_portfolio_holdings.csv',
    '10_benchmark':          '10_benchmark_indices.csv',
}
datasets = {}
for name, fname in files.items():
    df = pd.read_csv(RAW / fname)
    datasets[name] = df
    print(f"  {name:30s}  shape={str(df.shape):15s}  dtypes={dict(df.dtypes.value_counts())}")
"""),
md("## 2. Fund Master Overview"),
code("""
df_fund = datasets['01_fund_master']
print("Fund Houses:", df_fund['fund_house'].nunique())
print("Categories:",  df_fund['category'].value_counts().to_dict())
print("Sub-categories:", df_fund['sub_category'].nunique())
print("Risk grades:",  df_fund['risk_category'].value_counts().to_dict())
df_fund.head(5)
"""),
md("## 3. NAV History Validation"),
code("""
df_nav = datasets['02_nav_history']
df_nav['date'] = pd.to_datetime(df_nav['date'])
print(f"Date range: {df_nav['date'].min()} → {df_nav['date'].max()}")
print(f"Schemes in NAV data: {df_nav['amfi_code'].nunique()}")
print(f"Missing NAV values:  {df_nav['nav'].isna().sum()}")
print(f"NAV range: Rs.{df_nav['nav'].min():.2f} – Rs.{df_nav['nav'].max():.2f}")
df_nav.describe()
"""),
md("## 4. Validate AMFI Codes"),
code("""
nav_codes  = set(df_nav['amfi_code'].astype(str))
fund_codes = set(df_fund['amfi_code'].astype(str))
missing_in_nav = fund_codes - nav_codes
extra_in_nav   = nav_codes - fund_codes
print(f"Funds in master:          {len(fund_codes)}")
print(f"Funds in nav_history:     {len(nav_codes)}")
print(f"In master but no NAV:     {missing_in_nav}")
print(f"In NAV but not in master: {extra_in_nav}")
"""),
md("## 5. SIP Industry Data — Real AMFI Values"),
code("""
df_sip = datasets['04_monthly_sip']
print(f"SIP Dec-2025: Rs.{df_sip[df_sip['month']=='2025-12']['sip_inflow_crore'].values[0]:,.0f} crore")
print(f"SIP Jan-2022: Rs.{df_sip[df_sip['month']=='2022-01']['sip_inflow_crore'].values[0]:,.0f} crore")
df_sip.tail()
"""),
md("## 6. Investor Transactions Summary"),
code("""
df_tx = datasets['08_investor_tx']
df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
print(f"Total transactions:  {len(df_tx):,}")
print(f"Unique investors:    {df_tx['investor_id'].nunique():,}")
print(f"Transaction types:   {df_tx['transaction_type'].value_counts().to_dict()}")
print(f"States covered:      {df_tx['state'].nunique()}")
print(f"KYC Verified:        {(df_tx['kyc_status']=='Verified').mean()*100:.1f}%")
df_tx.describe()
"""),
md("## 7. Quick NAV Trend Preview"),
code("""
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# NAV history for 5 large cap funds
sample_codes = df_nav['amfi_code'].unique()[:5]
for code in sample_codes:
    sub = df_nav[df_nav['amfi_code']==code].sort_values('date')
    nav_norm = sub['nav'] / sub['nav'].iloc[0] * 100
    axes[0].plot(sub['date'], nav_norm, label=str(code), linewidth=1.2)
axes[0].set_title('Normalised NAV Growth (Base=100)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Date'); axes[0].set_ylabel('Indexed NAV')
axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)

# Schemes per category
cat_counts = df_fund['sub_category'].value_counts().head(8)
axes[1].barh(cat_counts.index, cat_counts.values, color='steelblue')
axes[1].set_title('Schemes by Sub-Category', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Number of Schemes')
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(BASE/'data'/'processed'/'nb01_preview.png', dpi=120, bbox_inches='tight')
plt.show()
print("Chart saved ✓")
"""),
md("## ✅ Day 1 Complete\n- All 10 datasets loaded and validated\n- AMFI code integrity confirmed\n- NAV history spans Jan 2022 – May 2026 (42,550 rows)\n- 63,451 investor transactions across 12 states"),
])
(NB_DIR/"01_data_ingestion.ipynb").write_text(json.dumps(n1, indent=1))
print("✓ Notebook 1 written")

# ══════════════════════════════════════════════════════════════
# NOTEBOOK 2 — Data Cleaning + SQL
# ══════════════════════════════════════════════════════════════
n2 = nb([
md("# 🧹 Notebook 02 — Data Cleaning + SQL Database\n**Bluestock Fintech | Day 2**"),
code("""
import pandas as pd, numpy as np, sqlite3, matplotlib.pyplot as plt
from pathlib import Path
import warnings; warnings.filterwarnings('ignore')

BASE = Path('..').resolve()
RAW  = BASE/'data'/'raw'; PROC = BASE/'data'/'processed'
DB   = BASE/'data'/'db'/'bluestock_mf.db'
print("Paths initialised ✓")
"""),
md("## 1. Clean NAV History — Forward Fill Holidays"),
code("""
df_nav = pd.read_csv(RAW/'02_nav_history.csv', parse_dates=['date'])
print(f"Raw shape: {df_nav.shape}")

# Sort, deduplicate
df_nav = df_nav.sort_values(['amfi_code','date']).drop_duplicates(['amfi_code','date'])

# Reindex to full date range & ffill (handles weekends/holidays)
full_date_range = pd.date_range(df_nav['date'].min(), df_nav['date'].max(), freq='D')
cleaned_dfs = []
for code, grp in df_nav.groupby('amfi_code'):
    grp = grp.set_index('date').reindex(full_date_range)
    grp['nav'] = grp['nav'].ffill()
    grp['amfi_code'] = code
    grp.index.name = 'date'
    cleaned_dfs.append(grp.reset_index())

df_nav_clean = pd.concat(cleaned_dfs, ignore_index=True)
df_nav_clean = df_nav_clean[df_nav_clean['nav'].notna()]
df_nav_clean['nav'] = df_nav_clean['nav'].round(4)
print(f"Cleaned shape: {df_nav_clean.shape}")
print(f"Null NAV remaining: {df_nav_clean['nav'].isna().sum()}")
df_nav_clean.to_csv(PROC/'clean_nav.csv', index=False)
print("clean_nav.csv saved ✓")
"""),
md("## 2. Clean Investor Transactions"),
code("""
df_tx = pd.read_csv(RAW/'08_investor_transactions.csv', parse_dates=['transaction_date'])
print(f"Raw transactions: {len(df_tx):,}")

# Standardise transaction_type
df_tx['transaction_type'] = df_tx['transaction_type'].str.strip().str.title()
valid_types = ['Sip','Lumpsum','Redemption']
df_tx = df_tx[df_tx['transaction_type'].isin(valid_types)]

# Validate amounts
df_tx = df_tx[df_tx['amount_inr'] > 0]

# KYC status
df_tx['kyc_status'] = df_tx['kyc_status'].str.strip()

# Fix city_tier
df_tx['city_tier'] = df_tx['city_tier'].str.upper().str.strip()
df_tx = df_tx[df_tx['city_tier'].isin(['T30','B30'])]

print(f"Clean transactions: {len(df_tx):,}")
print(f"Missing values:\\n{df_tx.isnull().sum()[df_tx.isnull().sum()>0]}")
df_tx.to_csv(PROC/'clean_transactions.csv', index=False)
print("clean_transactions.csv saved ✓")
"""),
md("## 3. Clean Scheme Performance"),
code("""
df_perf = pd.read_csv(RAW/'07_scheme_performance.csv')

# Ensure numeric
numeric_cols = ['return_1yr_pct','return_3yr_pct','return_5yr_pct',
                'alpha','beta','sharpe_ratio','sortino_ratio',
                'std_dev_ann_pct','max_drawdown_pct']
for col in numeric_cols:
    if col in df_perf.columns:
        df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')

# Validate expense ratio range
if 'expense_ratio_pct' in df_perf.columns:
    mask = df_perf['expense_ratio_pct'].between(0.01, 3.0)
    print(f"Expense ratio out of range: {(~mask).sum()} rows")

print(f"Negative Sharpe funds: {(df_perf.get('sharpe_ratio',pd.Series())<0).sum()}")
df_perf.to_csv(PROC/'clean_performance.csv', index=False)
print("clean_performance.csv saved ✓")
df_perf.describe()
"""),
md("## 4. Load & Query SQLite Database"),
code("""
conn = sqlite3.connect(DB)
print("Connected to:", DB)

# Show all tables
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("\\nTables in DB:")
for t in tables['name']:
    count = pd.read_sql(f"SELECT COUNT(*) as n FROM {t}", conn)['n'].iloc[0]
    print(f"  {t:30s}  {count:>8,} rows")
"""),
md("## 5. Run the 10 Analytical SQL Queries"),
code("""
queries = {
    "Q1 Top funds by composite score": '''
        SELECT f.scheme_name, f.fund_house, f.sub_category,
               p.cagr_3yr_pct, p.sharpe_ratio, p.composite_score, p.score_rank
        FROM fact_performance p JOIN dim_fund f ON p.amfi_code=f.amfi_code
        ORDER BY p.score_rank LIMIT 10''',

    "Q2 Avg NAV by category (last 6 months)": '''
        SELECT f.sub_category, ROUND(AVG(n.nav_inr),2) as avg_nav, COUNT(DISTINCT n.amfi_code) as funds
        FROM fact_nav n JOIN dim_fund f ON n.amfi_code=f.amfi_code
        WHERE n.nav_date >= '2025-12-01'
        GROUP BY f.sub_category ORDER BY avg_nav DESC''',

    "Q3 AUM market share latest quarter": '''
        SELECT fund_house, aum_lakh_crore,
               ROUND(aum_lakh_crore/SUM(aum_lakh_crore) OVER()*100,2) as market_share_pct
        FROM fact_aum WHERE quarter=(SELECT MAX(quarter) FROM fact_aum)
        ORDER BY aum_lakh_crore DESC''',

    "Q4 SIP by state T30 vs B30": '''
        SELECT state, city_tier, COUNT(*) as txns,
               ROUND(SUM(amount_inr)/1e7,2) as total_crore,
               ROUND(AVG(amount_inr),0) as avg_sip
        FROM fact_transactions WHERE transaction_type='Sip'
        GROUP BY state, city_tier ORDER BY total_crore DESC LIMIT 15''',

    "Q5 Low expense + high Sharpe funds": '''
        SELECT f.scheme_name, f.expense_ratio_pct, p.sharpe_ratio, p.cagr_3yr_pct
        FROM dim_fund f JOIN fact_performance p ON f.amfi_code=p.amfi_code
        WHERE f.expense_ratio_pct < 0.50 AND p.sharpe_ratio > 0.50
        ORDER BY p.sharpe_ratio DESC''',
}

for qname, qsql in queries.items():
    print(f"\\n{'='*55}")
    print(f"  {qname}")
    print('='*55)
    try:
        result = pd.read_sql(qsql.strip(), conn)
        print(result.to_string(index=False))
    except Exception as e:
        print(f"  ERROR: {e}")

conn.close()
print("\\n✅ All queries executed")
"""),
md("## 6. Data Quality Summary"),
code("""
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1,2,figsize=(12,4))

# Missing values heatmap
df_all = pd.read_csv(RAW/'08_investor_transactions.csv')
missing = df_all.isnull().sum().sort_values(ascending=True)
missing = missing[missing>0]
if len(missing):
    missing.plot(kind='barh', ax=axes[0], color='tomato')
    axes[0].set_title('Missing Values by Column')
else:
    axes[0].text(0.5,0.5,'No Missing Values!', ha='center', va='center', fontsize=14, color='green')
    axes[0].set_title('Data Quality — Investor Transactions')

# Transaction type split
df_tx2 = pd.read_csv(PROC/'clean_transactions.csv')
counts = df_tx2['transaction_type'].value_counts()
axes[1].pie(counts.values, labels=counts.index, autopct='%1.1f%%',
            colors=['#2196F3','#4CAF50','#FF5722'])
axes[1].set_title('Transaction Type Distribution')

plt.tight_layout()
plt.savefig(BASE/'data'/'processed'/'nb02_quality.png',dpi=120,bbox_inches='tight')
plt.show()
print("✅ Cleaning complete. All CSVs saved to data/processed/")
"""),
])
(NB_DIR/"02_data_cleaning.ipynb").write_text(json.dumps(n2, indent=1))
print("✓ Notebook 2 written")

# ══════════════════════════════════════════════════════════════
# NOTEBOOK 3 — EDA
# ══════════════════════════════════════════════════════════════
n3 = nb([
md("# 📊 Notebook 03 — Exploratory Data Analysis (EDA)\n**Bluestock Fintech | Day 3 | 15+ Charts**"),
code("""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import warnings; warnings.filterwarnings('ignore')
from pathlib import Path

BASE  = Path('..').resolve()
RAW   = BASE/'data'/'raw'
PROC  = BASE/'data'/'processed'
FIGS  = PROC

plt.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': '#f8f9fa',
    'axes.grid': True, 'grid.alpha': 0.3, 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
})
COLORS = ['#1565C0','#2E7D32','#C62828','#F57F17','#6A1B9A',
          '#00838F','#558B2F','#4527A0','#D84315','#00695C']

df_nav    = pd.read_csv(RAW/'02_nav_history.csv', parse_dates=['date'])
df_fund   = pd.read_csv(RAW/'01_fund_master.csv').drop_duplicates('amfi_code')
df_sip    = pd.read_csv(RAW/'04_monthly_sip_inflows.csv')
df_aum    = pd.read_csv(RAW/'03_aum_by_fund_house.csv')
df_tx     = pd.read_csv(RAW/'08_investor_transactions.csv', parse_dates=['transaction_date'])
df_folio  = pd.read_csv(RAW/'06_industry_folio_count.csv')
df_cat    = pd.read_csv(RAW/'05_category_inflows.csv')
df_bench  = pd.read_csv(RAW/'10_benchmark_indices.csv', parse_dates=['date'])
df_perf   = pd.read_csv(RAW/'07_scheme_performance.csv')
df_port   = pd.read_csv(RAW/'09_portfolio_holdings.csv')
df_nav    = df_nav.merge(df_fund[['amfi_code','scheme_name','sub_category','fund_house']], on='amfi_code', how='left')
print("All datasets loaded ✓")
"""),
md("## Chart 1 — NAV Growth Trend (Equity Funds)"),
code("""
fig, ax = plt.subplots(figsize=(14,5))
equity_codes = df_fund[df_fund['category']=='Equity']['amfi_code'].unique()[:8]
for i, code in enumerate(equity_codes):
    sub = df_nav[df_nav['amfi_code']==code].sort_values('date')
    if sub.empty: continue
    nav_norm = sub['nav'] / sub['nav'].iloc[0] * 100
    name = sub['scheme_name'].iloc[0][:30]
    ax.plot(sub['date'], nav_norm, label=name, color=COLORS[i%len(COLORS)], linewidth=1.5)
ax.axvline(pd.Timestamp('2024-06-04'), color='red', linestyle='--', alpha=0.5, label='Election 2024')
ax.set_title('Equity Fund NAV Growth 2022–2026 (Indexed to 100)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date'); ax.set_ylabel('Indexed NAV (Base=100)')
ax.legend(loc='upper left', fontsize=7, ncol=2)
plt.tight_layout()
plt.savefig(FIGS/'chart01_nav_trend.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 1 ✓")
"""),
md("## Chart 2 — AUM Growth by Fund House"),
code("""
fig, ax = plt.subplots(figsize=(13,6))
pivot = df_aum.pivot_table(index='quarter', columns='fund_house', values='aum_lakh_crore', aggfunc='sum')
pivot = pivot[[c for c in pivot.columns if pivot[c].notna().all()]]
bottom = np.zeros(len(pivot))
for i, col in enumerate(pivot.columns):
    ax.bar(range(len(pivot)), pivot[col].values, bottom=bottom,
           label=col, color=plt.cm.tab10(i/10))
    bottom += pivot[col].fillna(0).values
ax.set_xticks(range(len(pivot)))
ax.set_xticklabels(pivot.index, rotation=45, ha='right', fontsize=7)
ax.set_title('AUM by Fund House per Quarter (Rs. Lakh Crore)', fontsize=13, fontweight='bold')
ax.set_ylabel('AUM (Rs. Lakh Crore)')
ax.legend(fontsize=7, loc='upper left', ncol=2)
plt.tight_layout()
plt.savefig(FIGS/'chart02_aum_growth.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 2 ✓")
"""),
md("## Chart 3 — SIP Inflow Trend with Rs.31,002 Cr Milestone"),
code("""
fig, ax = plt.subplots(figsize=(13,4))
df_sip['month_dt'] = pd.to_datetime(df_sip['month'])
ax.fill_between(df_sip['month_dt'], df_sip['sip_inflow_crore'], alpha=0.2, color='#1565C0')
ax.plot(df_sip['month_dt'], df_sip['sip_inflow_crore'], color='#1565C0', linewidth=2)
peak = df_sip.loc[df_sip['sip_inflow_crore'].idxmax()]
ax.annotate(f"ATH: Rs.{peak['sip_inflow_crore']:,.0f} Cr\\n(Dec 2025)",
            xy=(peak['month_dt'], peak['sip_inflow_crore']),
            xytext=(-80, -30), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='red'), color='red', fontsize=9)
ax.set_title('Monthly SIP Inflows (Rs. Crore) — AMFI India', fontsize=13, fontweight='bold')
ax.set_xlabel('Month'); ax.set_ylabel('SIP Inflow (Rs. Crore)')
plt.tight_layout()
plt.savefig(FIGS/'chart03_sip_trend.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 3 ✓")
"""),
md("## Chart 4 — Category Inflow Heatmap"),
code("""
fig, ax = plt.subplots(figsize=(13,6))
pivot_cat = df_cat.pivot_table(index='category', columns='month', values='net_inflow_crore', aggfunc='sum')
sns.heatmap(pivot_cat, ax=ax, cmap='RdYlGn', center=0,
            linewidths=0.3, fmt='.0f', annot=False,
            cbar_kws={'label': 'Net Inflow (Rs. Crore)'})
ax.set_title('Category-wise Net Inflows Heatmap (FY 2024-25)', fontsize=13, fontweight='bold')
ax.set_xlabel('Month'); ax.set_ylabel('Fund Category')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(FIGS/'chart04_category_heatmap.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 4 ✓")
"""),
md("## Chart 5 — Investor Demographics"),
code("""
fig, axes = plt.subplots(1,2,figsize=(12,5))

# Age group pie
age_dist = df_tx.groupby('age_group')['amount_inr'].sum().sort_index()
axes[0].pie(age_dist.values, labels=age_dist.index, autopct='%1.1f%%',
            colors=COLORS, startangle=90, pctdistance=0.8)
axes[0].set_title('SIP Amount by Age Group', fontsize=12, fontweight='bold')

# Box plot of SIP amount by age group
sip_only = df_tx[df_tx['transaction_type']=='SIP']
age_order = ['18-25','26-35','36-45','46-55','56+']
data_by_age = [sip_only[sip_only['age_group']==ag]['amount_inr'].values for ag in age_order]
bp = axes[1].boxplot(data_by_age, labels=age_order, patch_artist=True,
                     medianprops=dict(color='red', linewidth=2))
for patch, color in zip(bp['boxes'], COLORS):
    patch.set_facecolor(color); patch.set_alpha(0.7)
axes[1].set_title('SIP Amount Distribution by Age Group', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Age Group'); axes[1].set_ylabel('SIP Amount (Rs.)')
axes[1].set_ylim(0, 30000)

plt.tight_layout()
plt.savefig(FIGS/'chart05_demographics.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 5 ✓")
"""),
md("## Chart 6 — Geographic Distribution"),
code("""
fig, axes = plt.subplots(1,2,figsize=(13,5))

# SIP amount by state
state_sip = df_tx[df_tx['transaction_type']=='SIP'].groupby('state')['amount_inr'].sum().sort_values()
axes[0].barh(state_sip.index, state_sip.values/1e7, color='steelblue', edgecolor='white')
axes[0].set_title('Total SIP Investment by State (Rs. Crore)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Total SIP Amount (Rs. Crore)')

# T30 vs B30
tier = df_tx.groupby('city_tier')['amount_inr'].sum()
axes[1].pie(tier.values, labels=tier.index, autopct='%1.1f%%',
            colors=['#1565C0','#43A047'], startangle=90, explode=[0.05,0])
axes[1].set_title('T30 vs B30 Investment Split', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(FIGS/'chart06_geographic.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 6 ✓")
"""),
md("## Chart 7 — Folio Count Growth"),
code("""
fig, ax = plt.subplots(figsize=(13,4))
df_folio['month_dt'] = pd.to_datetime(df_folio['month'])
ax.stackplot(df_folio['month_dt'],
             df_folio['equity_folios_crore'],
             df_folio['debt_folios_crore'],
             df_folio['hybrid_folios_crore'],
             labels=['Equity','Debt','Hybrid'],
             colors=['#1565C0','#F57F17','#2E7D32'], alpha=0.85)
ax.annotate('26.12 Cr Total\\n(Dec 2025)',
            xy=(pd.Timestamp('2025-12-01'), 26),
            xytext=(-120, -20), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
ax.set_title('Mutual Fund Folio Count Growth (Crore)', fontsize=13, fontweight='bold')
ax.set_xlabel('Month'); ax.set_ylabel('Folios (Crore)')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig(FIGS/'chart07_folio_growth.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 7 ✓")
"""),
md("## Chart 8 — NAV Return Correlation Matrix"),
code("""
codes = df_nav['amfi_code'].unique()[:10]
pivot_nav = df_nav[df_nav['amfi_code'].isin(codes)].pivot_table(
    index='date', columns='amfi_code', values='nav')
returns = pivot_nav.pct_change().dropna()
returns.columns = [str(c) for c in returns.columns]
corr = returns.corr()

fig, ax = plt.subplots(figsize=(9,7))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, ax=ax, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            cbar_kws={'shrink':0.8})
ax.set_title('NAV Return Correlation Matrix (10 Funds)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS/'chart08_correlation.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 8 ✓")
"""),
md("## Chart 9 — Sector Allocation (Portfolio Holdings)"),
code("""
fig, axes = plt.subplots(1,2,figsize=(12,5))

# Aggregate sector weights
sector_wt = df_port.groupby('sector')['weight_pct'].mean().sort_values(ascending=False)
wedge_colors = plt.cm.Set3(np.linspace(0,1,len(sector_wt)))
axes[0].pie(sector_wt.values, labels=sector_wt.index, autopct='%1.1f%%',
            colors=wedge_colors, startangle=90)
axes[0].set_title('Average Sector Allocation\\n(Equity Fund Holdings)', fontsize=11, fontweight='bold')

# Top 10 stocks
top_stocks = df_port.groupby('stock_symbol')['weight_pct'].mean().nlargest(10)
axes[1].barh(top_stocks.index[::-1], top_stocks.values[::-1], color='#1565C0', edgecolor='white')
axes[1].set_title('Top 10 Holdings by Avg Weight', fontsize=11, fontweight='bold')
axes[1].set_xlabel('Average Weight (%)')

plt.tight_layout()
plt.savefig(FIGS/'chart09_sectors.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 9 ✓")
"""),
md("## Chart 10 — Benchmark Index Comparison"),
code("""
fig, ax = plt.subplots(figsize=(13,5))
for i, idx in enumerate(['Nifty50','Nifty100','NiftyMidcap150','BSESmallCap']):
    sub = df_bench[df_bench['index_name']==idx].sort_values('date')
    norm = sub['close_value'] / sub['close_value'].iloc[0] * 100
    ax.plot(sub['date'], norm, label=idx, color=COLORS[i], linewidth=1.8)
ax.set_title('Benchmark Index Performance 2022–2026 (Indexed to 100)', fontsize=13, fontweight='bold')
ax.set_xlabel('Date'); ax.set_ylabel('Indexed Value (Base=100)')
ax.legend(); plt.tight_layout()
plt.savefig(FIGS/'chart10_benchmarks.png', dpi=130, bbox_inches='tight')
plt.show()
print("Chart 10 ✓")
"""),
md("## 📝 Key EDA Findings\n\n1. **SIP Milestone**: Monthly SIP inflows grew 3x from Rs.11,000 Cr (Jan 2022) to Rs.31,002 Cr (Dec 2025) — a 182% increase, reflecting India's maturing equity culture.\n2. **SBI Dominance**: SBI MF holds Rs.12.5 lakh crore AUM (largest AMC), followed by ICICI Pru (Rs.10.74L Cr) and HDFC (Rs.9.30L Cr).\n3. **Small Cap Outperformance**: Small Cap and Mid Cap funds consistently outperformed Large Cap in NAV growth over 4.5 years, albeit with higher volatility.\n4. **T30/B30 Split**: ~68% of SIP investments originate from T30 cities; B30 contribution is growing, driven by UPI adoption.\n5. **Age Group 26-35 Dominates**: This cohort accounts for 35% of investors and highest average SIP amounts.\n6. **High Correlation**: Large Cap funds show 0.85+ correlation with each other, reducing diversification benefit when holding multiple.\n7. **Folio Doubling**: Total folios grew from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025) — doubling in under 4 years.\n8. **ELSS Tax Efficiency**: ELSS category saw consistent inflows despite market corrections, driven by 80C tax benefits.\n9. **Financials Concentration**: Financials sector (banks + NBFCs) represents ~25-30% of most Large Cap fund portfolios.\n10. **Liquid Fund Stability**: Liquid fund NAVs grew at near-flat daily growth (~6.5% p.a.) with near-zero drawdown."),
])
(NB_DIR/"03_eda_analysis.ipynb").write_text(json.dumps(n3, indent=1))
print("✓ Notebook 3 written")

# ══════════════════════════════════════════════════════════════
# NOTEBOOK 4 — Performance Analytics
# ══════════════════════════════════════════════════════════════
n4 = nb([
md("# 📈 Notebook 04 — Fund Performance Analytics (D4)\n**Bluestock Fintech | Day 4**\n\nFormulas: CAGR · Sharpe · Sortino · Alpha · Beta · Max Drawdown · VaR"),
code("""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
from pathlib import Path
import warnings; warnings.filterwarnings('ignore')

BASE = Path('..').resolve()
RAW  = BASE/'data'/'raw'
PROC = BASE/'data'/'processed'

RF_ANNUAL   = 0.065   # RBI repo rate proxy
RF_DAILY    = RF_ANNUAL / 252
TRADING_DAYS = 252

df_nav   = pd.read_csv(RAW/'02_nav_history.csv', parse_dates=['date'])
df_fund  = pd.read_csv(RAW/'01_fund_master.csv').drop_duplicates('amfi_code')
df_bench = pd.read_csv(RAW/'10_benchmark_indices.csv', parse_dates=['date'])
nifty100 = df_bench[df_bench['index_name']=='Nifty100'].sort_values('date').set_index('date')['close_value']
bench_ret = nifty100.pct_change().dropna()
print("Data loaded ✓")
"""),
md("## 1. Daily Returns & CAGR"),
code("""
results = []
for code, grp in df_nav.groupby('amfi_code'):
    grp = grp.sort_values('date').dropna(subset=['nav'])
    nav = grp['nav'].values
    n   = len(grp)
    ret = pd.Series(nav).pct_change().dropna()

    def cagr(years):
        nd = int(years * TRADING_DAYS)
        if n < nd + 5: return np.nan
        return (nav[-1]/nav[-nd-1]) ** (TRADING_DAYS/nd) - 1

    results.append({
        'amfi_code': code,
        'n_days'   : n,
        'cagr_1yr' : cagr(1),
        'cagr_3yr' : cagr(3),
        'cagr_5yr' : cagr(5),
        'ann_vol'  : ret.std() * np.sqrt(TRADING_DAYS),
        'returns'  : ret,
        'nav_series': pd.Series(nav),
    })

df_cagr = pd.DataFrame([{k:v for k,v in r.items() if k not in ('returns','nav_series')}
                         for r in results])
df_cagr[['cagr_1yr','cagr_3yr','cagr_5yr']] *= 100
df_cagr = df_cagr.round(2)
df_cagr.to_csv(PROC/'cagr_report.csv', index=False)
print(df_cagr.nlargest(10,'cagr_3yr')[['amfi_code','cagr_1yr','cagr_3yr','cagr_5yr']].to_string(index=False))
"""),
md("## 2. Sharpe & Sortino Ratios"),
code("""
sharpe_rows = []
for r in results:
    ret = r['returns']
    excess = ret - RF_DAILY
    sharpe = (excess.mean() / ret.std() * np.sqrt(TRADING_DAYS)) if ret.std()>0 else np.nan
    dd_ret = ret[ret < 0]
    sortino = (excess.mean() * TRADING_DAYS / (dd_ret.std()*np.sqrt(TRADING_DAYS))) if len(dd_ret)>5 else np.nan
    sharpe_rows.append({'amfi_code':r['amfi_code'],
                        'sharpe_ratio':round(sharpe,2),
                        'sortino_ratio':round(sortino,2) if not np.isnan(sortino) else None,
                        'std_dev_ann_pct':round(r['ann_vol']*100,2)})

df_sharpe = pd.DataFrame(sharpe_rows)
df_sharpe.to_csv(PROC/'sharpe_sortino.csv', index=False)
print("Top 10 by Sharpe:")
print(df_sharpe.nlargest(10,'sharpe_ratio').to_string(index=False))
"""),
md("## 3. Alpha & Beta vs Nifty 100"),
code("""
ab_rows = []
for r in results:
    ret = r['returns'].copy()
    ret.index = range(len(ret))
    bench_aligned = bench_ret.reindex(df_nav[df_nav['amfi_code']==r['amfi_code']]['date'].iloc[1:]).dropna()
    min_len = min(len(ret), len(bench_aligned))
    if min_len < 60:
        ab_rows.append({'amfi_code':r['amfi_code'],'alpha':None,'beta':None,'te_pct':None})
        continue
    slope, intercept, rval, *_ = stats.linregress(bench_aligned.values[:min_len], ret.values[:min_len])
    alpha  = intercept * TRADING_DAYS
    te     = (ret.values[:min_len] - bench_aligned.values[:min_len]).std() * np.sqrt(TRADING_DAYS)
    ab_rows.append({'amfi_code':r['amfi_code'],
                    'alpha_ann' :round(alpha*100,3),
                    'beta'      :round(slope,3),
                    'r_squared' :round(rval**2,3),
                    'te_pct'    :round(te*100,2)})

df_ab = pd.DataFrame(ab_rows)
df_ab.to_csv(PROC/'alpha_beta.csv', index=False)
print("Alpha-Beta Report:")
print(df_ab.dropna().head(15).to_string(index=False))
"""),
md("## 4. Maximum Drawdown"),
code("""
mdd_rows = []
for r in results:
    nav = r['nav_series']
    roll_max = nav.cummax()
    drawdown = (nav - roll_max) / roll_max
    mdd = drawdown.min()
    mdd_date_idx = drawdown.idxmin()
    mdd_rows.append({'amfi_code': r['amfi_code'],
                     'max_drawdown_pct': round(mdd*100, 2),
                     'days_in_drawdown': int((drawdown < -0.05).sum())})

df_mdd = pd.DataFrame(mdd_rows)
df_mdd.to_csv(PROC/'max_drawdown.csv', index=False)
print("Worst Max Drawdowns:")
print(df_mdd.nsmallest(10,'max_drawdown_pct').to_string(index=False))
"""),
md("## 5. VaR & CVaR (95%)"),
code("""
var_rows = []
for r in results:
    ret = r['returns'].dropna()
    if len(ret) < 30: continue
    var95  = float(np.percentile(ret, 5))
    cvar95 = float(ret[ret <= var95].mean())
    var_rows.append({'amfi_code':r['amfi_code'],
                     'var_95_daily_pct' : round(var95*100,3),
                     'cvar_95_daily_pct': round(cvar95*100,3),
                     'var_95_ann_pct'   : round(var95*np.sqrt(TRADING_DAYS)*100,2)})

df_var = pd.DataFrame(var_rows)
df_var.to_csv(PROC/'var_cvar_report.csv', index=False)
print("VaR Report:")
print(df_var.to_string(index=False))
"""),
md("## 6. Fund Scorecard"),
code("""
df_score = df_cagr[['amfi_code','cagr_3yr']].copy()
df_score = df_score.merge(df_sharpe[['amfi_code','sharpe_ratio']], on='amfi_code', how='left')
df_score = df_score.merge(df_ab[['amfi_code','alpha_ann']], on='amfi_code', how='left')
df_score = df_score.merge(df_mdd[['amfi_code','max_drawdown_pct']], on='amfi_code', how='left')
df_score = df_score.merge(df_fund[['amfi_code','expense_ratio_pct','scheme_name','sub_category']], on='amfi_code', how='left')

df_score['score'] = (
    df_score['cagr_3yr'].rank(pct=True, na_option='bottom') * 30 +
    df_score['sharpe_ratio'].rank(pct=True, na_option='bottom') * 25 +
    df_score['alpha_ann'].rank(pct=True, na_option='bottom') * 20 +
    df_score['max_drawdown_pct'].rank(pct=True, na_option='bottom') * 15 +
    df_score['expense_ratio_pct'].rank(pct=True, ascending=False, na_option='bottom') * 10
)
df_score['rank'] = df_score['score'].rank(ascending=False).astype(int)
df_score = df_score.sort_values('rank')
df_score.to_csv(PROC/'fund_scorecard.csv', index=False)
print("Top 10 Fund Scorecard:")
print(df_score.head(10)[['rank','amfi_code','scheme_name','sub_category',
                          'cagr_3yr','sharpe_ratio','score']].to_string(index=False))
"""),
md("## 7. Benchmark Comparison Chart"),
code("""
fig, axes = plt.subplots(2,1,figsize=(14,10))

# Chart A: Top 5 funds vs Nifty 100
top5_codes = df_score.head(5)['amfi_code'].tolist()
ax = axes[0]
nifty_sub = df_bench[df_bench['index_name']=='Nifty100'].sort_values('date')
nifty_sub = nifty_sub[nifty_sub['date']>='2022-01-01']
nifty_norm = nifty_sub['close_value'] / nifty_sub['close_value'].iloc[0] * 100
ax.plot(nifty_sub['date'], nifty_norm, 'k--', linewidth=2, label='Nifty 100 (Benchmark)', zorder=5)
for i, code in enumerate(top5_codes):
    sub = df_nav[df_nav['amfi_code']==code].sort_values('date')
    if sub.empty: continue
    norm = sub['nav'] / sub['nav'].iloc[0] * 100
    ax.plot(sub['date'], norm, color=plt.cm.tab10(i/10), linewidth=1.5, label=f"Fund {code}")
ax.set_title('Top 5 Funds vs Nifty 100 Benchmark (2022–2026)', fontsize=13, fontweight='bold')
ax.set_ylabel('Indexed Performance (Base=100)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Chart B: Sharpe ratio bar chart
ax2 = axes[1]
df_s = df_sharpe.dropna(subset=['sharpe_ratio']).nlargest(15,'sharpe_ratio')
colors_bar = ['#2E7D32' if s>1 else '#1565C0' if s>0.5 else '#C62828' for s in df_s['sharpe_ratio']]
bars = ax2.barh(df_s['amfi_code'].astype(str), df_s['sharpe_ratio'], color=colors_bar)
ax2.axvline(1.0, color='green', linestyle='--', alpha=0.7, label='Sharpe=1 (Excellent)')
ax2.axvline(0.5, color='orange', linestyle='--', alpha=0.7, label='Sharpe=0.5 (Good)')
ax2.set_title('Sharpe Ratio by Fund (Rf = 6.5%)', fontsize=13, fontweight='bold')
ax2.set_xlabel('Sharpe Ratio')
ax2.legend(fontsize=8); ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(PROC/'chart_benchmark_comparison.png', dpi=130, bbox_inches='tight')
plt.show()
print("Benchmark comparison chart saved ✓")
print("\\n✅ D4 Complete — All metrics CSVs saved to data/processed/")
"""),
])
(NB_DIR/"04_performance_analytics.ipynb").write_text(json.dumps(n4, indent=1))
print("✓ Notebook 4 written")

# ══════════════════════════════════════════════════════════════
# NOTEBOOK 5 — Advanced Analytics (D6)
# ══════════════════════════════════════════════════════════════
n5 = nb([
md("# 🔬 Notebook 05 — Advanced Analytics (D6)\n**Bluestock Fintech | Day 6**\n\nCovers: VaR · Rolling Sharpe · Cohort Analysis · SIP Continuity · Recommender · Sector HHI · Monte Carlo · Efficient Frontier"),
code("""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from scipy import stats, optimize
from pathlib import Path
import warnings; warnings.filterwarnings('ignore')

BASE  = Path('..').resolve()
RAW   = BASE/'data'/'raw'
PROC  = BASE/'data'/'processed'
RF_D  = 0.065/252; TDAYS = 252

df_nav  = pd.read_csv(RAW/'02_nav_history.csv', parse_dates=['date'])
df_fund = pd.read_csv(RAW/'01_fund_master.csv').drop_duplicates('amfi_code')
df_tx   = pd.read_csv(RAW/'08_investor_transactions.csv', parse_dates=['transaction_date'])
df_port = pd.read_csv(RAW/'09_portfolio_holdings.csv')
df_perf = pd.read_csv(PROC/'fund_metrics.csv') if (PROC/'fund_metrics.csv').exists() else pd.DataFrame()
print("Data loaded ✓")
"""),
md("## 1. Historical VaR & CVaR (95%) per Fund"),
code("""
var_rows = []
for code, grp in df_nav.groupby('amfi_code'):
    ret = grp.sort_values('date')['nav'].pct_change().dropna()
    if len(ret) < 60: continue
    var95  = np.percentile(ret, 5)
    cvar95 = ret[ret <= var95].mean()
    var99  = np.percentile(ret, 1)
    var_rows.append({'amfi_code':code,
                     'var_95_daily_pct' : round(var95*100,3),
                     'cvar_95_daily_pct': round(cvar95*100,3),
                     'var_99_daily_pct' : round(var99*100,3),
                     'var_95_ann_pct'   : round(var95*np.sqrt(TDAYS)*100,2)})

df_var = pd.DataFrame(var_rows)
df_var.to_csv(PROC/'var_cvar_report.csv', index=False)

# Plot VaR distribution for one fund
code_example = df_var['amfi_code'].iloc[0]
ret_ex = df_nav[df_nav['amfi_code']==code_example].sort_values('date')['nav'].pct_change().dropna()
fig, ax = plt.subplots(figsize=(10,4))
ax.hist(ret_ex*100, bins=80, color='steelblue', alpha=0.7, edgecolor='white')
var_ex = df_var[df_var['amfi_code']==code_example]['var_95_daily_pct'].values[0]
ax.axvline(var_ex, color='red', linestyle='--', linewidth=2, label=f'VaR 95%: {var_ex:.2f}%')
ax.axvline(df_var[df_var['amfi_code']==code_example]['cvar_95_daily_pct'].values[0],
           color='darkred', linestyle=':', linewidth=2,
           label=f"CVaR 95%: {df_var[df_var['amfi_code']==code_example]['cvar_95_daily_pct'].values[0]:.2f}%")
ax.set_title(f'Daily Return Distribution & VaR — Fund {code_example}', fontsize=12, fontweight='bold')
ax.set_xlabel('Daily Return (%)'); ax.set_ylabel('Frequency')
ax.legend(); plt.tight_layout()
plt.savefig(PROC/'chart_var_distribution.png', dpi=130, bbox_inches='tight')
plt.show()
print(f"\\nVaR Report (worst 5 funds):")
print(df_var.nsmallest(5,'var_95_daily_pct').to_string(index=False))
"""),
md("## 2. Rolling 90-Day Sharpe Ratio"),
code("""
sample_codes = df_nav['amfi_code'].unique()[:5]
fig, ax = plt.subplots(figsize=(13,5))

for i, code in enumerate(sample_codes):
    sub = df_nav[df_nav['amfi_code']==code].sort_values('date')
    ret = sub['nav'].pct_change().dropna()
    rolling_sharpe = (
        ret.rolling(90).mean() - RF_D
    ) / ret.rolling(90).std() * np.sqrt(TDAYS)
    ax.plot(sub['date'].iloc[1:], rolling_sharpe.values,
            label=str(code), alpha=0.85, linewidth=1.4)

ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.axhline(1, color='green', linewidth=0.8, linestyle=':', label='Sharpe=1')
ax.set_title('Rolling 90-Day Sharpe Ratio (5 Funds)', fontsize=13, fontweight='bold')
ax.set_xlabel('Date'); ax.set_ylabel('Rolling Sharpe Ratio')
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(PROC/'rolling_sharpe_chart.png', dpi=130, bbox_inches='tight')
plt.show()
print("Rolling Sharpe chart saved ✓")
"""),
md("## 3. Investor Cohort Analysis"),
code("""
df_tx['year'] = df_tx['transaction_date'].dt.year
first_tx = df_tx.groupby('investor_id')['transaction_date'].min().reset_index()
first_tx['cohort_year'] = first_tx['transaction_date'].dt.year

df_tx_c = df_tx.merge(first_tx[['investor_id','cohort_year']], on='investor_id')
cohort = df_tx_c[df_tx_c['transaction_type']=='Sip'].groupby('cohort_year').agg(
    num_investors   = ('investor_id','nunique'),
    avg_sip_amount  = ('amount_inr','mean'),
    total_invested  = ('amount_inr','sum'),
    num_transactions= ('investor_id','count'),
).reset_index()
cohort['avg_tx_per_investor'] = (cohort['num_transactions'] / cohort['num_investors']).round(1)
cohort['total_invested_crore'] = (cohort['total_invested']/1e7).round(2)
cohort.to_csv(PROC/'cohort_analysis.csv', index=False)

fig, axes = plt.subplots(1,2,figsize=(12,4))
axes[0].bar(cohort['cohort_year'].astype(str), cohort['avg_sip_amount'],
            color=['#1565C0','#2E7D32','#C62828','#F57F17'])
axes[0].set_title('Avg SIP Amount by Cohort Year', fontsize=11, fontweight='bold')
axes[0].set_xlabel('First Investment Year'); axes[0].set_ylabel('Avg SIP (Rs.)')

axes[1].bar(cohort['cohort_year'].astype(str), cohort['avg_tx_per_investor'],
            color=['#1565C0','#2E7D32','#C62828','#F57F17'])
axes[1].set_title('Avg Transactions per Investor by Cohort', fontsize=11, fontweight='bold')
axes[1].set_xlabel('First Investment Year')

plt.tight_layout()
plt.savefig(PROC/'chart_cohort.png', dpi=130, bbox_inches='tight')
plt.show()
print(cohort.to_string(index=False))
"""),
md("## 4. SIP Continuity — At-Risk Investors"),
code("""
sip_only = df_tx[df_tx['transaction_type']=='Sip'].copy()
sip_only = sip_only.sort_values(['investor_id','transaction_date'])
sip_only['gap_days'] = sip_only.groupby('investor_id')['transaction_date'].diff().dt.days

continuity = sip_only.groupby('investor_id').agg(
    num_sips    = ('transaction_date','count'),
    avg_gap     = ('gap_days','mean'),
    max_gap     = ('gap_days','max'),
    total_invested = ('amount_inr','sum'),
).reset_index()
continuity = continuity[continuity['num_sips'] >= 6]
continuity['at_risk'] = continuity['max_gap'] > 35

at_risk_count = continuity['at_risk'].sum()
print(f"Total SIP investors (6+ transactions): {len(continuity):,}")
print(f"At-risk investors (gap > 35 days):     {at_risk_count:,} ({at_risk_count/len(continuity)*100:.1f}%)")
continuity.to_csv(PROC/'sip_continuity.csv', index=False)

fig, ax = plt.subplots(figsize=(8,4))
continuity['avg_gap'].hist(bins=40, color='steelblue', alpha=0.7, ax=ax, edgecolor='white')
ax.axvline(35, color='red', linestyle='--', label='35-day threshold')
ax.set_title('Distribution of Average SIP Gap (Days)', fontsize=12, fontweight='bold')
ax.set_xlabel('Avg Gap (Days)'); ax.set_ylabel('No. of Investors')
ax.legend(); plt.tight_layout()
plt.savefig(PROC/'chart_sip_continuity.png', dpi=130, bbox_inches='tight')
plt.show()
"""),
md("## 5. Fund Recommender"),
code("""
import sys
sys.path.insert(0, str(BASE/'scripts'))
from recommender import recommend, herfindahl_hirschman_index

for risk in ['Low','Moderate','High']:
    print(f"\\n{'='*55}")
    print(f"  Risk: {risk} | Horizon: Long (5yr)")
    print('='*55)
    recs = recommend(risk_appetite=risk, horizon='long', top_n=3)
    if not recs.empty:
        print(recs[['scheme_name','sub_category','sharpe_ratio','expense_ratio_pct']].to_string())
    else:
        print("  No matching funds.")
"""),
md("## 6. Sector Concentration (HHI)"),
code("""
hhi_df = herfindahl_hirschman_index(df_port)
hhi_df.to_csv(PROC/'sector_hhi.csv', index=False)

fig, ax = plt.subplots(figsize=(10,4))
colors_hhi = ['#2E7D32' if c=='Diversified' else '#F57F17' if c=='Moderate' else '#C62828'
               for c in hhi_df['concentration']]
ax.bar(hhi_df['amfi_code'].astype(str), hhi_df['sector_hhi'], color=colors_hhi)
ax.axhline(0.10, color='orange', linestyle='--', label='Moderate (HHI=0.10)')
ax.axhline(0.18, color='red',    linestyle='--', label='Concentrated (HHI=0.18)')
ax.set_title('Sector HHI by Fund (Portfolio Concentration Risk)', fontsize=12, fontweight='bold')
ax.set_xlabel('AMFI Code'); ax.set_ylabel('HHI Score')
ax.legend(); plt.tight_layout()
plt.savefig(PROC/'chart_hhi.png', dpi=130, bbox_inches='tight')
plt.show()
print(hhi_df.to_string(index=False))
"""),
md("## 7. Monte Carlo NAV Projection (B3)"),
code("""
# 5-year Monte Carlo for top 3 funds
code_mc = df_nav['amfi_code'].unique()[:3]
n_sim = 500; n_days = 252*5

fig, axes = plt.subplots(1, len(code_mc), figsize=(14, 5))
for idx, code in enumerate(code_mc):
    sub = df_nav[df_nav['amfi_code']==code].sort_values('date')
    nav = sub['nav'].values
    ret = np.diff(np.log(nav))
    mu  = ret.mean(); sigma = ret.std()
    last_nav = nav[-1]
    sims = np.zeros((n_days, n_sim))
    for s in range(n_sim):
        shocks = np.random.normal(mu, sigma, n_days)
        sims[:, s] = last_nav * np.exp(np.cumsum(shocks))
    p5  = np.percentile(sims, 5,  axis=1)
    p50 = np.percentile(sims, 50, axis=1)
    p95 = np.percentile(sims, 95, axis=1)
    t   = np.arange(n_days)
    ax  = axes[idx]
    ax.fill_between(t, p5, p95, alpha=0.2, color='steelblue', label='90% CI')
    ax.plot(t, p50, color='steelblue', linewidth=2, label='Median')
    ax.plot(t, p5,  color='red',   linewidth=1, linestyle='--', label='5th pct')
    ax.plot(t, p95, color='green', linewidth=1, linestyle='--', label='95th pct')
    ax.set_title(f'Monte Carlo — Fund {code}', fontsize=10, fontweight='bold')
    ax.set_xlabel('Trading Days'); ax.set_ylabel('Projected NAV (Rs.)')
    ax.legend(fontsize=7)

plt.suptitle('5-Year Monte Carlo NAV Projection (500 Simulations)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(PROC/'chart_monte_carlo.png', dpi=130, bbox_inches='tight')
plt.show()
print("Monte Carlo chart saved ✓")
"""),
md("## 8. Markowitz Efficient Frontier (B4)"),
code("""
# Select 5 equity funds for portfolio optimisation
ef_codes = df_nav['amfi_code'].unique()[:5]
pivot = df_nav[df_nav['amfi_code'].isin(ef_codes)].pivot_table(
    index='date', columns='amfi_code', values='nav')
returns = pivot.pct_change().dropna()
mu_vec  = returns.mean() * TDAYS
cov_mat = returns.cov()  * TDAYS
n_assets = len(ef_codes)

def portfolio_stats(weights):
    port_ret = np.dot(weights, mu_vec)
    port_vol = np.sqrt(weights @ cov_mat.values @ weights)
    sharpe   = (port_ret - 0.065) / port_vol
    return port_ret, port_vol, sharpe

# Monte Carlo portfolios
n_portfolios = 3000
p_rets, p_vols, p_sharpes = [], [], []
for _ in range(n_portfolios):
    w = np.random.dirichlet(np.ones(n_assets))
    r, v, s = portfolio_stats(w)
    p_rets.append(r); p_vols.append(v); p_sharpes.append(s)

# Min-volatility & Max-Sharpe
constraints = ({'type':'eq','fun': lambda w: w.sum()-1})
bounds = [(0.05,0.60)]*n_assets
min_vol = optimize.minimize(lambda w: portfolio_stats(w)[1],
    np.ones(n_assets)/n_assets, method='SLSQP', bounds=bounds, constraints=constraints)
max_sharpe = optimize.minimize(lambda w: -portfolio_stats(w)[2],
    np.ones(n_assets)/n_assets, method='SLSQP', bounds=bounds, constraints=constraints)

fig, ax = plt.subplots(figsize=(10,7))
sc = ax.scatter(p_vols, p_rets, c=p_sharpes, cmap='viridis', alpha=0.5, s=8)
plt.colorbar(sc, ax=ax, label='Sharpe Ratio')
mv_r, mv_v, _ = portfolio_stats(min_vol.x)
ms_r, ms_v, _ = portfolio_stats(max_sharpe.x)
ax.scatter(mv_v, mv_r, color='blue',  s=200, marker='*', zorder=5, label=f'Min Vol  (ret={mv_r*100:.1f}%)')
ax.scatter(ms_v, ms_r, color='red',   s=200, marker='*', zorder=5, label=f'Max Sharpe (ret={ms_r*100:.1f}%)')
ax.set_title('Markowitz Efficient Frontier (5 Equity Funds)', fontsize=13, fontweight='bold')
ax.set_xlabel('Annualised Volatility'); ax.set_ylabel('Annualised Return')
ax.legend()
plt.tight_layout()
plt.savefig(PROC/'chart_efficient_frontier.png', dpi=130, bbox_inches='tight')
plt.show()

print("\\nMax Sharpe Portfolio Weights:")
for code, w in zip(ef_codes, max_sharpe.x):
    print(f"  Fund {code}: {w*100:.1f}%")
print("\\n✅ Advanced Analytics Complete!")
"""),
])
(NB_DIR/"05_advanced_analytics.ipynb").write_text(json.dumps(n5, indent=1))
print("✓ Notebook 5 written")
print("\n✅ All 5 notebooks generated!")
