
from pathlib import Path
import pandas as pd
def test_load_audit_exists():
    p=Path("output/load_audit.csv")
    assert p.exists()
def test_load_audit_columns():
    df=pd.read_csv("output/load_audit.csv")
    assert set(["table","rows_in","rows_out","rejected","timestamp","runtime_s"]).issubset(df.columns)
def test_load_audit_tables():
    df=pd.read_csv("output/load_audit.csv")
    assert len(df)==12
def test_all_tables_have_rows():
    df=pd.read_csv("output/load_audit.csv")
    assert (df.rows_out>0).all()
def test_no_rows_out_exceed_rows_in():
    df=pd.read_csv("output/load_audit.csv")
    assert (df.rows_out<=df.rows_in).all()
