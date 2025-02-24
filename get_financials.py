# Get company financial data from SEC EDGAR database

import requests

# SEC API Base URL
SEC_API_BASE = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json"

# Required Headers (Identify yourself)
HEADERS = {
    "User-Agent": "Alexander Gorenstein (agorenst@tepper.cmu.edu)"
}

# Function to fetch financials from SEC API
def get_latest_financials(cik):
    url = SEC_API_BASE.format(str(cik).zfill(10))  # Zero-pad CIK to 10 digits
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Error: Unable to fetch data for CIK {cik}")
        return None

    data = response.json()
    
    try:
        
        # Check if financial data exists before accessing it
        revenue = data["facts"]["us-gaap"].get("Revenues", {}).get("units", {}).get("USD", [])
        net_income = data["facts"]["us-gaap"].get("NetIncomeLoss", {}).get("units", {}).get("USD", [])
        net_cash = data["facts"]["us-gaap"].get("NetCashProvidedByUsedInOperatingActivities", {}).get("units", {}).get("USD", [])

        # Extract latest values if available
        revenue_val = revenue[-1]["val"] if revenue else None
        net_income_val = net_income[-1]["val"] if net_income else None
        net_cash_val = net_cash[-1]["val"] if net_cash else None

        # If all values are None, return None to indicate missing data
        if revenue_val is None and net_income_val is None and net_cash_val is None:
            return None


        return {"Revenue": revenue_val, 
                "Net_Income": net_income_val, 
                "Net_Cash": net_cash_val}

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching data for CIK {cik}: {e}")
        return None
