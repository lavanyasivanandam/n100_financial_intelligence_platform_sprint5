from __future__ import annotations
from pathlib import Path
import sqlite3, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
DB=ROOT/"db/nifty100.db"
OUT=ROOT/"output"

def compute_valuation(db_path=DB):
    con=sqlite3.connect(db_path)
    ratios=pd.read_sql_query("SELECT * FROM financial_ratios",con)
    pl=pd.read_sql_query("SELECT company_id,year,net_profit FROM profitandloss",con)
    sectors=pd.read_sql_query("SELECT company_id,broad_sector,sub_sector FROM sectors",con)
    mc=pd.read_sql_query("SELECT * FROM market_cap",con)
    companies=pd.read_sql_query("SELECT id company_id,company_name FROM companies",con)
    con.close()
    ratios['yn']=ratios.year.str[:4].astype(int)
    latest_r=ratios.sort_values(['company_id','yn']).groupby('company_id').tail(1)
    mc=mc.sort_values(['company_id','year'])
    latest_mc=mc.groupby('company_id').tail(1).copy()
    rows=[]
    for _,r in latest_r.iterrows():
        cid=r.company_id
        m=latest_mc[latest_mc.company_id==cid]
        if m.empty: continue
        m=m.iloc[0]
        pe_hist=mc[mc.company_id==cid].tail(5).pe_ratio.dropna()
        sector=sectors.loc[sectors.company_id==cid,'broad_sector']
        sector_name=sector.iloc[0] if not sector.empty else None
        sector_latest=latest_mc.merge(sectors[['company_id','broad_sector']],on='company_id',how='left')
        sector_pes=sector_latest.loc[sector_latest.broad_sector==sector_name,'pe_ratio'].dropna()
        sector_median=float(sector_pes.median()) if not sector_pes.empty else np.nan
        pe=float(m.pe_ratio) if pd.notna(m.pe_ratio) else np.nan
        if pd.notna(pe) and pd.notna(sector_median):
            flag='Caution' if pe>sector_median*1.15 else 'Discount' if pe<sector_median*0.70 else 'Fair'
        else: flag='Insufficient Data'
        fcf=float(r.free_cash_flow_cr) if pd.notna(r.free_cash_flow_cr) else np.nan
        mcap=float(m.market_cap_crore) if pd.notna(m.market_cap_crore) else np.nan
        fcf_yield=(fcf/mcap*100) if pd.notna(fcf) and pd.notna(mcap) and mcap!=0 else np.nan
        rows.append({
          'company_id':cid,'company_name':companies.loc[companies.company_id==cid,'company_name'].iloc[0] if any(companies.company_id==cid) else cid,
          'year':int(m.year),'market_cap_crore':m.market_cap_crore,'enterprise_value_crore':m.enterprise_value_crore,
          'fcf_cr':fcf,'fcf_yield_pct':fcf_yield,'pe_ratio':m.pe_ratio,'pb_ratio':m.pb_ratio,'ev_ebitda':m.ev_ebitda,
          'dividend_yield_pct':m.dividend_yield_pct,'pe_5yr_median':float(pe_hist.median()) if not pe_hist.empty else np.nan,
          'sector_median_pe':sector_median,'broad_sector':sector_name,'valuation_flag':flag
        })
    return pd.DataFrame(rows)

def export_valuation(df):
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT/'valuation_flags.csv',index=False)
    df.to_excel(OUT/'valuation_summary.xlsx',index=False)
    return OUT/'valuation_summary.xlsx'

if __name__=='__main__':
    d=compute_valuation(); export_valuation(d); print(f'valuation_rows={len(d)}')
