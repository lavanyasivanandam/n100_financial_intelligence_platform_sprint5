# Sprint 5 Retrospective

## Scope completed
- NLP analysis parser and unmatched-text audit
- Parsed CAGR cross-check against Sprint 2 ratio engine where source data permits
- 12 positive and 12 negative rule framework with confidence scores
- Cash-flow intelligence: CFO quality, CapEx intensity, distress, deleveraging, capital allocation
- Capital allocation latest-year summary and year-over-year pattern changes
- Two-page company tearsheets
- Sector reports
- One-page-per-company portfolio summary

## Build results
- Companies: 92
- Pros/cons coverage: 92 companies
- Analysis parsed rows: 51
- Parse failures logged: 13
- CAGR manual-review divergences >5 percentage points: 1
- Cash-flow intelligence rows: 92
- Distress alerts: 13
- Pattern changes: 418
- Tearsheets: 92 generated, 0 skipped
- Sector reports: 10
- Portfolio pages: 92
- Minimum tearsheet size: 54822 bytes

## Specification notes
- Pro Rule 8 uses `market_cap.dividend_yield_pct`, because the specification explicitly says Dividend Yield while the ratio table stores payout ratio separately.
- Pro Rule 11 is implemented using the literal `Revenue CAGR > PAT CAGR` condition from the task text; its supplied explanatory sentence says revenue is growing slower than profits, which conflicts with that condition. The implementation does not silently change the requested condition.
- The exit requirement of at least one pro and one con per company is enforced with explicit `NO_PRO_SIGNAL` / `NO_CON_SIGNAL` records when no configured rule fires. These are clearly marked as no-signal records rather than being presented as genuine positive/negative financial signals.
