# add_ciks_to_csv.py

import pandas as pd
from cik_lookup import get_cik_from_ticker  # Import the CIK lookup function

def add_ciks_to_csv(csv_file: str, output_csv: str):
    try:
        # Try reading the CSV with a semicolon delimiter and skipping bad lines
        df = pd.read_csv(csv_file, delimiter=';', on_bad_lines='skip')  # Adjust delimiter to semicolon

        # Print out the first few rows to confirm the data structure
        print("CSV loaded successfully. Sample data:")
        print(df.head())
        
        # Ensure we have a 'Ticker' column before proceeding
        if 'Ticker' not in df.columns:
            print("Error: 'Ticker' column not found in CSV.")
            return
        
        # Add a new column for CIKs
        cik_list = []

        # Loop through the tickers in the CSV and fetch CIK for each
        for ticker in df["Ticker"]:
            cik = get_cik_from_ticker(ticker)  # Function to fetch CIK for each ticker
            cik_list.append(cik)

        # Add the CIK column to the DataFrame
        df["CIK"] = cik_list

        # Save the updated DataFrame back to a new CSV
        df.to_csv(output_csv, index=False)
        print(f"Updated CSV saved to {output_csv}")
    
    except Exception as e:
        print(f"Error processing the CSV: {e}")

# Example usage
add_ciks_to_csv("Tickers.csv", "Tickers_with_CIKs.csv")
