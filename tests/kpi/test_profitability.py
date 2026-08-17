from src.analytics.profitability import *
def test_npm_normal(): assert net_profit_margin(10,100)==10
def test_npm_zero_sales(): assert net_profit_margin(10,0) is None
def test_roe_normal(): assert return_on_equity(20,10,90)==20
def test_roe_negative_equity(): assert return_on_equity(20,-100,0) is None
def test_roce_normal(): assert roce(30,100,100,100)==10
def test_roa_zero_assets(): assert return_on_assets(20,0) is None
def test_opm_normal(): assert operating_profit_margin(25,100)==25
def test_opm_zero_sales(): assert operating_profit_margin(25,0) is None
