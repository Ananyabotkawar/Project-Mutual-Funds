# Bluestock Mutual Funds Analytics Warehouse Data Dictionary

This document provides a comprehensive map of the columns, strict data types, core business definitions, and architectural source references for the relational Star Schema deployed inside `bluestock_mf.db`.

---

## 1. dim_fund (Dimension Table)
**Business Purpose:** Serves as the master lookup registry for all registered mutual fund schemes. It removes text redundancies from the fact tables.
**Source Reference:** Generated from raw staging data file `01_fund_maste.csv`.

| Column Name | Data Type | Constraint / Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Unique asset code assigned by the Association of Mutual Funds in India. |
| `fund_house` | TEXT | NOT NULL | The Asset Management Company (AMC) managing the fund (e.g., SBI Mutual Fund). |
| `category` | TEXT | NOT NULL | Broad asset class classification (e.g., Equity, Debt, Hybrid). |
| `sub_category` | TEXT | NOT NULL | Specific investment strategy classification (e.g., Small Cap, Large Cap, Gilt). |

---

## 2. fact_nav (Fact Table)
**Business Purpose:** Stores historical daily tracking metrics for Net Asset Value (NAV). Missing market weekend and holiday prices are resolved using a forward-fill (ffill) time-series strategy.
**Source Reference:** Generated from cleaned production data file `cleaned_nav_history.csv`.

| Column Name | Data Type | Constraint / Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `nav_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sequence tracker for database rows. |
| `amfi_code` | INTEGER | FOREIGN KEY | References `dim_fund(amfi_code)` to link asset descriptions. |
| `date` | TEXT | NOT NULL | Calculated calendar timestamp normalized to standard `YYYY-MM-DD` format. |
| `nav` | REAL | NOT NULL | Net Asset Value per unit, validated to be strictly greater than zero. |

---

## 3. fact_transactions (Fact Table)
**Business Purpose:** Captures individual retail investor transactions, tracking capital flowing in and out of the fund schemes.
**Source Reference:** Generated from cleaned production data file `cleaned_transactions.csv`.

| Column Name | Data Type | Constraint / Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `transaction_id`| INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sequence tracker for transaction receipts. |
| `amfi_code` | INTEGER | FOREIGN KEY | References `dim_fund(amfi_code)` to map target scheme. |
| `transaction_date`| TEXT | NOT NULL | Date the transaction request was settled (`YYYY-MM-DD`). |
| `transaction_type`| TEXT | NOT NULL | Categorized into strict enums: `SIP`, `Lumpsum`, or `Redemption`. |
| `amount_inr` | REAL | NOT NULL | Absolute monetary financial volume of the transaction (must be > 0). |
| `kyc_status` | TEXT | NOT NULL | Regulatory compliance flag restricted to enums: `Y` (Yes), `N` (No), `P` (Pending). |
| `state` | TEXT | None | Regional geographical indicator of the investor within India. |

---

## 4. fact_performance (Fact Table)
**Business Purpose:** Houses medium-to-long-term compound annual growth returns and operational fee tracking percentages.
**Source Reference:** Generated from cleaned production data file `cleaned_performance.csv`.

| Column Name | Data Type | Constraint / Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `performance_id`| INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for performance rows. |
| `amfi_code` | INTEGER | FOREIGN KEY | References `dim_fund(amfi_code)`. |
| `return_1yr_pct`| REAL | None | 1-Year annualized percentage return trailing metric. |
| `return_3yr_pct`| REAL | None | 3-Year annualized percentage return trailing metric. |
| `return_5yr_pct`| REAL | None | 5-Year annualized percentage return trailing metric. |
| `aum_crore` | REAL | None | Total Assets Under Management valued in Crores (INR). |
| `expense_ratio` | REAL | None | Operational management fee charged to investors, clamped between 0.1% and 2.5%. |

