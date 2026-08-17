
from pathlib import Path
import pandas as pd
from .config import RAW,SUPPORTING
from .normalizer import normalize_ticker,normalize_year

CORE = {
 "companies.xlsx":"companies","profitandloss.xlsx":"profitandloss",
 "balancesheet.xlsx":"balancesheet","cashflow.xlsx":"cashflow",
 "analysis.xlsx":"analysis","documents.xlsx":"documents","prosandcons.xlsx":"prosandcons"
}
SUPPORT = {
 "sectors.xlsx":"sectors","stock_prices.xlsx":"stock_prices",
 "market_cap.xlsx":"market_cap","financial_ratios.xlsx":"financial_ratios",
 "peer_groups.xlsx":"peer_groups"
}

def read_core(path):
    # Supplied core files have a title/metadata row followed by the real header row.
    return pd.read_excel(path,header=1)

def read_support(path):
    return pd.read_excel(path)

def load_raw_frames():
    frames={}
    for fn,name in CORE.items():
        frames[name]=read_core(RAW/fn)
    for fn,name in SUPPORT.items():
        frames[name]=read_support(SUPPORTING/fn)
    return frames

def normalize_frames(frames):
    out={k:v.copy() for k,v in frames.items()}
    for name,df in out.items():
        if "company_id" in df.columns:
            df["company_id_raw"]=df["company_id"]
            df["company_id"]=df["company_id"].map(normalize_ticker)
        if name in {"profitandloss","balancesheet","cashflow","financial_ratios"}:
            if "year" in df.columns:
                df["year_raw"]=df["year"]
                df["year"]=df["year"].map(normalize_year)
        if name=="documents":
            df["year_raw"]=df["Year"]
            df["year"]=df["Year"].map(normalize_year)
    return out

def deduplicate_annual(df):
    if not {"company_id","year"}.issubset(df.columns):
        return df.copy(), pd.DataFrame(columns=df.columns)
    mask=df.duplicated(["company_id","year"],keep="last")
    rejected=df.loc[mask].copy()
    clean=df.loc[~mask].copy()
    return clean,rejected
