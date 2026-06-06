"""
Bluestock Fintech — Automated HTML Email Report Generator (B5)
Generates weekly performance summary as styled HTML and optionally sends via SMTP.
Usage: python scripts/email_report.py [--send]
"""

import pandas as pd, numpy as np
from pathlib import Path
from datetime import datetime
import smtplib, argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"

def generate_html_report() -> str:
    now = datetime.now().strftime("%d %B %Y")
    sip = pd.read_csv(RAW/"04_monthly_sip_inflows.csv")
    latest_sip = sip.iloc[-1]
    fund = pd.read_csv(RAW/"01_fund_master.csv").drop_duplicates("amfi_code")

    perf_path = PROC/"fund_metrics.csv"
    if perf_path.exists():
        perf = pd.read_csv(perf_path)
        perf = perf.merge(fund[["amfi_code","scheme_name","sub_category"]], on="amfi_code", how="left")
        top5 = perf.sort_values("composite_score", ascending=False).head(5)
        perf_rows = ""
        for _, r in top5.iterrows():
            perf_rows += f"""
            <tr>
                <td>{r.get('scheme_name','N/A')[:40]}</td>
                <td>{r.get('sub_category','')}</td>
                <td style="color:{'green' if r.get('cagr_3yr_pct',0)>0 else 'red'}">
                    {r.get('cagr_3yr_pct','N/A')}%</td>
                <td>{r.get('sharpe_ratio','N/A')}</td>
                <td>{r.get('composite_score','N/A')}</td>
            </tr>"""
    else:
        perf_rows = "<tr><td colspan='5'>Run notebooks to compute metrics</td></tr>"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; margin: 0; padding: 20px; }}
  .container {{ max-width: 700px; margin: auto; background: white; border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
  .header {{ background: linear-gradient(135deg, #1e3a5f, #2196F3);
             color: white; padding: 30px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 24px; }}
  .header p  {{ margin: 5px 0 0; opacity: 0.85; font-size: 13px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; padding: 20px; }}
  .kpi {{ background: #e8f4fd; border-radius: 8px; padding: 16px; text-align: center;
          border-left: 4px solid #2196F3; }}
  .kpi-val {{ font-size: 22px; font-weight: bold; color: #1e3a5f; }}
  .kpi-lbl {{ font-size: 11px; color: #666; margin-top: 4px; }}
  .section  {{ padding: 0 20px 20px; }}
  h2        {{ color: #1e3a5f; border-bottom: 2px solid #2196F3; padding-bottom: 6px; font-size: 16px; }}
  table     {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th        {{ background: #1e3a5f; color: white; padding: 8px 10px; text-align: left; }}
  td        {{ padding: 7px 10px; border-bottom: 1px solid #eee; }}
  tr:hover td {{ background: #f0f7ff; }}
  .footer   {{ background: #1e3a5f; color: #90CAF9; text-align: center;
               padding: 16px; font-size: 11px; }}
  .badge    {{ display:inline-block; padding:3px 8px; border-radius:12px;
               background:#e3f2fd; color:#1565C0; font-size:11px; font-weight:bold; }}
  .disclaimer {{ font-size:10px; color:#999; padding:10px 20px; border-top:1px solid #eee; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📈 Bluestock MF Weekly Report</h1>
    <p>Performance Summary — Week ending {now}</p>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-val">Rs.81L Cr</div>
      <div class="kpi-lbl">Industry AUM (Dec 2025)</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">Rs.{latest_sip['sip_inflow_crore']:,.0f} Cr</div>
      <div class="kpi-lbl">Latest SIP Inflow</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{latest_sip['active_sip_accounts_crore']:.2f} Cr</div>
      <div class="kpi-lbl">Active SIP Accounts</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">26.12 Cr</div>
      <div class="kpi-lbl">Total Folios</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{fund['fund_house'].nunique()}</div>
      <div class="kpi-lbl">Fund Houses Tracked</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{len(fund)}</div>
      <div class="kpi-lbl">Schemes Monitored</div>
    </div>
  </div>

  <div class="section">
    <h2>🏆 Top 5 Funds This Week (by Composite Score)</h2>
    <table>
      <tr>
        <th>Scheme Name</th><th>Category</th>
        <th>3yr CAGR</th><th>Sharpe</th><th>Score</th>
      </tr>
      {perf_rows}
    </table>
  </div>

  <div class="section">
    <h2>📊 Market Insights</h2>
    <ul style="font-size:13px;line-height:1.8;color:#333;">
      <li>SIP inflows crossed <strong>Rs.31,002 Cr</strong> in Dec 2025 — an all-time high.</li>
      <li>Small Cap & Mid Cap categories continue to attract highest net inflows in FY25.</li>
      <li>T30 cities contribute ~68% of total SIP volume; B30 share growing via UPI.</li>
      <li>Age 26–35 cohort dominates SIP registrations — 35% of all investors.</li>
      <li>Index funds gaining traction: Nifty 50 TRI funds now offer expense ratios as low as 0.10%.</li>
    </ul>
  </div>

  <div class="section">
    <h2>⚠️ Risk Alerts</h2>
    <table>
      <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
      <tr><td>Equity Market Volatility (VIX proxy)</td><td>14.2</td>
          <td><span class="badge">Normal</span></td></tr>
      <tr><td>Small Cap Avg Max Drawdown</td><td>-28.5%</td>
          <td><span class="badge" style="background:#fff3e0;color:#e65100;">Monitor</span></td></tr>
      <tr><td>Liquid Fund Avg VaR (95%, daily)</td><td>-0.05%</td>
          <td><span class="badge" style="background:#e8f5e9;color:#2e7d32;">Safe</span></td></tr>
    </table>
  </div>

  <div class="disclaimer">
    ⚠️ Disclaimer: This report is generated for educational/internal purposes only.
    Mutual Fund investments are subject to market risks. Past performance does not guarantee future returns.
    Data sourced from AMFI India. © 2026 Bluestock Fintech Pvt. Ltd.
  </div>

  <div class="footer">
    Bluestock Fintech Pvt. Ltd. | Gurugram, Haryana | analytics@bluestock.in<br>
    <a href="#" style="color:#64B5F6;">Unsubscribe</a> | Generated: {now}
  </div>
</div>
</body>
</html>"""
    return html


def send_email(html: str, to_addr: str, smtp_host: str, smtp_port: int,
               smtp_user: str, smtp_pass: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Bluestock MF Weekly Report — {datetime.now().strftime('%d %b %Y')}"
    msg["From"]    = smtp_user
    msg["To"]      = to_addr
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_addr, msg.as_string())
    print(f"Email sent to {to_addr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--to",   default="intern@bluestock.in")
    args = parser.parse_args()

    html = generate_html_report()
    out  = BASE / "reports" / "weekly_report.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"HTML report saved → {out}")

    if args.send:
        # Configure these via environment variables in production
        import os
        send_email(html, args.to,
                   smtp_host=os.getenv("SMTP_HOST","smtp.gmail.com"),
                   smtp_port=int(os.getenv("SMTP_PORT","465")),
                   smtp_user=os.getenv("SMTP_USER",""),
                   smtp_pass=os.getenv("SMTP_PASS",""))
