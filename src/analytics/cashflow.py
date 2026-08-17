
def free_cash_flow(cfo,cfi):
    if cfo is None or cfi is None: return None
    return cfo+cfi
def capex(cfi): return None if cfi is None else abs(cfi)
def cfo_quality_score(history):
    vals=[cfo/pat for cfo,pat in history if cfo is not None and pat not in (None,0)]
    if not vals: return None,"Not Available"
    score=sum(vals[-5:])/min(len(vals),5)
    return score,("High Quality" if score>1.0 else "Moderate" if score>=0.5 else "Accrual Risk")
def capital_intensity(cfi,sales):
    if cfi is None or sales is None or sales==0: return None,"Not Available"
    pct=abs(cfi)/abs(sales)*100
    return pct,("Light" if pct<=5 else "Moderate" if pct<=8 else "Capital Intensive")
def fcf_conversion_rate(fcf,operating_profit):
    if fcf is None or operating_profit is None or operating_profit==0: return None
    return fcf/operating_profit*100
