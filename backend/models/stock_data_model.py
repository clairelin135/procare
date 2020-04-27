import warnings
warnings.filterwarnings('ignore')

from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import pandas as pd
import numpy as np

def core_parse(ticker, factors_to_load):
    url = "http://finance.yahoo.com/quote/%s?p=%s"%(ticker,ticker)
    response = requests.get(url, verify=False)
    sleep(4)
    parser = html.fromstring(response.text)
    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
    summary_data = OrderedDict()
    other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(ticker)
    summary_json_response = requests.get(other_details_json_link)
    
    
    final = {}

    json_loaded_summary =  json.loads(summary_json_response.text)
    core = json_loaded_summary["quoteSummary"]["result"][0]
    processing_sets = []

    for factor in factors_to_load:
        if factor in core:
            processing_sets.append(core[factor])
    
    if "calendarEvents" in core:
        if 'earnings' in core["calendarEvents"]:
            processing_sets.append(core["calendarEvents"]['earnings'])
    
    
    for ps in processing_sets:
        for x in list(ps.keys()):    
            if isinstance(ps[x], dict):
                if len(ps[x]) == 0:
                    ps[x] = None
                elif 'raw' in ps[x]:
                    ps[x] = ps[x]['raw']

            if isinstance(ps[x], list):
                ps[x] = [y['fmt'] for y in ps[x] if 'fmt' in y]
                    
        final.update(ps)
    
    
    return final  

def get_key_data(ticker, factors_to_load):
    return core_parse(ticker, factors_to_load)

def get_full_portfolio_dataset(tickers, factors_to_load=["financialData", "defaultKeyStatistics"]):
    d = {}
    
    for ticker in tickers:
        d[ticker] = get_key_data(ticker, factors_to_load)
    
    to_return = pd.DataFrame.from_dict(d, orient='index')
    
    return to_return

def get_market_compare(ticker):
    x = get_full_portfolio_dataset([ticker])
    return list(x['52WeekChange'])[0] - list(x['SandP52WeekChange'])[0]