# Sprint 1 — Data Foundation Review

## Exit criteria
Specification: SQLite DB loaded, all required tables populated, load audit generated, critical DQ failures resolved before load, and DQ report reviewed.

## Actual result
- Companies in master: 92
- Critical DQ findings in raw data: 786
- Critical records are rejected before database insertion.
- SQLite foreign-key check: see `foreign_key_check.csv`.
- Original source workbooks are preserved unchanged.

## Important specification note
The document calls this a 10-table SQLite database but its Module 1 output explicitly lists 12 named tables. This implementation creates all 12 named tables so all 12 supplied datasets remain represented; the discrepancy is documented rather than silently discarded.

## URL rule
DQ-13 is network-dependent. It is disabled by default for deterministic local builds; set `DQ_CHECK_URLS=true` to run HTTP HEAD checks.

## Manual review
Five deterministic companies: ABB, TCS, HDFCBANK, INFY, RELIANCE.
