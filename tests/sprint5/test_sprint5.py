import json, sqlite3
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).parents[2]
def test_92_companies():
    c=sqlite3.connect(ROOT/"db/nifty100.db"); assert c.execute("select count(*) from companies").fetchone()[0]==92; c.close()
def test_pros_cons_coverage():
    d=pd.read_csv(ROOT/"output/pros_cons_generated.csv"); assert d.company_id.nunique()==92; assert set(d.type)=={"pro","con"}; assert d.groupby(["company_id","type"]).size().min()>=1; assert (d.confidence_score>60).all()
def test_cashflow_output():
    d=pd.read_excel(ROOT/"output/cashflow_intelligence.xlsx"); assert len(d)==92; required={"company_id","sector","cfo_quality_score","cfo_quality_label","capex_intensity_pct","capex_label","pat_cagr_5yr","fcf_conversion_pct","distress_flag","deleveraging_flag","capital_allocation_label"}; assert required.issubset(d.columns)
def test_distress_file():
    assert (ROOT/"output/distress_alerts.csv").exists()
def test_analysis_parser_outputs():
    d=pd.read_csv(ROOT/"output/analysis_parsed.csv"); assert {"company_id","metric_type","period_years","value_pct"}.issubset(d.columns); assert len(d)>0
def test_reports():
    tears=list((ROOT/"reports/tearsheets").glob("*_tearsheet.pdf")); assert len(tears)==92
    assert min(p.stat().st_size for p in tears)>=30000
    import pypdf
    assert all(len(pypdf.PdfReader(str(p)).pages)==2 for p in tears[:10])
    assert len(list((ROOT/"reports/sector").glob("*_report.pdf")))==11
    assert len(pypdf.PdfReader(str(ROOT/"reports/portfolio/portfolio_summary.pdf")).pages)==92
def test_summary():
    s=json.loads((ROOT/"output/sprint5_summary.json").read_text()); assert s["companies"]==92; assert s["tearsheets_generated"]==92
