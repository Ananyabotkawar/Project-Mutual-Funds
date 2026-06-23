import os
import pandas as pd

master_path = os.path.join("data", "raw", "01_fund_master.csv")
raw_dir = os.path.join("data", "raw")

print("RUNNING DATA QUALITY ASSURANCE REPORT")

if not os.path.exists(master_path):
    print(f"Aborting: Master registry file not found at {master_path}")
else:
    # 1. Load your asset scheme registry
    df_master = pd.read_csv(master_path)
    
    # Ensure standard string type alignment for accurate evaluation comparison
    # (Assuming column name tracking the ID is 'scheme_code' or 'amfi_code')
    code_column = 'scheme_code' if 'scheme_code' in df_master.columns else 'amfi_code'
    master_codes = set(df_master[code_column].astype(str).unique())
    
    print(f"Master registry tracking code collection size: {len(master_codes)}")
    
    # 2. Compile all unique schema keys currently present across downloaded data files
    downloaded_codes = set()
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('_raw.csv') and not f.startswith('fund_master')]
    
    for file in csv_files:
        try:
            df_temp = pd.read_csv(os.path.join(raw_dir, file))
            if 'scheme_code' in df_temp.columns:
                unique_vals = df_temp['scheme_code'].astype(str).unique()
                downloaded_codes.update(unique_vals)
        except Exception as e:
            print(f"Error scanning data properties for {file}: {e}")

    print(f"Total verified active codes found inside historical logs: {len(downloaded_codes)}")
    print("-" * 50)
    
    # 3. Compute Set Intersections for mapping verification
    missing_in_history = master_codes - downloaded_codes
    orphan_history_records = downloaded_codes - master_codes
    
    # 4. Format outputs based on findings
    if not missing_in_history:
        print("PASS: All AMFI reference codes in your master list match corresponding historical records.")
    else:
        print(f"FAIL: Found {len(missing_in_history)} missing master code links!")
        print(f"The following codes have no downloadable backup entries: {list(missing_in_history)}")
        
    if orphan_history_records:
        print(f"\nNOTE: Detected historical data files not indexed by master registry: {list(orphan_history_records)}")
        
print("VALIDATION PROTOCOL CONCLUDED")
