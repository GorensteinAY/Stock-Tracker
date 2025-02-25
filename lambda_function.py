# Lambda function to run daily

import csv_add_cik
import cik_lookup
import dynamodb_csv
import dynamodb_utils
import dynamodb_financials

def lambda_handler(event, context):
    # Review Tickers.csv for any new tickers
    csv_add_cik.add_cik_to_csv("Tickers.csv")

    # Look up CIK's and add to DynamoDB, clean table to remove duplicates and tickers with no CIK
    dynamodb_csv.upload_csv_to_dynamodb("Updated_Tickers.csv")
    dynamodb_utils.clean_duplicates()
    dynamodb_utils.clean_cik()
    
    # Update financials from SEC EDGAR database, clean table to remove tickers with no financials
    dynamodb_financials.update_dynamodb()
    dynamodb_utils.clean_financials()


# Ensure the script still works when run manually
if __name__ == "__main__":
    lambda_handler({}, {})