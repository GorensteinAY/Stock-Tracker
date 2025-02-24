#get_financials_test.py

from cik_lookup import *
from get_financials import *

# Initialize CIK lookup
cik_mapping, name_mapping = load_sec_ticker_data()

ticker = "IPSC"
cik = get_cik_by_ticker(ticker,cik_mapping)  # Ensure this returns a valid CIK
financials = get_latest_financials("0001850119")  # Check if this returns valid data

print(f"Debug CIK for {ticker}: {cik}")
print(f"Debug Financials for {ticker}: {financials}")
