
import sqlite3, time
from pathlib import Path
import pandas as pd
from src.etl.config import DB_PATH,OUTPUT
from src.etl.loader import load_raw_frames,normalize_frames,deduplicate_annual

TABLES=["companies","profitandloss","balancesheet","cashflow","analysis","documents",
        "prosandcons","sectors","stock_prices","market_cap","financial_ratios","peer_groups"]

def connect():
    con=sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys=ON")
    return con

def create_schema(con):
    sql=Path(__file__).with_name("schema.sql").read_text()
    con.executescript(sql)

def clean_for_db(frames):
    f=frames
    # Master
    f["companies"]=f["companies"].copy()
    f["companies"]["id"]=f["companies"]["id"].astype(str).str.strip().str.upper()
    master=set(f["companies"]["id"])
    rejects={}
    # Time-series: reject unparseable years and orphans; dedup keep last.
    for name in ["profitandloss","balancesheet","cashflow"]:
        df=f[name].copy()
        before=len(df)
        df=df[df["company_id"].isin(master)]
        df=df[df["year"].astype(str).str.fullmatch(r"\d{4}-\d{2}")]
        df,dup=deduplicate_annual(df)
        rejects[name]=before-len(df)
        f[name]=df.drop(columns=[c for c in ["company_id_raw","year_raw"] if c in df],errors="ignore")
    # Other tables: reject orphans. Documents keep numeric years normalized.
    for name in ["analysis","documents","prosandcons","sectors","stock_prices","market_cap","financial_ratios","peer_groups"]:
        df=f[name].copy()
        before=len(df)
        df=df[df["company_id"].isin(master)]
        if name=="financial_ratios":
            df=df[df["year"].astype(str).str.fullmatch(r"\d{4}-\d{2}")]
            df,_=deduplicate_annual(df)
        rejects[name]=before-len(df)
        f[name]=df.drop(columns=[c for c in ["company_id_raw","year_raw","Year_raw"] if c in df],errors="ignore")
    # Raw helper columns from companies.
    f["companies"]=f["companies"].drop(columns=["id_raw"],errors="ignore")
    return f,rejects

def write_df(con,name,df):
    df.to_sql(name,con,if_exists="append",index=False)

def build():
    t0=time.perf_counter()
    raw=load_raw_frames()
    source_frames=normalize_frames(raw)
    source_counts={k:len(v) for k,v in source_frames.items()}
    frames={k:v.copy() for k,v in source_frames.items()}
    clean,rejects=clean_for_db(frames)
    con=connect()
    # Rebuild deterministically: drop child tables before parent tables.
    for t in reversed(TABLES):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.commit()
    create_schema(con)
    audit=[]
    for t in TABLES:
        start=time.perf_counter()
        df=clean[t].copy()
        # Remove helper/raw columns and normalize DB column naming.
        allowed=[r[1] for r in con.execute(f"PRAGMA table_info({t})").fetchall()]
        df=df[[c for c in df.columns if c in allowed]]
        if t=="documents" and "year" in df.columns:
            pass
        write_df(con,t,df)
        con.commit()
        rows_in=source_counts[t]; rows_out=len(df)
        audit.append([t,rows_in,rows_out,rows_in-rows_out,rejects.get(t,0),
                      round(time.perf_counter()-start,4)])
    con.close()
    audit_df=pd.DataFrame(audit,columns=["table","rows_in","rows_out","rejected","rejected_by_cleaning","runtime_s"])
    audit_df["timestamp"]=pd.Timestamp.utcnow().isoformat()
    audit_df.to_csv(OUTPUT/"load_audit.csv",index=False)
    return audit_df

if __name__=="__main__":
    print(build().to_string(index=False))
