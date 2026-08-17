from pathlib import Path
import sqlite3
import pandas as pd
from src.analytics.valuation import compute_valuation

ROOT=Path(__file__).resolve().parents[2]

def test_valuation_has_92_companies():
    d=compute_valuation()
    assert len(d)==92
    assert d.company_id.nunique()==92

def test_required_valuation_columns():
    d=compute_valuation()
    required=['fcf_yield_pct','pe_ratio','pb_ratio','ev_ebitda','pe_5yr_median','sector_median_pe','valuation_flag']
    assert all(c in d.columns for c in required)

def test_valuation_flags_are_valid():
    d=compute_valuation()
    assert set(d.valuation_flag.dropna()).issubset({'Caution','Discount','Fair','Insufficient Data'})

def test_discount_and_caution_logic():
    d=compute_valuation()
    q=d.dropna(subset=['pe_ratio','sector_median_pe'])
    assert ((q.loc[q.pe_ratio>q.sector_median_pe*1.15,'valuation_flag']=='Caution')).all()
    assert ((q.loc[q.pe_ratio<q.sector_median_pe*0.70,'valuation_flag']=='Discount')).all()

def test_valuation_outputs_exist():
    assert (ROOT/'output/valuation_summary.xlsx').exists()
    assert (ROOT/'output/valuation_flags.csv').exists()

def test_dashboard_db_helpers():
    from src.dashboard.db import get_companies,get_ratios,get_pl,get_bs,get_cf,get_sectors,get_peers,get_valuation
    assert len(get_companies())==92
    assert not get_ratios('ABB').empty
    assert not get_pl('ABB').empty
    assert not get_bs('ABB').empty
    assert not get_cf('ABB').empty
    assert not get_sectors('ABB').empty
    assert not get_peers().empty
    assert len(get_valuation())==92

def test_dashboard_structure():
    pages=sorted((ROOT/'src/dashboard/pages').glob('*.py'))
    assert len(pages)==8
    names=[p.name for p in pages]
    assert names==['01_home.py','02_profile.py','03_screener.py','04_peers.py','05_trends.py','06_sectors.py','07_capital_allocation.py','08_reports.py']
