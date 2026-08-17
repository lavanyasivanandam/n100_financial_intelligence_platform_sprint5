
NORMAL="NORMAL"; DECLINE_TO_LOSS="DECLINE_TO_LOSS"; TURNAROUND="TURNAROUND"
BOTH_NEGATIVE="BOTH_NEGATIVE"; ZERO_BASE="ZERO_BASE"; INSUFFICIENT="INSUFFICIENT"
def cagr(start,end,years):
    if years is None or years<=0 or start is None or end is None: return None,INSUFFICIENT
    if start==0: return None,ZERO_BASE
    if start>0 and end<0: return None,DECLINE_TO_LOSS
    if start<0 and end>0: return None,TURNAROUND
    if start<0 and end<0: return None,BOTH_NEGATIVE
    try: return ((end/start)**(1.0/years)-1.0)*100.0,NORMAL
    except (ValueError,ZeroDivisionError,OverflowError): return None,"INVALID"
