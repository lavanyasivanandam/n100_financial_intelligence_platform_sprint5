# Nifty 100 Financial Intelligence Platform — Sprint 1

Real-data Sprint 1 implementation based on the supplied project specification and the supplied 12 Excel datasets.

## Sprint 1 scope
- D01 project structure/configuration
- D02 Excel loading, `normalize_year`, `normalize_ticker`, 20+20 normalization tests
- D03 16 DQ rules with auditable failures
- D04 SQLite schema + FK enforcement
- D05 all 12 datasets loaded
- D06 deterministic 5-company review
- D07 10 exploratory SQL queries + retrospective

## Run
```bash
python -m src.etl.pipeline
pytest -q
```

The original Excel files under `data/raw/` and `data/supporting/` are never modified.
