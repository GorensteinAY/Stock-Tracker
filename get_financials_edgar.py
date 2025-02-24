# Get company data from SEC EDGAR database via edgartools library

import pandas as pd
from edgar import *
from xbrl import XBRLParser, GAAP

set_identity("Alexander Gorenstein agorenst@tepper.cmu.edu")

c = Company("AAPL")
c.financials.cashflow

# parse = XBRLParser.parse(c.financials.get_balance_sheet())
# print(parse)