from src.analytics.capital_allocation import capital_allocation_pattern
def test_reinvestor(): assert capital_allocation_pattern(10,-5,-2)[1]=='Reinvestor'
def test_shareholder(): assert capital_allocation_pattern(10,-5,2)[1]=='Shareholder Returns'
def test_liquidating(): assert capital_allocation_pattern(10,5,-2)[1]=='Liquidating Assets'
def test_distress(): assert capital_allocation_pattern(-10,5,2)[1]=='Distress Signal'
def test_pre_revenue(): assert capital_allocation_pattern(-10,5,-2)[1]=='Pre-Revenue Growth'
def test_growth_debt(): assert capital_allocation_pattern(10,5,2)[1]=='Growth + Debt'
def test_mixed1(): assert capital_allocation_pattern(-10,-5,-2)[1]=='Mixed'
def test_mixed2(): assert capital_allocation_pattern(-10,-5,2)[1]=='Mixed'
