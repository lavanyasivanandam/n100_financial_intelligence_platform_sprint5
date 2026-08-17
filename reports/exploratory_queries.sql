
-- Q01: Row counts by table
SELECT 'companies' table_name, COUNT(*) rows FROM companies
UNION ALL SELECT 'profitandloss',COUNT(*) FROM profitandloss
UNION ALL SELECT 'balancesheet',COUNT(*) FROM balancesheet
UNION ALL SELECT 'cashflow',COUNT(*) FROM cashflow
UNION ALL SELECT 'analysis',COUNT(*) FROM analysis
UNION ALL SELECT 'documents',COUNT(*) FROM documents
UNION ALL SELECT 'prosandcons',COUNT(*) FROM prosandcons
UNION ALL SELECT 'sectors',COUNT(*) FROM sectors
UNION ALL SELECT 'stock_prices',COUNT(*) FROM stock_prices
UNION ALL SELECT 'market_cap',COUNT(*) FROM market_cap
UNION ALL SELECT 'financial_ratios',COUNT(*) FROM financial_ratios
UNION ALL SELECT 'peer_groups',COUNT(*) FROM peer_groups;

-- Q02: Null counts in P&L
SELECT COUNT(*) total_rows,
       SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) null_sales,
       SUM(CASE WHEN net_profit IS NULL THEN 1 ELSE 0 END) null_net_profit
FROM profitandloss;

-- Q03: Year coverage per company
SELECT company_id, COUNT(*) years, MIN(year) first_year, MAX(year) last_year
FROM profitandloss GROUP BY company_id ORDER BY years,company_id;

-- Q04: Companies with fewer than 5 P&L years
SELECT company_id, COUNT(*) years FROM profitandloss GROUP BY company_id HAVING COUNT(*) < 5;

-- Q05: Balance-sheet mismatch rows
SELECT company_id,year,total_assets,total_liabilities,
       ABS(total_assets-total_liabilities)/NULLIF(ABS(total_assets),0) mismatch_pct
FROM balancesheet
WHERE ABS(total_assets-total_liabilities)/NULLIF(ABS(total_assets),0) >= 0.01;

-- Q06: Negative/non-positive sales
SELECT company_id,year,sales FROM profitandloss WHERE sales <= 0;

-- Q07: Cash-flow reconciliation
SELECT company_id,year,net_cash_flow,
       operating_activity+investing_activity+financing_activity components_sum
FROM cashflow
WHERE ABS(net_cash_flow-(operating_activity+investing_activity+financing_activity)) > 10;

-- Q08: Orphan check (should return zero)
SELECT p.company_id FROM profitandloss p LEFT JOIN companies c ON c.id=p.company_id
WHERE c.id IS NULL;

-- Q09: Latest available P&L year by company
SELECT c.id,c.company_name,MAX(p.year) latest_year
FROM companies c LEFT JOIN profitandloss p ON p.company_id=c.id
GROUP BY c.id,c.company_name ORDER BY latest_year;

-- Q10: Sector company counts
SELECT broad_sector,COUNT(*) companies
FROM sectors GROUP BY broad_sector ORDER BY companies DESC;
