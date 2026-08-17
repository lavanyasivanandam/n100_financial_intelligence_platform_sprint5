
import re
import pandas as pd

MONTHS = {
    "JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
    "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12
}

def normalize_ticker(value):
    if pd.isna(value):
        return None
    return str(value).strip().upper()

def normalize_year(value):
    """Normalize documented annual/period labels to YYYY-MM."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    if re.fullmatch(r"\d{4}-\d{2}", s):
        y,m=map(int,s.split("-"))
        return s if 1<=m<=12 else "PARSE_ERROR"
    if re.fullmatch(r"\d{4}(?:\.0+)?", s):
        return f"{int(float(s)):04d}-03"
    u=re.sub(r"\s+"," ",s.upper())
    m=re.fullmatch(r"([A-Z]{3})[- ](\d{2,4})",u)
    if m and m.group(1) in MONTHS:
        yy=m.group(2); y=int(yy); y=2000+y if len(yy)==2 else y
        return f"{y:04d}-{MONTHS[m.group(1)]:02d}"
    m=re.fullmatch(r"FY(\d{2,4})",u)
    if m:
        yy=m.group(1); y=int(yy); y=2000+y if len(yy)==2 else y
        return f"{y:04d}-03"
    return "PARSE_ERROR"
