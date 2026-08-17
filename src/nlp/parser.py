import re
import pandas as pd
PATTERN=re.compile(r"(\d+)\s*Years?\s*:\s*(-?\d+(?:\.\d+)?)\s*%", re.I)
FIELDS={"compounded_sales_growth":"revenue_cagr","compounded_profit_growth":"pat_cagr","stock_price_cagr":"stock_price_cagr","roe":"roe"}
def parse_analysis(df):
    rows=[]; failures=[]
    for _,r in df.iterrows():
        for source,metric in FIELDS.items():
            raw="" if pd.isna(r.get(source)) else str(r.get(source))
            m=PATTERN.search(raw)
            if m:
                rows.append([r["company_id"],metric,int(m.group(1)),float(m.group(2))])
            elif raw.strip():
                failures.append([r["company_id"],source,raw])
    parsed=pd.DataFrame(rows,columns=["company_id","metric_type","period_years","value_pct"])
    failed=pd.DataFrame(failures,columns=["company_id","source_field","raw_text"])
    return parsed,failed
