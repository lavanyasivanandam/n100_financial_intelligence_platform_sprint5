import pandas as pd,numpy as np
from src.screener.engine import apply_filters

def frame():
 return pd.DataFrame({'company_id':['A','B'],'company_name':['A','B'],'return_on_equity_pct':[20,10],'debt_to_equity':[.5,2.],'free_cash_flow_cr':[100,-10],'revenue_cagr_5yr':[12,5],'pat_cagr_5yr':[15,2],'operating_profit_margin_pct':[20,8],'pe_ratio':[15,25],'pb_ratio':[2,4],'dividend_yield_pct':[2,.5],'interest_coverage':[3,np.nan],'interest_coverage_label':['Adequate','Debt Free'],'market_cap_crore':[100000,50000],'net_profit_cr':[1000,300],'eps_cagr_5yr':[10,2],'asset_turnover':[1.5,.5],'sales_cr':[10000,4000],'broad_sector':['Industrials','Financials'],'composite_quality_score':[80,50],'fcf_cagr_5yr':[10,5],'cfo_pat_ratio':[1.2,.8],'fcf_positive_flag':[1,0],'return_on_capital_employed_pct':[18,10],'net_profit_margin_pct':[10,5],'revenue_cagr_3yr':[12,5]})
def test_01_roe():assert len(apply_filters(frame(),{'roe_min':15}))==1
def test_02_de_financials_exempt():assert len(apply_filters(frame(),{'de_max':1}))==2
def test_03_fcf():assert len(apply_filters(frame(),{'fcf_min':0}))==1
def test_04_rev5():assert len(apply_filters(frame(),{'revenue_cagr_5yr_min':10}))==1
def test_05_pat5():assert len(apply_filters(frame(),{'pat_cagr_5yr_min':10}))==1
def test_06_opm():assert len(apply_filters(frame(),{'opm_min':10}))==1
def test_07_pe():assert len(apply_filters(frame(),{'pe_max':20}))==1
def test_08_pb():assert len(apply_filters(frame(),{'pb_max':3}))==1
def test_09_dividend():assert len(apply_filters(frame(),{'dividend_yield_min':1}))==1
def test_10_icr_debt_free():assert len(apply_filters(frame(),{'icr_min':2}))==2
def test_11_market_cap():assert len(apply_filters(frame(),{'market_cap_min':75000}))==1
def test_12_net_profit():assert len(apply_filters(frame(),{'net_profit_min':500}))==1
def test_13_eps_cagr():assert len(apply_filters(frame(),{'eps_cagr_5yr_min':5}))==1
def test_14_asset_turnover():assert len(apply_filters(frame(),{'asset_turnover_min':1}))==1
