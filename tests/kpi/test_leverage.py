from src.analytics.leverage import *
def test_debt_free_zero(): assert debt_to_equity(0,100,200)==0
def test_de_normal(): assert debt_to_equity(100,100,100)==0.5
def test_de_negative_equity_none(): assert debt_to_equity(100,-100,0) is None
def test_icr_zero_interest_none(): assert interest_coverage(100,10,0) is None
def test_icr_debt_free(): assert interest_coverage_label(None,0)=='Debt Free'
def test_icr_risk(): assert interest_coverage_label(1.0,10)=='High Risk'
def test_icr_ok(): assert interest_coverage_label(2.0,10)=='Adequate'
def test_turnover_zero_assets(): assert asset_turnover(100,0) is None
