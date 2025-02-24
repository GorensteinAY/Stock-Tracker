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
        # Extract financials
        revenue = data["facts"]["us-gaap"]["Revenues"]["units"]["USD"][-1]["val"]
        net_income = data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"][-1]["val"]
        cash_flow = data["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"][-1]["val"]

        return {
            "Revenue": revenue,
            "Net_Income": net_income,
            "Cash_Flow": cash_flow
        }

    except KeyError:
        print(f"⚠️ Missing financial data for CIK {cik}")
        return None
