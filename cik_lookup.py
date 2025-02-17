import requests
import pandas as pd

from bs4 import BeautifulSoup

headers = {"User-Agent":"agorenst@tepper.cmu.edu"}

def get_cik_from_ticker(ticker: str) -> str:
    
    ticker = ticker.upper().replace(".","-")
    url = f"https://www.sec.gov/files/company_tickers.json"

    ticker_json = requests.get(url,headers=headers).json()

    for company in ticker_json.values():
        if company["ticker"] == ticker:
            cik = str(company["cik_str"]).zfill(10)
            return cik
    raise ValueError(f"Ticker {ticker} not found in SEC database")

"""
    ticker_json = requests.get("https://www.sec.gov/files/company_tickers.json",headers=headers).json()
    # SEC EDGAR URL for company search (will search by ticker)
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=include&action=getcompany"
    
    # Send GET request to the SEC search page
    response = requests.get(url, headers={"User-Agent": "Russell2000Lookup/1.0 (gorenstein.alexander@gmail.com)"})
    
    if response.status_code == 200:
        # Parse the HTML page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the CIK number on the page
        cik_tag = soup.find('div', {'class': 'companyName'})
        if cik_tag:
            # The CIK is typically listed as a number in the company name section
            cik = cik_tag.get_text().split("CIK#")[-1].strip()
            return cik
        else:
            print(f"CIK not found for {ticker}")
            return None
    else:
        print(f"Error fetching CIK for {ticker}")
        return None

"""
