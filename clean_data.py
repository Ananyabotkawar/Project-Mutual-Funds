import os
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_nav_history():
    print(" Cleaning nav_history.csv...")
    file_path = os.path.join(RAW_DIR, "02_nav_history.csv")
    
    if not os.path.exists(file_path):
        print(f" File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    
    # 1. Clean column names
    df.columns = df.columns.str.strip().str.lower()
    
    # 2. Parse dates to datetime format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']) # Drop rows where date formatting failed
    
    # 3. Validate NAV > 0 (Drop rows with negative or zero NAV)
    df = df[df['nav'] > 0]
    
    # 4. Remove exact duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'], keep='last')
    
    # 5. Handle Weekends/Holidays via Forward Fill
    # To ffill properly, we sort by asset code and date, then group by asset code
    df = df.sort_values(by=['amfi_code', 'date']).reset_index(drop=True)
    
    # Generating a complete date range per fund to catch missing weekend dates
    cleaned_dfs = []
    for amfi, group in df.groupby('amfi_code'):
        group = group.set_index('date')
        full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
        # Reindex expands the dataframe to include all calendar dates
        group = group.reindex(full_range)
        group['amfi_code'] = group['amfi_code'].ffill()
        group['nav'] = group['nav'].ffill()
        group = group.reset_index().rename(columns={'index': 'date'})
        cleaned_dfs.append(group)
        
    df_cleaned = pd.concat(cleaned_dfs, ignore_index=True)
    
    # Save to processed folder
    output_path = os.path.join(PROCESSED_DIR, "cleaned_nav_history.csv")
    df_cleaned.to_csv(output_path, index=False)
    print(f" Saved cleaned NAV history to {output_path} (Rows: {len(df_cleaned)})")

if __name__ == "__main__":
    clean_nav_history()
    
def clean_transactions():
    print("\nCleaning investor_transactions.csv...")
    file_path = os.path.join(RAW_DIR, "08_investor_transactions.csv")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    
    # Parse Date
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df = df.dropna(subset=['transaction_date'])
    
    # Standardize transaction types
    type_mapping = {
        'sip': 'SIP', 'systematic investment plan': 'SIP',
        'lumpsum': 'Lumpsum', 'one-time': 'Lumpsum',
        'redemption': 'Redemption', 'withdrawal': 'Redemption', 'sell': 'Redemption'
    }
    
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip().str.lower()
    df['transaction_type'] = df['transaction_type'].map(type_mapping).fillna('Other')
    

    df = df[df['amount_inr'] > 0]
    
    # Enforce KYC Enum constraints (Y = Yes, N = No, P = Pending)
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.upper()
    df.loc[~df['kyc_status'].isin(['Y', 'N', 'P']), 'kyc_status'] = 'N'
    
    output_path = os.path.join(PROCESSED_DIR, "cleaned_transactions.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned transactions to {output_path} (Rows: {len(df)})")
    
def clean_performance():
    print("\nCleaning scheme_performance.csv...")
    file_path = os.path.join(RAW_DIR, "07_scheme_performance.csv")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    
    # Enforce numeric return values
    return_cols = [col for col in df.columns if 'return' in col]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[(df[col] > 500) | (df[col] < -100), col] = np.nan
        df[col] = df[col].fillna(0.0)
        
    # Expense Ratio validation (0.1% to 2.5%)
    if 'expense_ratio' in df.columns:
        df['expense_ratio'] = pd.to_numeric(df['expense_ratio'], errors='coerce')
        df['expense_ratio'] = df['expense_ratio'].clip(lower=0.1, upper=2.5)
        
    output_path = os.path.join(PROCESSED_DIR, "cleaned_performance.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned performance to {output_path} (Rows: {len(df)})")


if __name__ == "__main__":
    clean_nav_history()
    clean_transactions()
    clean_performance()