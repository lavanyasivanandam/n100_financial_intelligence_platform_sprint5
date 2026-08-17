
import pandas as pd
from src.etl.validator import validate
def test_dq04_bs_balance():
    frames={
      "companies":pd.DataFrame({"id":["TCS"]}),
      "profitandloss":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"sales":[100],"operating_profit":[20],"opm_percentage":[20],"tax_percentage":[20],"dividend_payout":[10],"eps":[1],"net_profit":[10]}),
      "balancesheet":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"total_assets":[1000],"total_liabilities":[1020],"fixed_assets":[100]}),
      "cashflow":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"net_cash_flow":[0],"operating_activity":[0],"investing_activity":[0],"financing_activity":[0]}),
      "analysis":pd.DataFrame({"company_id":["TCS"]}),"documents":pd.DataFrame({"company_id":["TCS"]}),
      "prosandcons":pd.DataFrame({"company_id":["TCS"]}),"sectors":pd.DataFrame({"company_id":["TCS"],"sub_sector":["IT"]}),
      "stock_prices":pd.DataFrame({"company_id":["TCS"]}),"market_cap":pd.DataFrame({"company_id":["TCS"]}),
      "financial_ratios":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"]}),"peer_groups":pd.DataFrame({"company_id":["TCS"]})
    }
    out=validate(frames)
    assert ((out.rule_id=="DQ-04")&(out.severity=="WARNING")).any()
def test_dq06_zero_sales():
    frames={
      "companies":pd.DataFrame({"id":["TCS"]}),
      "profitandloss":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"sales":[0],"operating_profit":[0],"opm_percentage":[0],"tax_percentage":[20],"dividend_payout":[10],"eps":[1],"net_profit":[10]}),
      "balancesheet":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"total_assets":[100],"total_liabilities":[100],"fixed_assets":[10]}),
      "cashflow":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"],"net_cash_flow":[0],"operating_activity":[0],"investing_activity":[0],"financing_activity":[0]}),
      "analysis":pd.DataFrame({"company_id":["TCS"]}),"documents":pd.DataFrame({"company_id":["TCS"]}),
      "prosandcons":pd.DataFrame({"company_id":["TCS"]}),"sectors":pd.DataFrame({"company_id":["TCS"],"sub_sector":["IT"]}),
      "stock_prices":pd.DataFrame({"company_id":["TCS"]}),"market_cap":pd.DataFrame({"company_id":["TCS"]}),
      "financial_ratios":pd.DataFrame({"company_id":["TCS"],"year":["2024-03"]}),"peer_groups":pd.DataFrame({"company_id":["TCS"]})
    }
    out=validate(frames)
    assert ((out.rule_id=="DQ-06")&(out.severity=="WARNING")).any()
