from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"

def _read(sql, params=()):
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(sql, con, params=params)

def get_companies(query=None):
    sql="SELECT id AS ticker, company_name, about_company, website, nse_profile, bse_profile, face_value, book_value, roce_percentage, roe_percentage FROM companies"
    if query:
        sql += " WHERE id LIKE ? OR company_name LIKE ?"
        return _read(sql+" ORDER BY company_name", (f"%{query}%",f"%{query}%"))
    return _read(sql+" ORDER BY company_name")

def get_ratios(ticker, year=None):
    sql="SELECT * FROM financial_ratios WHERE company_id=?"
    params=[ticker]
    if year: sql += " AND year=?"; params.append(year)
    return _read(sql+" ORDER BY year",params)

def get_pl(ticker, year=None):
    sql="SELECT * FROM profitandloss WHERE company_id=?"; params=[ticker]
    if year: sql += " AND year=?"; params.append(year)
    return _read(sql+" ORDER BY year",params)

def get_bs(ticker, year=None):
    sql="SELECT * FROM balancesheet WHERE company_id=?"; params=[ticker]
    if year: sql += " AND year=?"; params.append(year)
    return _read(sql+" ORDER BY year",params)

def get_cf(ticker, year=None):
    sql="SELECT * FROM cashflow WHERE company_id=?"; params=[ticker]
    if year: sql += " AND year=?"; params.append(year)
    return _read(sql+" ORDER BY year",params)

def get_sectors(ticker=None):
    if ticker: return _read("SELECT * FROM sectors WHERE company_id=?",(ticker,))
    return _read("SELECT * FROM sectors ORDER BY broad_sector,company_id")

def get_peers(group_name=None):
    if group_name: return _read("SELECT * FROM peer_groups WHERE peer_group_name=? ORDER BY is_benchmark DESC,company_id",(group_name,))
    return _read("SELECT * FROM peer_groups ORDER BY peer_group_name,is_benchmark DESC,company_id")

def get_peer_percentiles(group_name, ticker=None):
    sql="SELECT * FROM peer_percentiles WHERE peer_group_name=?"; params=[group_name]
    if ticker: sql += " AND company_id=?"; params.append(ticker)
    return _read(sql+" ORDER BY company_id,metric",params)

def get_stock_prices(ticker):
    return _read("SELECT date,close_price,adjusted_close FROM stock_prices WHERE company_id=? ORDER BY date",(ticker,))

def get_market_cap(ticker=None):
    if ticker: return _read("SELECT * FROM market_cap WHERE company_id=? ORDER BY year",(ticker,))
    return _read("SELECT * FROM market_cap ORDER BY company_id,year")

def get_documents(ticker):
    return _read("SELECT year,Annual_Report FROM documents WHERE company_id=? ORDER BY year DESC",(ticker,))

def get_pros_cons(ticker):
    return _read("SELECT pros,cons FROM prosandcons WHERE company_id=?",(ticker,))

def get_capital_allocation():
    p=ROOT/"output"/"capital_allocation.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def latest_company_frame():
    ratios=_read("""SELECT * FROM financial_ratios WHERE id IN (SELECT MAX(id) FROM financial_ratios GROUP BY company_id)""")
    companies=get_companies().rename(columns={"ticker":"company_id"})
    sectors=get_sectors()[["company_id","sub_sector","market_cap_category"]]
    mc=_read("""SELECT * FROM market_cap WHERE id IN (SELECT MAX(id) FROM market_cap GROUP BY company_id)""")
    pl=_read("""SELECT company_id, year, sales AS sales_cr FROM profitandloss
                 WHERE id IN (SELECT MAX(id) FROM profitandloss GROUP BY company_id, year)""")
    # Source spreadsheets can store years as text while market-cap stores them
    # as integers. Normalize before joining so the dashboard never crashes.
    for frame in (ratios, mc, pl):
        frame["year"] = pd.to_numeric(frame["year"].astype(str).str[:4], errors="coerce").astype("Int64")
    return (ratios.merge(companies,on="company_id",how="left")
                  .merge(sectors,on="company_id",how="left")
                  .merge(mc,on=["company_id","year"],how="left",suffixes=("","_mc"))
                  .merge(pl,on=["company_id","year"],how="left"))

def get_valuation():
    from src.analytics.valuation import compute_valuation
    return compute_valuation()
