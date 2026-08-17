from pathlib import Path
import sqlite3
from src.screener.engine import latest_financials,add_composite,load_config
from src.analytics.peer import compute_peer_percentiles
ROOT=Path(__file__).resolve().parents[2]
def data():
 c=sqlite3.connect(ROOT/'db/nifty100.db');d=add_composite(latest_financials(c));c.close();return d
def test_full_universe_92():assert len(data())==92
def test_composite_0_100():assert data().composite_quality_score.between(0,100).all()
def test_six_presets():assert len(load_config()['presets'])==6
def test_fifteen_filterable_metrics():assert len(load_config()['metrics'])==15
def test_peer_groups_11():
 c=sqlite3.connect(ROOT/'db/nifty100.db');n=c.execute('select count(distinct peer_group_name) from peer_groups').fetchone()[0];c.close();assert n==11
def test_peer_rank_10_metrics():assert compute_peer_percentiles(data()).metric.nunique()==10
def test_peer_rank_range():assert compute_peer_percentiles(data()).percentile_rank.dropna().between(0,100).all()
def test_it_services_highest_roe_highest_rank():
 d=data();g=d[d.peer_group_name=='IT Services'];p=compute_peer_percentiles(d);r=p[(p.peer_group_name=='IT Services')&(p.metric=='roe')];cid=g.loc[g.return_on_equity_pct.idxmax(),'company_id'];assert r.loc[r.company_id==cid,'percentile_rank'].iloc[0]==r.percentile_rank.max()
