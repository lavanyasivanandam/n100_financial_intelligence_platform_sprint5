from pathlib import Path
import sqlite3,pandas as pd
ROOT=Path(__file__).resolve().parents[2]
def test_ratio_rows(): 
    c=sqlite3.connect(ROOT/'db/nifty100.db'); n=c.execute('SELECT COUNT(*) FROM financial_ratios').fetchone()[0]; c.close(); assert n>=1100
def test_92_companies():
    c=sqlite3.connect(ROOT/'db/nifty100.db'); n=c.execute('SELECT COUNT(DISTINCT company_id) FROM financial_ratios').fetchone()[0]; c.close(); assert n==92
def test_unique_keys():
    c=sqlite3.connect(ROOT/'db/nifty100.db'); n=c.execute('SELECT COUNT(*) FROM financial_ratios').fetchone()[0]; u=c.execute("SELECT COUNT(DISTINCT company_id||'|'||year) FROM financial_ratios").fetchone()[0]; c.close(); assert n==u
def test_roe_checks(): assert (pd.read_csv(ROOT/'output/roe_spot_checks.csv').absolute_difference_pct<=0.1).all()
def test_screener_range(): assert 15<=len(pd.read_csv(ROOT/'output/screener_preview.csv'))<=50
def test_allocation_rows(): assert len(pd.read_csv(ROOT/'output/capital_allocation.csv'))>=1000
def test_edge_log(): assert (ROOT/'output/ratio_edge_cases.log').exists()
def test_required_columns():
    c=sqlite3.connect(ROOT/'db/nifty100.db'); cols=[x[1] for x in c.execute('PRAGMA table_info(financial_ratios)')]; c.close()
    for x in ['net_profit_margin_pct','operating_profit_margin_pct','return_on_equity_pct','debt_to_equity','interest_coverage','free_cash_flow_cr','capex_cr','earnings_per_share','book_value_per_share','dividend_payout_ratio_pct','total_debt_cr','cash_from_operations_cr','revenue_cagr_5yr','pat_cagr_5yr','eps_cagr_5yr','composite_quality_score']: assert x in cols

def test_financials_de_warning_suppressed():
    c=sqlite3.connect(ROOT/"db/nifty100.db")
    n=c.execute("SELECT COUNT(*) FROM financial_ratios WHERE broad_sector='Financials' AND de_warning_suppressed=1").fetchone()[0]
    c.close()
    assert n>0
def test_roce_source_crosscheck_log_category():
    text=(ROOT/"output/ratio_edge_cases.log").read_text()
    assert "ROCE" in text
