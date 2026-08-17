# Sprint 4 — Dashboard & Valuation Module

Run from the project root:

```powershell
python -m pip install -r requirements.txt
streamlit run src/dashboard/app.py
```

Dashboard screens: Home, Company Profile, Screener, Peers, Trends, Sectors, Capital Allocation, Reports & Valuation.

Valuation output is generated from the SQLite `market_cap` and `financial_ratios` tables and written to `output/valuation_summary.xlsx` and `output/valuation_flags.csv`.
