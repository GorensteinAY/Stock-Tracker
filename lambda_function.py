# Lambda function to run daily

import concurrent.futures
import csv_add_cik
import dynamodb_csv
import dynamodb_utils
import dynamodb_financials

def lambda_handler(event, context):
    
    """
    # Step 1️: Process Tickers from CSV (Sequential)
    csv_add_cik.add_cik_to_csv("Tickers.csv")
    dynamodb_csv.upload_csv_to_dynamodb("Updated_Tickers.csv")
    print("Updated DynamoDB")

    # Step 2️: Clean up database (Must run in sequence)
    dynamodb_utils.clean_duplicates()
    dynamodb_utils.clean_cik()
    print("Cleaned DynamoDB to remove duplicates and blank CIK's")
    


    # Step 3️: Fetch financials and clean in parallel (Optimized)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_financials = executor.submit(dynamodb_financials.update_dynamodb)
        future_clean_financials = executor.submit(dynamodb_utils.clean_financials)

        # Make sure update_dynamodb() finishes before clean_financials()
        future_financials.result()  # Waits for financial update to complete
        future_clean_financials.result()  # Now cleans safely

    """
    
    dynamodb_financials.update_dynamodb()
    dynamodb_utils.clean_financials()
    print("Processed financials and cleaned DynamoDB to remove blanks")
    return {"status": "success"}


# Ensure the script still works when run manually
if __name__ == "__main__":
    lambda_handler({}, {})