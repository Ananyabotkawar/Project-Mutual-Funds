import os
import requests
import pandas as pd

# The specific URL target for HDFC Top 100 Fund - Direct Plan - Growth
API_URL = "https://api.mfapi.in/mf/125497"

# Target path to dump our raw data extraction
OUTPUT_CSV_PATH = os.path.join("data", "raw", "hdfc_top_100_raw.csv")
print("LAUNCHING MUTUAL FUND NAV INGESTION PIPELINE")
try:
    print(f"Sending GET request to API: {API_URL}")
    # 1. Fetch data from web server
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status() # Throws an error if the website goes down
    
    print("API Response received successfully. Parsing JSON content...")
    # 2. Translate response string into a clean JSON dictionary
    json_data = response.json()
    
    # 3. Extract the metadata details
    meta_info = json_data.get("meta", {})
    fund_name = meta_info.get("scheme_name", "Unknown Scheme")
    scheme_code = meta_info.get("scheme_code", "Unknown Code")
    
    print(f"Target Fund Identified: {fund_name} (Code: {scheme_code})")
    
    # 4. Extract the historical array data
    nav_records = json_data.get("data", [])
    
    if not nav_records:
        print("WARNING: The API structural payload contains no NAV data arrays.")
    else:
        print(f"Extracted {len(nav_records)} daily market price logs.")
        
        # 5. Load array into a Pandas DataFrame
        df = pd.DataFrame(nav_records)
        
        # Ensure target destination folders exist
        os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
        
        # 6. Export directly to raw CSV file without saving index numbers
        df.to_csv(OUTPUT_CSV_PATH, index=False)
        print(f"SUCCESS: Raw extraction written to -> {OUTPUT_CSV_PATH}")
        
        # Display sample overview to confirm file consistency
        print("\nPipeline Verification Sample Layout:")
        print("-" * 40)
        print(df.head(5))

except requests.exceptions.RequestException as req_error:
    print(f"NETWORK ERROR: Failed to establish API handshakes. Details: {req_error}")
except ValueError as parse_error:
    print(f"PARSING ERROR: Failed to decode target structural JSON format. Details: {parse_error}")
except Exception as unexpected_error:
    print(f"PIPELINE FAILURE: An unexpected issue occurred. Details: {unexpected_error}")

print("NAV INGESTION PIPELINE EXECUTION TERMINATED")