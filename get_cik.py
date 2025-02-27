import requests
import pandas as pd
import re  # To clean company names

SEC_API_BASE_URL = "https://www.sec.gov/files/company_tickers.json"
HEADERS = {"User-Agent":"agorenst@tepper.cmu.edu"} 

# Load SEC ticker & company name data
def load_sec_ticker_data():
    try:
        response = requests.get(SEC_API_BASE_URL, headers=HEADERS)
        response.raise_for_status()
        sec_data = response.json()

        cik_mapping = {str(entry["ticker"]).upper(): str(entry["cik_str"]).zfill(10) for entry in sec_data.values()}
        name_mapping = {clean_company_name(entry["title"]): str(entry["cik_str"]).zfill(10) for entry in sec_data.values()}
        
        return cik_mapping, name_mapping
    except requests.RequestException as e:
        print(f"Error fetching SEC data: {e}")
        return {}, {}

# Normalize company names for better matching
def clean_company_name(name):
    if not isinstance(name, str):  # Ensure it's a string before processing
        return ""
    
    name = name.strip().upper()  # Remove extra spaces & ensure uppercase
    name = re.sub(r"[^\w\s]", "", name)  # Remove special characters
    name = re.sub(r"\s+", " ", name)  # Ensure single spaces between words
    return name

# Function to find CIK based on ticker
def get_cik_by_ticker(ticker, cik_mapping):
    return cik_mapping.get(str(ticker).upper(), None)

# Function to find CIK based on cleaned company name
def get_cik_by_company_name(company_name, name_mapping):
    return name_mapping.get(clean_company_name(company_name), None)
