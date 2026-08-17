# Sprint 4 — Dashboard & Valuation Retrospective

## Scope implemented
- Streamlit dashboard with exactly 8 navigation screens.
- Home market summary and top-5 composite table.
- Company profile search/autocomplete, KPI card, revenue/net-profit and ROE/ROCE charts.
- Screener with 10 sidebar sliders, 6 Sprint-3 presets, result count and CSV export.
- Peer comparison with Plotly Scatterpolar radar and benchmark-highlighted KPI table.
- Trend analysis with company search and up to 3 metrics over a 10-year window.
- Sector analysis with Revenue/ROE/Market-Cap bubble chart and median KPI chart.
- Capital allocation pattern explorer with company list and Plotly treemap.
- Annual report viewer with BSE links and unavailable badges; valuation is a tab on screen 08.

## Valuation
- FCF yield = FCF / market cap x 100.
- Latest P/E, P/B, EV/EBITDA and dividend yield are taken from the latest market-cap observation.
- 5-year median P/E is the median of the latest five available market-cap P/E observations per company.
- Sector median P/E is calculated from the latest market-cap observation for companies in the same broad sector.
- Valuation flag: Caution when P/E > sector median x 1.15; Discount when P/E < sector median x 0.70; otherwise Fair.

## Verification
- 92 valuation rows generated.
- 92 unique companies covered.
- 32 Caution, 30 Fair, 30 Discount flags on the supplied data.
- Dashboard latest-company query benchmarked at ~0.01 seconds in the build environment; chart rendering is handled by Streamlit/Plotly at runtime.
- Combined Sprint 1–4 automated tests: 134 passed.

## Known implementation note
The brief specifies eight dashboard page files (`01_home.py` through `08_reports.py`) while also requiring a valuation module. To preserve exactly eight dashboard screens, valuation is implemented as a tab inside screen 08 (`Reports & Valuation`) rather than creating a ninth screen.
