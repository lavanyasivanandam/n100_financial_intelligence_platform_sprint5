
def debt_to_equity(borrowings,equity_capital,reserves):
    borrowings=0 if borrowings is None else borrowings
    if borrowings==0: return 0.0
    denom=(equity_capital or 0)+(reserves or 0)
    return None if denom<=0 else borrowings/denom
def interest_coverage(operating_profit,other_income,interest):
    if interest is None or interest==0: return None
    return ((operating_profit or 0)+(other_income or 0))/interest
def interest_coverage_label(value,interest):
    if interest is None or interest==0: return "Debt Free"
    if value is None: return "Not Available"
    return "High Risk" if value<1.5 else "Adequate"
def net_debt(borrowings,investments): return (borrowings or 0)-(investments or 0)
def asset_turnover(sales,total_assets):
    if total_assets is None or total_assets==0: return None
    return (sales or 0)/total_assets
