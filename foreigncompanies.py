# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 20:28:41 2021

@author: Gunardilin
"""
import pandas as pd
from get_statement import open_in_excel
from datetime import datetime

def last_row(symbol, name):
    requirements = [symbol.lower()=="total", name.isdigit()]
    return all(requirements)

def get_foreigncompanies_info():
    df_list = []
    links = ["https://stockmarketmba.com/nonuscompaniesonusexchanges.php",
              "https://stockmarketmba.com/listofadrs.php"]
    for i in links:
        df = pd.read_html(i)[0][['Symbol', 'Name', 'GICS Sector']]
        if last_row(df.iloc[-1]['Symbol'], df.iloc[-1]['Name']):
            df_list.append(df.iloc[:-1])
        else:
            df_list.append(df)
    return pd.concat(df_list).reset_index(drop=True).rename(columns={'Name': 'Security'})
    
if __name__ == "__main__":
    start = datetime.now()
    df = get_foreigncompanies_info()
    print(datetime.now() - start)
    open_in_excel(get_foreigncompanies_info())