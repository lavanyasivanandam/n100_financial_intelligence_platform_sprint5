
from pathlib import Path
import sqlite3,pandas as pd,numpy as np,json
from .profitability import net_profit_margin,operating_profit_margin,return_on_equity,roce,return_on_assets
from .leverage import debt_to_equity,interest_coverage,interest_coverage_label,net_debt,asset_turnover
from .cagr import cagr,INSUFFICIENT
from .cashflow import free_cash_flow,capex,cfo_quality_score,capital_intensity,fcf_conversion_rate
from .capital_allocation import capital_allocation_pattern

ROOT=Path(__file__).resolve().parents[2]; DB_PATH=ROOT/"db/nifty100.db"; OUTPUT=ROOT/"output"
def num(x): return None if pd.isna(x) else float(x)

def build_ratio_frame(con):
    keys=pd.read_sql_query("""
      SELECT company_id,year FROM profitandloss
      UNION SELECT company_id,year FROM balancesheet
      UNION SELECT company_id,year FROM cashflow
    """,con)
    pl=pd.read_sql_query("SELECT * FROM profitandloss",con)
    bs=pd.read_sql_query("SELECT * FROM balancesheet",con)
    cf=pd.read_sql_query("SELECT * FROM cashflow",con)
    co=pd.read_sql_query("SELECT id company_id,face_value FROM companies",con)
    sec=pd.read_sql_query("SELECT company_id,broad_sector,sub_sector FROM sectors",con)
    df=keys.merge(pl,on=["company_id","year"],how="left").merge(bs,on=["company_id","year"],how="left").merge(cf,on=["company_id","year"],how="left").merge(co,on="company_id",how="left").merge(sec,on="company_id",how="left")
    df["year_num"]=df.year.str[:4].astype(int); df=df.sort_values(["company_id","year"]).reset_index(drop=True)
    hist=df[["company_id","year","year_num","sales","net_profit","eps"]].copy()
    ebit=df["profit_before_tax"].fillna(df["operating_profit"])+df["interest"].fillna(0)
    denom=df["equity_capital"].fillna(0)+df["reserves"].fillna(0)+df["borrowings"].fillna(0)
    sector_roce=(ebit/denom.replace(0,np.nan)*100)
    sector_benchmark=df.assign(_roce=sector_roce).groupby("broad_sector")["_roce"].transform("median")
    edges=[]; rows=[]
    company_roce=pd.read_sql_query(
        "SELECT id company_id,roce_percentage FROM companies WHERE roce_percentage IS NOT NULL",
        con
    ).set_index("company_id")["roce_percentage"].to_dict()
    for i,r in df.iterrows():
        sales=num(r.get("sales")); op=num(r.get("operating_profit")); np_=num(r.get("net_profit"))
        eq=num(r.get("equity_capital")); res=num(r.get("reserves")); debt=num(r.get("borrowings"))
        assets=num(r.get("total_assets")); interest=num(r.get("interest")); other=num(r.get("other_income"))
        cfo=num(r.get("operating_activity")); cfi=num(r.get("investing_activity")); cff=num(r.get("financing_activity"))
        inv=num(r.get("investments")); eps=num(r.get("eps")); face=num(r.get("face_value")); divp=num(r.get("dividend_payout"))
        opm=operating_profit_margin(op,sales); src_opm=num(r.get("opm_percentage"))
        if opm is not None and src_opm is not None and abs(opm-src_opm)>1:
            edges.append(f"OPM | {r.company_id} | {r.year} | source={src_opm} computed={opm:.4f} | SOURCE_MISMATCH")
        roe=return_on_equity(np_,eq,res); roce_v=roce(num(ebit[i]),eq,res,debt); roa=return_on_assets(np_,assets)
        de=debt_to_equity(debt,eq,res); icr=interest_coverage(op,other,interest); nd=net_debt(debt,inv)
        fcf=free_cash_flow(cfo,cfi); capex_v=capex(cfi); at=asset_turnover(sales,assets); fcfcr=fcf_conversion_rate(fcf,op)
        bvps=None
        if eq is not None and eq>0 and face is not None and face>0: bvps=(eq+(res or 0))/(eq/face)
        row={"company_id":r.company_id,"year":r.year,
          "net_profit_margin_pct":net_profit_margin(np_,sales),"operating_profit_margin_pct":opm,
          "return_on_equity_pct":roe,"return_on_capital_employed_pct":roce_v,"return_on_assets_pct":roa,
          "debt_to_equity":de,"interest_coverage":icr,"interest_coverage_label":interest_coverage_label(icr,interest),
          "net_debt_cr":nd,"asset_turnover":at,"free_cash_flow_cr":fcf,"capex_cr":capex_v,
          "earnings_per_share":eps,"book_value_per_share":bvps,"dividend_payout_ratio_pct":divp,
          "total_debt_cr":debt,"cash_from_operations_cr":cfo,"fcf_conversion_rate_pct":fcfcr,
          "broad_sector":r.get("broad_sector"),
          "roce_sector_benchmark_pct":num(sector_benchmark[i]),
          "de_warning_suppressed": bool(str(r.get("broad_sector"))=="Financials")}
        for metric,prefix in [("sales","revenue_cagr"),("net_profit","pat_cagr"),("eps","eps_cagr")]:
            for n in (3,5,10):
                target=int(r.year_num)-n
                old=hist[(hist.company_id==r.company_id)&(hist.year_num==target)]
                if old.empty: val,flag=None,INSUFFICIENT
                else: val,flag=cagr(num(old.iloc[0][metric]),num(r.get(metric)),n)
                row[f"{prefix}_{n}yr"]=val; row[f"{prefix}_{n}yr_flag"]=flag
                if flag!="NORMAL": edges.append(f"CAGR | {r.company_id} | {r.year} | {prefix}_{n}yr | {flag}")
        rows.append(row)
    out=pd.DataFrame(rows)
    common_latest=out.dropna(subset=["return_on_capital_employed_pct"]).sort_values("year").groupby("company_id").tail(1)
    for _,rr in common_latest.iterrows():
        source=company_roce.get(rr.company_id)
        computed=rr.return_on_capital_employed_pct
        if source is not None and computed is not None and abs(float(source)-float(computed))>5:
            edges.append(f"ROCE | {rr.company_id} | {rr.year} | source={source} computed={computed:.4f} | ROCE_SOURCE_MISMATCH")
    # 5-year rolling CFO/PAT quality
    quality={}
    raw=df[["company_id","year_num","operating_activity","net_profit"]]
    for company,h in raw.groupby("company_id"):
        h=h.sort_values("year_num")
        for y in h.year_num:
            hist5=h[h.year_num<=y].tail(5)
            score,label=cfo_quality_score(list(hist5[["operating_activity","net_profit"]].itertuples(index=False,name=None)))
            quality[(company,y)]=(score,label)
    out["cfo_quality_score"]=[quality.get((r.company_id,int(r.year[:4])),(None,"Not Available"))[0] for _,r in out.iterrows()]
    out["cfo_quality_label"]=[quality.get((r.company_id,int(r.year[:4])),(None,"Not Available"))[1] for _,r in out.iterrows()]
    ci=[capital_intensity(num(r.investing_activity),num(r.sales)) for _,r in df.iterrows()]
    out["capital_intensity_pct"]=[x[0] for x in ci]; out["capital_intensity_label"]=[x[1] for x in ci]
    out["roce_vs_sector_benchmark_pct"]=out["return_on_capital_employed_pct"]-out["roce_sector_benchmark_pct"]
    def composite(r):
        vals=[]
        for v,lo,hi in [(r.return_on_equity_pct,-20,30),(r.operating_profit_margin_pct,-10,40),(r.return_on_assets_pct,-10,20),(r.interest_coverage,0,10),(r.asset_turnover,0,5),(r.fcf_conversion_rate_pct,-100,150)]:
            if pd.notna(v): vals.append(max(0,min(100,(float(v)-lo)/(hi-lo)*100)))
        if pd.notna(r.debt_to_equity): vals.append(max(0,min(100,(1-float(r.debt_to_equity)/2)*100)))
        return round(sum(vals)/len(vals),2) if vals else None
    out["composite_quality_score"]=out.apply(composite,axis=1)
    return out,edges

def write_table(con,df):
    con.execute("DROP TABLE IF EXISTS financial_ratios")
    con.execute("""CREATE TABLE financial_ratios(
      id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT NOT NULL, year TEXT NOT NULL,
      net_profit_margin_pct REAL, operating_profit_margin_pct REAL, return_on_equity_pct REAL,
      return_on_capital_employed_pct REAL, return_on_assets_pct REAL, debt_to_equity REAL,
      interest_coverage REAL, interest_coverage_label TEXT, net_debt_cr REAL, asset_turnover REAL,
      free_cash_flow_cr REAL, capex_cr REAL, earnings_per_share REAL, book_value_per_share REAL,
      dividend_payout_ratio_pct REAL, total_debt_cr REAL, cash_from_operations_cr REAL,
      fcf_conversion_rate_pct REAL, cfo_quality_score REAL, cfo_quality_label TEXT,
      capital_intensity_pct REAL, capital_intensity_label TEXT,
      revenue_cagr_3yr REAL,revenue_cagr_3yr_flag TEXT,revenue_cagr_5yr REAL,revenue_cagr_5yr_flag TEXT,
      revenue_cagr_10yr REAL,revenue_cagr_10yr_flag TEXT,pat_cagr_3yr REAL,pat_cagr_3yr_flag TEXT,
      pat_cagr_5yr REAL,pat_cagr_5yr_flag TEXT,pat_cagr_10yr REAL,pat_cagr_10yr_flag TEXT,
      eps_cagr_3yr REAL,eps_cagr_3yr_flag TEXT,eps_cagr_5yr REAL,eps_cagr_5yr_flag TEXT,
      eps_cagr_10yr REAL,eps_cagr_10yr_flag TEXT,broad_sector TEXT,roce_sector_benchmark_pct REAL,
      roce_vs_sector_benchmark_pct REAL,de_warning_suppressed INTEGER,composite_quality_score REAL,UNIQUE(company_id,year),
      FOREIGN KEY(company_id) REFERENCES companies(id))""")
    df=df.where(pd.notna(df),None)
    df.to_sql("financial_ratios",con,if_exists="append",index=False); con.commit()

def build():
    con=sqlite3.connect(DB_PATH); con.execute("PRAGMA foreign_keys=ON")
    df,edges=build_ratio_frame(con); write_table(con,df)
    alloc=pd.read_sql_query("SELECT company_id,year,operating_activity cfo,investing_activity cfi,financing_activity cff FROM cashflow ORDER BY company_id,year",con)
    pa=alloc.apply(lambda r: capital_allocation_pattern(r.cfo,r.cfi,r.cff),axis=1)
    alloc["cfo_sign"]=alloc.cfo.map(lambda x:"+" if x>0 else "-" if x<0 else "0")
    alloc["cfi_sign"]=alloc.cfi.map(lambda x:"+" if x>0 else "-" if x<0 else "0")
    alloc["cff_sign"]=alloc.cff.map(lambda x:"+" if x>0 else "-" if x<0 else "0")
    alloc["pattern_code"]=[x[0] for x in pa]; alloc["pattern_label"]=[x[1] for x in pa]
    alloc.to_csv(OUTPUT/"capital_allocation.csv",index=False)
    # Screener preview uses the latest year where the P&L and balance sheet
    # both exist, because ROE and D/E require both statements.
    common=pd.read_sql_query("""
      SELECT p.company_id,p.year
      FROM profitandloss p JOIN balancesheet b USING(company_id,year)
    """,con)
    latest_common=common.sort_values(["company_id","year"]).groupby("company_id").tail(1)
    preview=df.merge(latest_common,on=["company_id","year"],how="inner")
    preview=preview[(preview.return_on_equity_pct>15)&(preview.debt_to_equity<1)]
    preview[["company_id","year","return_on_equity_pct","debt_to_equity"]].to_csv(OUTPUT/"screener_preview.csv",index=False)
    checks=[]
    for ticker in ["ABB","TCS","RELIANCE"]:
        rr=df.merge(latest_common,on=["company_id","year"],how="inner")
        rr=rr[rr.company_id==ticker].sort_values("year").tail(1).iloc[0]
        src=pd.read_sql_query("""SELECT p.net_profit,b.equity_capital,b.reserves FROM profitandloss p JOIN balancesheet b USING(company_id,year) WHERE p.company_id=? ORDER BY p.year DESC LIMIT 1""",con,params=(ticker,)).iloc[0]
        manual=src.net_profit/(src.equity_capital+src.reserves)*100
        checks.append([ticker,rr.year,manual,rr.return_on_equity_pct,abs(manual-rr.return_on_equity_pct)])
    pd.DataFrame(checks,columns=["company_id","year","manual_roe_pct","engine_roe_pct","absolute_difference_pct"]).to_csv(OUTPUT/"roe_spot_checks.csv",index=False)
    (OUTPUT/"ratio_edge_cases.log").write_text("\n".join(edges) if edges else "No documented edge cases.\n")
    summary={"ratio_rows":len(df),"companies":df.company_id.nunique(),"ratio_columns":len(df.columns),"capital_allocation_rows":len(alloc),"screener_preview_count":len(preview),"edge_log_entries":len(edges)}
    (OUTPUT/"sprint2_engine_summary.json").write_text(json.dumps(summary,indent=2))
    con.close(); return summary
if __name__=="__main__": print(build())
