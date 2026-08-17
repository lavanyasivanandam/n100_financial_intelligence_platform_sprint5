from src.analytics.cashflow import *
def test_fcf(): assert free_cash_flow(100,-40)==60
def test_capex(): assert capex(-40)==40
def test_quality_high(): assert cfo_quality_score([(100,80),(120,100)])[1]=='High Quality'
def test_quality_moderate(): assert cfo_quality_score([(50,100)])[1]=='Moderate'
def test_quality_risk(): assert cfo_quality_score([(20,100)])[1]=='Accrual Risk'
def test_intensity_light(): assert capital_intensity(-4,100)[1]=='Light'
def test_intensity_moderate(): assert capital_intensity(-6,100)[1]=='Moderate'
def test_intensity_heavy(): assert capital_intensity(-10,100)[1]=='Capital Intensive'
def test_fcf_conversion_zero(): assert fcf_conversion_rate(10,0) is None
