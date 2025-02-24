# Update list of companies stored in DynamoDB with latest financials from SEC EDGAR database


import boto3
import time
from decimal import Decimal
from get_financials import get_latest_financials 

# AWS Config
DYNAMODB_TABLE = "StockTickers"

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

def update_dynamodb():
    """Loop through companies in DynamoDB and update their latest financials."""
    response = table.scan()
    companies = response.get("Items", [])

    for company in companies:
        ticker = company["Ticker"]
        cik = company.get("CIK")

        if not cik:
            print(f"⚠️ No CIK for {ticker}, skipping...")
            continue

        financials = get_latest_financials(cik)
        if not financials:
            continue

    # Assuming `financials` is the dictionary with raw data
    print(f"Original Financials: {financials}")

    # Clean financials (remove None values and convert to Decimal)
    financials_cleaned = {
        k: Decimal(str(v)) for k, v in financials.items() if v is not None
    }

    # Debug the cleaned data
    print(f"Cleaned Financials: {financials_cleaned}")

    # Check for missing data after cleaning (if any of the fields is still None or invalid)
    if any(value is None for value in financials_cleaned.values()):
        print(f"Missing or invalid data for {ticker}: {financials_cleaned}")

    # Now, ensure valid data for update to DynamoDB
    revenue = financials_cleaned.get("Revenue", Decimal('0'))
    net_income = financials_cleaned.get("NetIncome", Decimal('0'))
    cash_flow = financials_cleaned.get("CashFlow", Decimal('0'))

    # Update DynamoDB
    try:
        table.update_item(
            Key={"Ticker": ticker},
            UpdateExpression="SET Revenue = :r, NetIncome = :n, CashFlow = :c",
            ExpressionAttributeValues={
                ":r": revenue,
                ":n": net_income,
                ":c": cash_flow,
            }
        )
        print(f"Successfully updated {ticker} in DynamoDB.")
    except Exception as e:
        print(f"Error updating {ticker} in DynamoDB: {e}")


    print(f"✅ Updated {ticker}: {financials}")
    time.sleep(1.2)  # Respect SEC rate limit

# Run the update
if __name__ == "__main__":
    update_dynamodb()
