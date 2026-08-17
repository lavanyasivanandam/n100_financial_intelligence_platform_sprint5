# Sprint 2 — Financial Ratio Engine

Implemented against the real Sprint-1 database and the supplied Sprint-2 specification.

- financial_ratios: 1155 rows across 92 companies
- KPI columns: 48
- capital allocation: 1056 available cash-flow company-years
- screener preview: 38 companies using latest common P&L + BS year
- Financials D/E warning suppression: 23 companies
- edge-log entries: 6244
- FK violations: 0

The supplied financial_ratios.xlsx remains untouched under data/supporting/. The SQLite financial_ratios table is computed by the Sprint-2 engine.
