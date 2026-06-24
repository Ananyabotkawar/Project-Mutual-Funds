import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Configuration paths
PROCESSED_DIR = os.path.join("data", "processed")
RAW_DIR = os.path.join("data", "raw")
DB_PATH = "bluestock_mf.db"

def init_database():
    print("Building SQLite database tables...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables to build fresh
    cursor.execute("DROP TABLE IF EXISTS fact_transactions;")
    cursor.execute("DROP TABLE IF EXISTS fact_nav;")
    cursor.execute("DROP TABLE IF EXISTS fact_performance;")
    cursor.execute("DROP TABLE IF EXISTS dim_fund;")
    
    # 1. Dimension Fund Table
    cursor.execute("""
    CREATE TABLE dim_fund (
        amfi_code INTEGER PRIMARY KEY,
        fund_house TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT NOT NULL
    );
    """)
    
    # 2. Fact Daily NAV Table
    cursor.execute("""
    CREATE TABLE fact_nav (
        nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        date TEXT NOT NULL,
        nav REAL NOT NULL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """)
    
    # 3. Fact Transactions Table
    cursor.execute("""
    CREATE TABLE fact_transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        transaction_date TEXT NOT NULL,
        transaction_type TEXT NOT NULL,
        amount_inr REAL NOT NULL,
        kyc_status TEXT NOT NULL,
        state TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """)
    
    # 4. Fact Performance Table (Updated to match your actual file columns cleanly)
    cursor.execute("""
    CREATE TABLE fact_performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        return_1yr_pct REAL,
        return_3yr_pct REAL,
        return_5yr_pct REAL,
        aum_crore REAL,
        expense_ratio REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database structures initialized successfully.")

def populate_tables():
    print("\nLoading datasets into database...")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # 1. Load Dim Fund
    master_path = os.path.join(RAW_DIR, "01_fund_maste.csv")
    if os.path.exists(master_path):
        df_master = pd.read_csv(master_path)
        df_master.columns = df_master.columns.str.strip().str.lower()
        if 'scheme_code' in df_master.columns:
            df_master = df_master.rename(columns={'scheme_code': 'amfi_code'})
        
        df_fund_dim = df_master[['amfi_code', 'fund_house', 'category', 'sub_category']].drop_duplicates()
        df_fund_dim.to_sql('dim_fund', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_fund_dim)} records into dim_fund.")

    # 2. Load Fact NAV History
    nav_path = os.path.join(PROCESSED_DIR, "cleaned_nav_history.csv")
    if os.path.exists(nav_path):
        df_nav = pd.read_csv(nav_path)
        df_nav.to_sql('fact_nav', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_nav)} records into fact_nav.")
        
    # 3. Load Fact Transactions
    trans_path = os.path.join(PROCESSED_DIR, "cleaned_transactions.csv")
    if os.path.exists(trans_path):
        df_trans = pd.read_csv(trans_path)
        cols = ['amfi_code', 'transaction_date', 'transaction_type', 'amount_inr', 'kyc_status', 'state']
        df_trans = df_trans[[c for c in cols if c in df_trans.columns]]
        df_trans.to_sql('fact_transactions', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_trans)} records into fact_transactions.")

    # 4. Load Fact Performance (Explicitly keeping only schema-matching columns)
    perf_path = os.path.join(PROCESSED_DIR, "cleaned_performance.csv")
    if os.path.exists(perf_path):
        df_perf = pd.read_csv(perf_path)
        
        # Explicit column mapping if your cleaned file uses 'expense_ratio_pct'
        if 'expense_ratio_pct' in df_perf.columns and 'expense_ratio' not in df_perf.columns:
            df_perf = df_perf.rename(columns={'expense_ratio_pct': 'expense_ratio'})
            
        target_cols = ['amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'aum_crore', 'expense_ratio']
        
        # Keep only the target columns that exist in the file
        df_perf_filtered = df_perf[[c for c in target_cols if c in df_perf.columns]]
        
        df_perf_filtered.to_sql('fact_performance', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_perf_filtered)} records into fact_performance.")

if __name__ == "__main__":
    init_database()
    populate_tables()