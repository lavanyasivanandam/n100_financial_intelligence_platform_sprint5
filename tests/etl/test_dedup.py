
import pandas as pd
from src.etl.loader import deduplicate_annual
def test_dedup_keeps_last():
    df=pd.DataFrame({"company_id":["TCS","TCS","INFY"],"year":["2024-03","2024-03","2024-03"],"v":[1,2,3]})
    clean,rejected=deduplicate_annual(df)
    assert len(clean)==2 and clean.loc[clean.company_id=="TCS","v"].iloc[0]==2
    assert len(rejected)==1
def test_dedup_no_duplicates():
    df=pd.DataFrame({"company_id":["TCS","INFY"],"year":["2024-03","2024-03"]})
    clean,rejected=deduplicate_annual(df)
    assert len(clean)==2 and rejected.empty
def test_dedup_empty():
    df=pd.DataFrame({"company_id":[],"year":[]})
    clean,rejected=deduplicate_annual(df)
    assert rejected.empty
def test_dedup_preserves_columns():
    df=pd.DataFrame({"company_id":["TCS","TCS"],"year":["2024-03","2024-03"],"x":[1,2]})
    clean,_=deduplicate_annual(df)
    assert list(clean.columns)==list(df.columns)
def test_dedup_multiple_companies():
    df=pd.DataFrame({"company_id":["TCS","TCS","INFY","INFY"],"year":["2024-03","2024-03","2024-03","2024-03"]})
    clean,rejected=deduplicate_annual(df)
    assert len(clean)==2 and len(rejected)==2
