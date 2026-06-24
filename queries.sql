-- queries.sql

-- 1. Top 5 funds by total transactional investment volume
SELECT 
    f.fund_house, 
    f.category, 
    SUM(t.amount_inr) AS total_invested_inr
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
WHERE t.transaction_type IN ('SIP', 'Lumpsum')
GROUP BY f.fund_house, f.category
ORDER BY total_invested_inr DESC
LIMIT 5;

-- 2. Average NAV price parsed per fund house
SELECT 
    f.fund_house, 
    ROUND(AVG(n.nav), 2) AS average_nav_price
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY f.fund_house
ORDER BY average_nav_price DESC;

-- 3. Total Transaction counts grouped by State and Transaction Type
SELECT 
    state, 
    transaction_type, 
    COUNT(*) AS total_transactions,
    SUM(amount_inr) AS aggregate_volume
FROM fact_transactions
GROUP BY state, transaction_type
ORDER BY total_transactions DESC;

-- 4. Low cost structural funds with an expense ratio below 1%
SELECT 
    f.amfi_code, 
    f.fund_house, 
    f.category, 
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- 5. KYC distribution count among system transaction records
SELECT 
    kyc_status, 
    COUNT(*) as customer_record_count
FROM fact_transactions
GROUP BY kyc_status;

-- 6. High-Value Transactions (Investments over ₹5,000,000 / 50 Lakhs)
SELECT 
    t.transaction_id,
    f.fund_house,
    t.transaction_type,
    t.amount_inr,
    t.state
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
WHERE t.amount_inr >= 5000000 AND t.transaction_type IN ('SIP', 'Lumpsum')
ORDER BY t.amount_inr DESC;

-- 7. High-Risk Capital Alert (Total volume tied up in Unverified/Pending KYC accounts)
SELECT 
    kyc_status,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_stuck_volume_inr,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_size
FROM fact_transactions
WHERE kyc_status IN ('N', 'P')
GROUP BY kyc_status;

-- 8. Fund Category Performance Leaderboard (Top 3-Year Return Averages)
SELECT 
    f.category,
    COUNT(DISTINCT f.amfi_code) AS total_active_schemes,
    ROUND(AVG(p.return_3yr_pct), 2) AS average_3y_return_pct,
    ROUND(AVG(p.expense_ratio), 2) AS average_expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY average_3y_return_pct DESC;

-- 9. Cost vs. Return Efficiency Matrix (High Return, Low Expense Schemes)

SELECT 
    f.amfi_code,
    f.fund_house,
    f.category,
    p.return_5yr_pct,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_5yr_pct > 15.0 AND p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC, p.return_5yr_pct DESC;

-- 10. Dynamic Volatility Snapshot (Most recent asset price check)
SELECT 
    f.fund_house,
    f.category,
    n.date AS calculation_date,
    n.nav AS closing_nav_price
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE n.date = (SELECT MAX(date) FROM fact_nav)
ORDER BY n.nav DESC;