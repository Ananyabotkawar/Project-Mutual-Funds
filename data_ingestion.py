import os
import pandas as pd

# This tells Python to look inside Project Mutual Funds/data/raw
RAW_DATA_DIR = os.path.join("data", "raw")

print("STARTING DATA INGESTION PROCESS")

# Verify the directory exists
if not os.path.exists(RAW_DATA_DIR):
    print(f"ERROR: The directory '{RAW_DATA_DIR}' was not found.")
else:
    # Find all files inside data/raw that end with '.csv'
    csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"WARNING: No CSV files found in '{RAW_DATA_DIR}'. Please check the folder.")
    else:
        print(f"Found {len(csv_files)} CSV file(s) to process.\n")
        
        # Loop through each of the 10 files automatically
        for i, file_name in enumerate(csv_files, start=1):
            file_path = os.path.join(RAW_DATA_DIR, file_name)
            
            print(f"[{i}/{len(csv_files)}] Processing file: {file_name}")
            print("-" * 40)
            
            try:
                # Load the dataset into a pandas DataFrame
                df = pd.read_csv(file_path)
                
                # Print Shape (Rows, Columns)
                print(f"Shape (Rows, Columns): {df.shape}")
                
                # Print Data Types of columns
                print("\nData Types:")
                print(df.dtypes)
                
                # Print the first 3 rows
                print("\nFirst 3 Rows:")
                print(df.head(3))
                
            except Exception as e:
                print(f"ERROR: Failed to read {file_name}. Details: {e}")
                
            print("==================================================")

print("\nData ingestion checking sequence completed.")