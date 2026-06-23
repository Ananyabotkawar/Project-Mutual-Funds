import os
import requests
import pandas as pd

SCHEMES = {
    "119551": "sbi_bluechip",
    "120503": "icici_bluechip",
    "118632": "nippon_large_cap",
    "119092": "axis_bluechip",
    "120841": "kotak_bluechip"
}

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

print("BATCH NAV INGESTION ACTIVE")

for code, name in SCHEMES.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"Requesting data for {name.upper()} (Code: {code})...")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        nav_records = json_data.get("data", [])
        if not nav_records:
            print(f"Warning: No data found for {name}")
            continue
            
        # Convert to DataFrame
        df = pd.DataFrame(nav_records)
        
        # Add a column for scheme_code to uniquely identify records later
        df["scheme_code"] = int(code)
        
        # Re-organize columns slightly for standard structure
        df = df[["scheme_code", "date", "nav"]]
        
        # Save file
        output_file = os.path.join(RAW_DIR, f"{name}_raw.csv")
        df.to_csv(output_file, index=False)
        print(f"Success: Saved {len(nav_records)} records to {output_file}\n")
        
    except Exception as e:
        print(f"Error extracting code {code}: {e}\n")
        
print("BATCH DOWNLOAD COMPLETE")