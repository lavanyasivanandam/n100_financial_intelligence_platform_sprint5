import pandas as pd

def latest_by_company(df,year_col='year'):
    if df.empty:return df
    x=df.copy(); x['_y']=pd.to_numeric(x[year_col].astype(str).str[:4],errors='coerce')
    return x.sort_values(['company_id','_y']).groupby('company_id').tail(1).drop(columns=['_y'])

def safe_label(x,fmt='{:.2f}'):
    return '—' if pd.isna(x) else fmt.format(float(x))

def pct_change_index(df,cols):
    unique_cols=list(dict.fromkeys(cols))
    data={"year": df["year"]}
    for c in unique_cols:
        raw=df.loc[:, c]
        if isinstance(raw, pd.DataFrame):
            raw=raw.iloc[:, 0]
        series=pd.to_numeric(raw,errors="coerce")
        first=series.dropna().iloc[0] if series.notna().any() else None
        data[c]=((series/first)-1)*100 if first not in (None,0) else pd.Series(pd.NA,index=df.index,dtype="Float64")
    return pd.DataFrame(data,index=df.index)
