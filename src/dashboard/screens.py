from __future__ import annotations
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests

from .db import *
from .utils import latest_by_company, pct_change_index, safe_label
from src.analytics.valuation import compute_valuation, export_valuation

ROOT=Path(__file__).resolve().parents[2]

@st.cache_data(ttl=300)
def cached_companies(): return get_companies()
@st.cache_data(ttl=300)
def cached_latest(): return latest_company_frame()
@st.cache_data(ttl=300)
def cached_valuation():
    d=compute_valuation(); export_valuation(d); return d
@st.cache_data(ttl=300)
def cached_capital(): return get_capital_allocation()


def home():
    st.title('Nifty 100 Financial Intelligence Platform')
    st.caption('Sprint 4 — Dashboard & Valuation Module')
    d=cached_latest()
    st.subheader('Market Snapshot')
    k1,k2,k3,k4,k5,k6=st.columns(6)
    k1.metric('Average ROE',safe_label(d.return_on_equity_pct.mean(),'{:.1f}%'))
    k2.metric('Median P/E',safe_label(d.pe_ratio.median(),'{:.1f}'))
    k3.metric('Median D/E',safe_label(d.debt_to_equity.median(),'{:.2f}'))
    k4.metric('Companies',str(d.company_id.nunique()))
    k5.metric('Median Revenue CAGR 5Y',safe_label(d.revenue_cagr_5yr.median(),'{:.1f}%'))
    k6.metric('Debt-Free Companies',str((d.interest_coverage_label=='Debt Free').sum()))
    st.subheader('Top 5 by Composite Quality Score')
    top=d.nlargest(5,'composite_quality_score')[['company_id','company_name','broad_sector','composite_quality_score','return_on_equity_pct','debt_to_equity','revenue_cagr_5yr']]
    st.dataframe(top,use_container_width=True,hide_index=True)


def _company_picker():
    companies=cached_companies()
    q=st.text_input('Search company name or ticker','',placeholder='e.g. HDFC or HDFCBANK')
    opts=companies if not q else companies[companies.ticker.str.contains(q,case=False,na=False)|companies.company_name.str.contains(q,case=False,na=False)]
    if opts.empty:
        st.warning('Ticker not found — please try another search.')
        return None
    labels=(opts.ticker+' — '+opts.company_name).tolist()
    choice=st.selectbox('Company',labels)
    return choice.split(' — ',1)[0]

def profile():
    st.title('Company Profile')
    ticker=_company_picker()
    if not ticker:return
    company=cached_companies().query('ticker==@ticker').iloc[0]
    ratios=get_ratios(ticker); pl=get_pl(ticker); bs=get_bs(ticker); cf=get_cf(ticker); peers=get_peers(); pc=get_pros_cons(ticker)
    sector=get_sectors(ticker).iloc[0]
    latest=latest_by_company(ratios).iloc[-1]
    st.subheader(company.company_name)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Sector',sector.broad_sector); c2.metric('Sub-sector',sector.sub_sector)
    c3.metric('ROE',safe_label(latest.return_on_equity_pct,'{:.1f}%')); c4.metric('ROCE',safe_label(latest.return_on_capital_employed_pct,'{:.1f}%'))
    st.write(company.about_company)
    st.markdown(f'**Website:** {company.website or "—"}')
    metrics={'ROE %':latest.return_on_equity_pct,'ROCE %':latest.return_on_capital_employed_pct,'NPM %':latest.net_profit_margin_pct,'D/E':latest.debt_to_equity,'ICR':latest.interest_coverage,'FCF Cr':latest.free_cash_flow_cr,'Revenue CAGR 5Y %':latest.revenue_cagr_5yr,'EPS CAGR 5Y %':latest.eps_cagr_5yr}
    st.dataframe(pd.DataFrame([metrics]),use_container_width=True,hide_index=True)
    st.subheader('10-Year Revenue & Net Profit')
    chart=pl[['year','sales','net_profit']].copy().sort_values('year').tail(10).melt('year',var_name='Metric',value_name='Value')
    fig=px.line(chart,x='year',y='Value',color='Metric',markers=True); st.plotly_chart(fig,use_container_width=True)
    st.subheader('10-Year ROE & ROCE')
    rr=ratios[['year','return_on_equity_pct','return_on_capital_employed_pct']].sort_values('year').tail(10).melt('year',var_name='Metric',value_name='Value')
    st.plotly_chart(px.line(rr,x='year',y='Value',color='Metric',markers=True),use_container_width=True)
    if not pc.empty:
        st.subheader('Pros & Cons')
        for _,r in pc.iterrows():
            st.markdown(f'**Pro:** {r.pros or "—"}  \n**Con:** {r.cons or "—"}')


def screener():
    from src.screener.engine import latest_financials, add_composite, apply_filters, load_config
    st.title('Screener')
    cfg=load_config(); con=sqlite3.connect(ROOT/'db/nifty100.db'); d=add_composite(latest_financials(con)); con.close()
    st.sidebar.subheader('Screener Filters')
    defaults={'roe_min':0,'de_max':5,'fcf_min':0,'revenue_cagr_5yr_min':-20,'pat_cagr_5yr_min':-20,'opm_min':-20,'pe_max':100,'pb_max':50,'dividend_yield_min':0,'icr_min':0}
    vals={}
    vals['roe_min']=st.sidebar.slider('ROE min %',-20.0,50.0,float(defaults['roe_min']))
    vals['de_max']=st.sidebar.slider('D/E max',0.0,10.0,float(defaults['de_max']))
    vals['fcf_min']=st.sidebar.slider('FCF min Cr',-50000.0,50000.0,float(defaults['fcf_min']))
    vals['revenue_cagr_5yr_min']=st.sidebar.slider('Revenue CAGR 5Y min %',-50.0,50.0,float(defaults['revenue_cagr_5yr_min']))
    vals['pat_cagr_5yr_min']=st.sidebar.slider('PAT CAGR 5Y min %',-50.0,100.0,float(defaults['pat_cagr_5yr_min']))
    vals['opm_min']=st.sidebar.slider('OPM min %',-50.0,60.0,float(defaults['opm_min']))
    vals['pe_max']=st.sidebar.slider('P/E max',0.0,150.0,float(defaults['pe_max']))
    vals['pb_max']=st.sidebar.slider('P/B max',0.0,50.0,float(defaults['pb_max']))
    vals['dividend_yield_min']=st.sidebar.slider('Dividend Yield min %',0.0,15.0,float(defaults['dividend_yield_min']))
    vals['icr_min']=st.sidebar.slider('ICR min',0.0,30.0,float(defaults['icr_min']))
    st.sidebar.markdown('**Presets**')
    preset=st.sidebar.radio('Choose preset',['Custom']+list(cfg['presets'].keys()),index=0)
    if preset!='Custom': vals=dict(cfg['presets'][preset])
    result=apply_filters(d,vals)
    st.metric('Result count',len(result))
    cols=['company_id','company_name','broad_sector','composite_quality_score','return_on_equity_pct','debt_to_equity','free_cash_flow_cr','revenue_cagr_5yr','pat_cagr_5yr','operating_profit_margin_pct','pe_ratio','pb_ratio','dividend_yield_pct','interest_coverage']
    st.dataframe(result[[c for c in cols if c in result.columns]],use_container_width=True,hide_index=True)
    st.download_button('Download CSV',result.to_csv(index=False).encode('utf-8'),'screener_results.csv','text/csv')


def peers():
    st.title('Peer Comparison')
    groups=get_peers().peer_group_name.dropna().unique().tolist(); group=st.selectbox('Peer group',sorted(groups))
    pg=get_peers(group); tickers=pg.company_id.tolist(); names=cached_companies().set_index('ticker').company_name.to_dict()
    ticker=st.selectbox('Company',tickers,format_func=lambda x:f'{x} — {names.get(x,x)}')
    d=cached_latest(); g=d[d.company_id.isin(tickers)].copy(); row=d[d.company_id==ticker].iloc[0]
    metrics=[('ROE %','return_on_equity_pct',True),('ROCE %','return_on_capital_employed_pct',True),('NPM %','net_profit_margin_pct',True),('D/E','debt_to_equity',False),('FCF score','free_cash_flow_cr',True),('PAT CAGR 5Y','pat_cagr_5yr',True),('Revenue CAGR 5Y','revenue_cagr_5yr',True),('Composite Score','composite_quality_score',True)]
    labels=[m[0] for m in metrics]
    vals=[]; av=[]
    for _,c,h in metrics:
        s=pd.to_numeric(g[c],errors='coerce'); x=row[c]; vals.append(float(x) if pd.notna(x) else 0); av.append(float(s.mean()) if s.notna().any() else 0)
    vals += vals[:1]; av += av[:1]; theta=labels+[labels[0]]
    fig=go.Figure(); fig.add_trace(go.Scatterpolar(r=vals,theta=theta,fill='toself',name=ticker)); fig.add_trace(go.Scatterpolar(r=av,theta=theta,mode='lines',line=dict(dash='dash'),name='Peer average')); fig.update_layout(polar=dict(radialaxis=dict(visible=True)),showlegend=True)
    st.plotly_chart(fig,use_container_width=True)
    show=g[['company_id','company_name','composite_quality_score','return_on_equity_pct','return_on_capital_employed_pct','net_profit_margin_pct','debt_to_equity','free_cash_flow_cr','pat_cagr_5yr','revenue_cagr_5yr']].copy()
    bench=set(pg.loc[pg.is_benchmark==1,'company_id'])
    def style(r): return ['background-color: #F4B183' if r.company_id in bench else '' for _ in r]
    st.dataframe(show.style.apply(style,axis=1),use_container_width=True,hide_index=True)


def trends():
    st.title('Trend Analysis')
    ticker=_company_picker()
    if not ticker:return
    r=get_ratios(ticker).sort_values('year')
    available={'ROE':'return_on_equity_pct','ROCE':'return_on_capital_employed_pct','NPM':'net_profit_margin_pct','D/E':'debt_to_equity','FCF':'free_cash_flow_cr','Revenue CAGR 5Y':'revenue_cagr_5yr','PAT CAGR 5Y':'pat_cagr_5yr','EPS CAGR 5Y':'eps_cagr_5yr','Asset Turnover':'asset_turnover'}
    chosen=st.multiselect('Select up to 3 metrics',list(available),default=['ROE','Revenue CAGR 5Y'],max_selections=3)
    if not chosen:return
    x=pct_change_index(r,['year']+[available[c] for c in chosen])
    long=x.melt('year',var_name='Metric',value_name='% Change from first available year')
    long['Metric']=long.Metric.map({v:k for k,v in available.items()})
    st.plotly_chart(px.line(long,x='year',y='% Change from first available year',color='Metric',markers=True),use_container_width=True)


def sectors():
    st.title('Sector Analysis')
    d=cached_latest(); sectors=sorted(d.broad_sector.dropna().unique()); sec=st.selectbox('Sector',sectors)
    g=d[d.broad_sector==sec].copy()
    if 'sales_cr' not in g.columns or g['sales_cr'].notna().sum()==0:
        st.warning('Revenue data is not available for this sector.')
        return
    fig=px.scatter(g,x='sales_cr',y='return_on_equity_pct',size='market_cap_crore',hover_name='company_name',color='broad_sector',title=f'{sec}: Revenue vs ROE')
    st.plotly_chart(fig,use_container_width=True)
    st.subheader('Sector Median KPI')
    med=g[['return_on_equity_pct','return_on_capital_employed_pct','net_profit_margin_pct','debt_to_equity','free_cash_flow_cr','revenue_cagr_5yr','pat_cagr_5yr','composite_quality_score']].median().reset_index(); med.columns=['Metric','Median']
    st.plotly_chart(px.bar(med,x='Metric',y='Median'),use_container_width=True)


def capital_allocation():
    st.title('Capital Allocation Patterns')
    d=cached_capital()
    if d.empty: st.info('Capital allocation output not available.'); return
    counts=d.groupby(['pattern_code','pattern_label']).company_id.nunique().reset_index(name='companies').sort_values('companies',ascending=False)
    st.dataframe(counts,use_container_width=True,hide_index=True)
    choice=st.selectbox('Select pattern',counts.pattern_label.tolist())
    g=d[d.pattern_label==choice].copy()
    st.write(f'{len(g.company_id.unique())} companies in {choice}')
    latest=d.sort_values('year').groupby('company_id').tail(1)[['company_id','pattern_label']]
    names=cached_companies().rename(columns={'ticker':'company_id'})[['company_id','company_name']]
    g=g.merge(names,on='company_id',how='left')
    st.dataframe(g[['company_id','company_name','year','cfo','cfi','cff','pattern_code','pattern_label']],use_container_width=True,hide_index=True)
    # Treemap uses company as leaf and count/absolute CFO as value.
    g2=g.groupby(['pattern_label','company_name'],as_index=False).size().rename(columns={'size':'years'})
    st.plotly_chart(px.treemap(g2,path=['pattern_label','company_name'],values='years',title='Capital Allocation Pattern Treemap'),use_container_width=True)


def reports():
    st.title('Reports & Valuation')
    tab_reports, tab_valuation = st.tabs(['Annual Reports','Valuation'])
    with tab_reports:
        ticker=_company_picker()
        if ticker:
            docs=get_documents(ticker)
            if docs.empty:
                st.error('No annual reports available.')
            else:
                st.write(f'{len(docs)} report records found')
                for _,r in docs.iterrows():
                    url=r.Annual_Report
                    if not url:
                        st.markdown(f'**{r.year}** — 🔴 Report unavailable')
                        continue
                    ok=False; status=''
                    try:
                        resp=requests.head(url,timeout=3,allow_redirects=True,headers={'User-Agent':'Mozilla/5.0'}); ok=resp.status_code<400; status=str(resp.status_code)
                    except Exception: status='unreachable'
                    if ok: st.markdown(f'**{r.year}** — [Open BSE Annual Report]({url})')
                    else: st.markdown(f'**{r.year}** — 🔴 Report unavailable ({status})')
    with tab_valuation:
        valuation()

def valuation():
    st.title('Valuation Module')
    d=cached_valuation()
    st.metric('Companies with valuation output',d.company_id.nunique())
    st.dataframe(d[['company_id','company_name','broad_sector','fcf_yield_pct','pe_ratio','pb_ratio','ev_ebitda','pe_5yr_median','sector_median_pe','valuation_flag']],use_container_width=True,hide_index=True)
    st.download_button('Download valuation CSV',d.to_csv(index=False).encode('utf-8'),'valuation_flags.csv','text/csv')
    st.download_button('Download valuation Excel',Path(ROOT/'output/valuation_summary.xlsx').read_bytes(),'valuation_summary.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
