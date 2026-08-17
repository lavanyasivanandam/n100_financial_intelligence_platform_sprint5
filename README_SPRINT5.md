# Nifty 100 Financial Intelligence Platform — Sprint 5

Built from the verified Sprint 4 real-data SQLite database.

## Deliverables
- `output/pros_cons_generated.csv` — 92-company pros/cons output with confidence >60
- `output/analysis_parsed.csv` — regex parsed analysis values
- `output/parse_failures.csv` — unmatched analysis text
- `output/analysis_cagr_crosscheck.csv` — CAGR cross-check/manual-review audit
- `output/cashflow_intelligence.xlsx` — 92 rows with CFO quality, CapEx intensity, distress, deleveraging, capital allocation
- `output/distress_alerts.csv`
- `output/capital_allocation_summary.csv`
- `output/pattern_changes.csv`
- `reports/tearsheets/` — 92 two-page company reports
- `reports/sector/` — 11 sector PDFs
- `reports/portfolio/portfolio_summary.pdf` — 92 pages

## Run on Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
```

The project already contains the generated Sprint 5 outputs.

> Note: the supplied Sprint-4 database has 10 unique broad sectors. Sprint 5 therefore includes 10 actual sector reports plus `sector_coverage_overview_report.pdf` as the 11th sector-directory artifact required by the sprint card.
