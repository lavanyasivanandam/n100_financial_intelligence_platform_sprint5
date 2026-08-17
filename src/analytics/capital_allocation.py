
def sign(x):
    if x is None:return None
    return "+" if x>0 else "-" if x<0 else "0"
PATTERN_LABELS={
 "(+,-,-)":"Reinvestor","(+,-,+)":"Shareholder Returns","(+,+,-)":"Liquidating Assets",
 "(-,+,+)":"Distress Signal","(-,+,-)":"Pre-Revenue Growth","(+,+,+)":"Growth + Debt",
 "(-,-,-)":"Mixed","(-,-,+)":"Mixed","(0,0,0)":"Mixed"}
def capital_allocation_pattern(cfo,cfi,cff):
    s=(sign(cfo),sign(cfi),sign(cff))
    key=f"({','.join(s)})" if all(x is not None for x in s) else None
    return key,PATTERN_LABELS.get(key,"Mixed / Unclassified")
