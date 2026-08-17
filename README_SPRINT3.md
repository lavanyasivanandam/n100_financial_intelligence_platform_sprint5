# Nifty 100 Financial Intelligence Platform — Sprint 3

Sprint 3 adds the Screen & Peer Comparison Engine on top of the verified Sprint 2 SQLite database.

Run:
```bash
pip install -r requirements.txt
python -m src.screener.run_all
pytest -q
```

`config/screener_config.yaml` is analyst-editable. It defines the 15 filterable screener metrics plus the six named presets. D/E max filters exempt the Financials sector; Debt-Free companies pass any ICR minimum. The screener uses the latest P&L year as the financial anchor and latest market-cap observation.

Outputs: `output/screener_output.xlsx`, `output/peer_comparison.xlsx`, `reports/radar_charts/*.png`, SQLite `peer_percentiles`, and `output/sprint3_summary.json`.

## Custom thresholds from the command line
Example:
```bash
python -m src.screener.engine --preset custom --threshold roe_min=15 --threshold de_max=1 --threshold fcf_min=0 --threshold revenue_cagr_5yr_min=10
```
Multiple `--threshold key=value` arguments are combined with AND logic.
