
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
import re, os
from .normalizer import normalize_ticker

@dataclass
class Failure:
    rule_id:str; dataset:str; company_id:object; year:object; field:str; issue:str; severity:str; raw_value:object=""

RULES = {
"DQ-01":"Company PK Uniqueness","DQ-02":"Annual PK Uniqueness","DQ-03":"FK Integrity",
"DQ-04":"Balance Sheet Balance","DQ-05":"OPM Cross-Check","DQ-06":"Positive Sales",
"DQ-07":"Year Format","DQ-08":"Ticker Format","DQ-09":"Net Cash Check",
"DQ-10":"Non-Negative Fixed Assets","DQ-11":"Tax Rate Range","DQ-12":"Dividend Payout Cap",
"DQ-13":"URL Validity","DQ-14":"EPS Sign Consistency","DQ-15":"BSE/ASE Balance","DQ-16":"Coverage Check"
}

def _add(rows, rule,dataset, df, mask, field, issue, severity, raw_col=None):
    mask=pd.Series(mask,index=df.index).fillna(False).astype(bool)
    for i in df.index[mask]:
        r=df.loc[i]
        rows.append(Failure(rule,dataset,r.get("company_id"),r.get("year",r.get("Year")),
                            field,issue,severity,r.get(raw_col) if raw_col else ""))

def validate(frames, check_urls=False):
    rows=[]
    companies=frames["companies"]
    master=set(companies["id"].map(normalize_ticker).dropna())

    _add(rows,"DQ-01","companies",companies,
         companies["id"].map(normalize_ticker).duplicated(keep=False),
         "id","Duplicate company ticker","CRITICAL")

    for name in ["profitandloss","balancesheet","cashflow"]:
        df=frames[name]
        _add(rows,"DQ-02",name,df,df.duplicated(["company_id","year"],keep=False),
             "company_id,year","Duplicate annual company/year pair","CRITICAL")
        _add(rows,"DQ-03",name,df,~df["company_id"].isin(master),
             "company_id","Orphan company_id","CRITICAL")
        _add(rows,"DQ-07",name,df,~df["year"].astype(str).str.fullmatch(r"\d{4}-\d{2}"),
             "year","Unparseable year","CRITICAL", "year_raw")
        _add(rows,"DQ-08",name,df,
             ~df["company_id"].astype(str).str.fullmatch(r"[A-Z0-9&.-]{2,12}"),
             "company_id","Ticker outside 2–12 character format","CRITICAL")

    for name in ["analysis","documents","prosandcons","sectors","stock_prices","market_cap","financial_ratios","peer_groups"]:
        df=frames[name]
        _add(rows,"DQ-03",name,df,~df["company_id"].isin(master),"company_id","Orphan company_id","CRITICAL")
        _add(rows,"DQ-08",name,df,~df["company_id"].astype(str).str.fullmatch(r"[A-Z0-9&.-]{2,12}"),
             "company_id","Ticker outside 2–12 character format","CRITICAL")

    pl=frames["profitandloss"]; bs=frames["balancesheet"]; cf=frames["cashflow"]
    assets=pd.to_numeric(bs["total_assets"],errors="coerce")
    liabilities=pd.to_numeric(bs["total_liabilities"],errors="coerce")
    bal=(assets.abs()>0) & ((assets-liabilities).abs()/assets.abs()>=0.01)
    _add(rows,"DQ-04","balancesheet",bs,bal,"total_assets,total_liabilities",
         "Balance-sheet imbalance >= 1%","WARNING")

    sales=pd.to_numeric(pl["sales"],errors="coerce")
    op=pd.to_numeric(pl["operating_profit"],errors="coerce")
    src=pd.to_numeric(pl["opm_percentage"],errors="coerce")
    calc=op/sales.replace(0,np.nan)*100
    _add(rows,"DQ-05","profitandloss",(pl if True else pl),
         (src-calc).abs()>=1,"opm_percentage",
         "Source OPM differs from computed OPM by >= 1 percentage point","WARNING")

    sector_map=frames["sectors"].set_index("company_id")["sub_sector"].astype(str).to_dict()
    bank_mask=pl["company_id"].map(lambda x:"bank" in sector_map.get(x,"").lower())
    _add(rows,"DQ-06","profitandloss",pl,(sales<=0)&(~bank_mask),
         "sales","Non-bank sales <= 0","WARNING")

    net=pd.to_numeric(cf["net_cash_flow"],errors="coerce")
    components=(pd.to_numeric(cf["operating_activity"],errors="coerce").fillna(0)
                +pd.to_numeric(cf["investing_activity"],errors="coerce").fillna(0)
                +pd.to_numeric(cf["financing_activity"],errors="coerce").fillna(0))
    _add(rows,"DQ-09","cashflow",cf,(net-components).abs()>10,
         "net_cash_flow","Net cash differs from CFO+CFI+CFF by >10 Cr","WARNING")

    fixed=pd.to_numeric(bs["fixed_assets"],errors="coerce")
    _add(rows,"DQ-10","balancesheet",bs,fixed<0,"fixed_assets","Negative fixed assets","WARNING")

    tax=pd.to_numeric(pl["tax_percentage"],errors="coerce")
    _add(rows,"DQ-11","profitandloss",pl,(tax<0)|(tax>60),
         "tax_percentage","Tax rate outside 0–60%","WARNING")

    payout=pd.to_numeric(pl["dividend_payout"],errors="coerce")
    _add(rows,"DQ-12","profitandloss",pl,payout>200,
         "dividend_payout","Dividend payout >200%","WARNING")

    # URL validity is intentionally optional: network validation is not part of a deterministic local load.
    docs=frames["documents"]
    if check_urls:
        import requests
        statuses=[]
        for u in docs["Annual_Report"].fillna(""):
            try: statuses.append(requests.head(str(u),timeout=8,allow_redirects=True).status_code)
            except Exception: statuses.append(None)
        _add(rows,"DQ-13","documents",docs,[x!=200 for x in statuses],
             "Annual_Report","URL did not return HTTP 200","WARNING")

    eps=pd.to_numeric(pl["eps"],errors="coerce"); npv=pd.to_numeric(pl["net_profit"],errors="coerce")
    _add(rows,"DQ-14","profitandloss",pl,(npv>0)&(eps<=0),
         "eps","EPS sign inconsistent with positive net profit","WARNING")

    _add(rows,"DQ-15","balancesheet",bs,
         assets.notna() & liabilities.notna() & (assets!=liabilities),
         "total_assets,total_liabilities","Strict balance counter","INFO")

    for name in ["profitandloss","balancesheet","cashflow"]:
        df=frames[name]
        coverage=df[df["year"].astype(str).str.fullmatch(r"\d{4}-\d{2}")].groupby("company_id")["year"].nunique()
        bad=set(coverage[coverage<5].index)
        _add(rows,"DQ-16",name,df,df["company_id"].isin(bad),
             "company_id","Company has fewer than 5 annual records","WARNING")
    return pd.DataFrame([x.__dict__ for x in rows])
