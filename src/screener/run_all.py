from pathlib import Path
import json,sqlite3
from .engine import load_config,latest_financials,add_composite,run_preset,export_screener,ROOT,OUTPUT
from src.analytics.peer import run as peer_run
def main():
 cfg=load_config();con=sqlite3.connect(ROOT/'db/nifty100.db');d=add_composite(latest_financials(con));con.close();results={n:run_preset(n,d,cfg) for n in cfg['presets']};export_screener(results,cfg);p,_=peer_run();summary={'universe':len(d),'preset_counts':{k:len(v) for k,v in results.items()},'peer_groups':int(p.peer_group_name.nunique()),'peer_percentile_rows':len(p),'radar_png_count':len(list((ROOT/'reports/radar_charts').glob('*.png')))};(OUTPUT/'sprint3_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
