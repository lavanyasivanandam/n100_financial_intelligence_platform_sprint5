import pandas as pd
from src.dashboard.utils import pct_change_index
from src.dashboard.db import latest_company_frame

def test_pct_change_handles_duplicate_metric_labels():
    df=pd.DataFrame([[2022,100,100],[2023,120,120]],columns=["year","metric","metric"])
    out=pct_change_index(df,["metric"])
    assert abs(float(out["metric"].iloc[-1]) - 20) < 1e-9

def test_latest_frame_contains_revenue_for_sector_chart():
    d=latest_company_frame()
    assert "sales_cr" in d.columns
    assert d["sales_cr"].notna().any()
