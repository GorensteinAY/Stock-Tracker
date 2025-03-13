import logging
import csv_add_cik
import dynamodb_csv
import dynamodb_utils
import dynamodb_financials

# Set up logging
logging.basicConfig(
    filename="app.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    logging.info("Starting financial update process")

    try:
        """
        # Review Tickers.csv for any new tickers
        logging.info("Checking for new tickers in CSV")
        csv_add_cik.add_cik_to_csv("Tickers.csv")

        # Upload to DynamoDB and clean up data
        logging.info("Uploading CSV to DynamoDB")
        dynamodb_csv.upload_csv_to_dynamodb("Updated_Tickers.csv")
        dynamodb_utils.clean_duplicates()
        dynamodb_utils.clean_cik()
        """

        # Update financials from SEC EDGAR database
        logging.info("Updating financial data from SEC EDGAR database")
        dynamodb_financials.update_dynamodb()
        dynamodb_utils.clean_financials()

        # Update timestamps for successful updates
        logging.info("Updating timestamps")
        dynamodb_utils.update_time()

        logging.info("✅ Financial update process completed successfully")

    except Exception as e:
        logging.error(f"❌ Error during execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
