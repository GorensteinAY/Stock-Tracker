# Add CIK to CSV list of tickers

import time
import pandas as pd
from cik_lookup import get_cik_by_company_name, get_cik_by_ticker, load_sec_ticker_data

# Process the CSV file and update with CIKs
def add_cik_to_csv(csv_file):
    cik_mapping, name_mapping = load_sec_ticker_data()

    try:
        df = pd.read_csv(csv_file, delimiter=";", dtype=str)  # Ensure all data is read as strings
        
        if "CIK" not in df.columns:
            df["CIK"] = ""

        valid_rows = []  # Store rows that will remain in the final CSV

        for index, row in df.iterrows():
            ticker = str(row["Ticker"]).strip().upper() if pd.notna(row["Ticker"]) else ""
            company_name = str(row["CompanyName"]).strip() if pd.notna(row["CompanyName"]) else ""

            if not ticker and not company_name:
                print(f"Skipping row {index}: Missing both ticker and company name")
                continue

            # First attempt: Look up by ticker
            cik = get_cik_by_ticker(ticker, cik_mapping)

            # If not found, try looking up by company name
            if cik is None:
                print(f"Ticker {ticker} not found, searching by company name...")
                cik = get_cik_by_company_name(company_name, name_mapping)

            # If found, add to the valid list
            if cik:
                row["CIK"] = cik  # Store the found CIK
                valid_rows.append(row)
            else:
                print(f"❌ CIK not found for {ticker} ({company_name}) - Removing from CSV.")

            # Respect SEC rate limits
            time.sleep(0.2)  # 5 requests per second max

        # Convert the filtered rows back into a DataFrame
        updated_df = pd.DataFrame(valid_rows)

        output_file = "Updated_" + csv_file
        updated_df.to_csv(output_file, index=False, sep=";")
        print(f"✅ Updated CSV saved as {output_file}")

    except Exception as e:
        print(f"Error processing the CSV: {e}")

"""
# Run the function
csv_filename = "Tickers.csv"  # Update with your file path
add_cik_to_csv(csv_filename)

"""