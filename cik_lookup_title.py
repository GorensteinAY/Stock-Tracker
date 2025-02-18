# Get CIK from Company Name

import sys
import requests
import pandas as pd

from bs4 import BeautifulSoup

headers = {"User-Agent":"agorenst@tepper.cmu.edu"}

def get_cik_from_title(title: str) -> str:
    
    title = title.upper()
    url = f"https://www.sec.gov/files/company_tickers.json"

    title_json = requests.get(url,headers=headers).json()
    

    for company in title_json.values():
        if company["title"] == title:
            cik = str(company["cik_str"]).zfill(10)
            print(f"Successfully fetched cik for company: {title}:",cik)
            return cik
    raise ValueError(f"Title {title} not found in SEC database")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        title = sys.argv[1]  # Pass the ticker from the command-line argument
        cik = get_cik_from_title(title)
        if cik:
            print(f"CIK for {title} is {cik}")
        else:
            print(f"Could not find CIK for {title}")
    else:
        print("Please provide a company name.")
