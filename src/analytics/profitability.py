
def safe_pct(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0: return None
    return numerator / denominator * 100.0
def net_profit_margin(net_profit, sales): return safe_pct(net_profit, sales)
def operating_profit_margin(operating_profit, sales): return safe_pct(operating_profit, sales)
def return_on_equity(net_profit, equity_capital, reserves):
    if net_profit is None: return None
    denom=(equity_capital or 0)+(reserves or 0)
    return None if denom<=0 else net_profit/denom*100.0
def roce(ebit,equity_capital,reserves,borrowings):
    if ebit is None: return None
    denom=(equity_capital or 0)+(reserves or 0)+(borrowings or 0)
    return None if denom<=0 else ebit/denom*100.0
def return_on_assets(net_profit,total_assets): return safe_pct(net_profit,total_assets)
