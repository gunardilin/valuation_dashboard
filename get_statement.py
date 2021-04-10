# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 16:12:35 2021

@author: Gunardilin
"""
import pandas as pd
import numpy as np
# import html5lib
# from bs4 import BeautifulSoup

def remove_coma(string):
    if type(string) == str:
        return string.replace(',', '')
    else:
        return string

def get_statement(ticker):
    balance_sheet_url = "https://www.marketwatch.com/investing/stock/" + ticker + "/financials/balance-sheet"
    income_url = "https://www.marketwatch.com/investing/stock/" + ticker + "/financials"
    #cashflow_url = "https://www.marketwatch.com/investing/stock/" + ticker + "/financials/cash-flow"
    #urls = [balance_sheet_url, income_url, cashflow_url]
    urls = [balance_sheet_url, income_url]
    tables_list = []  # list for all table dataframes
    pattern = {'\((.*)\)': '-\\1',    # convert (x) to -x
               'T': ' * 1000000000000',
               'B': ' * 1000000000',  # convert B to ' * 1000000000'
               'M': ' * 1000000',     # convert M to ' * 1000000'
               'K': ' * 1000',        # convert K to ' * 1000'
               '%': ' / 100'          # convert % to ' / 100'
              }

    for url in urls:
        tables = pd.read_html(url, match="Item", index_col=0, thousands=',') # Scrape only tables with word 'Item' in it
        for i in range(len(tables)):
            tables[i] = tables[i].applymap(remove_coma)
            #tables[i].to_csv('table{}.csv'.format(i))
            # remove the duplicate from index.
            tables[i].index = list(map(lambda x: " ".join(dict.fromkeys(x.lower().split())), tables[i].index))
            if not tables[i].columns[-1].isdigit(): # If a column has no digit character, drop it
                tables[i].drop(tables[i].columns[-1], axis="columns", inplace=True)
            # 1. replace '-' with np.nan
            # 2. replace according regex patern dictionary
            # 3. evaluate the arithmetic symbols with pd.eval
            tables_list.append(tables[i].replace("-", np.nan).replace(pattern, regex=True).applymap(pd.eval, na_action='ignore'))
    return tables_list

def open_in_excel(dataframe):
    import xlwings as xw
    xw.view(dataframe)

if __name__ == "__main__":
    tables_list = get_statement("baba")
    # for i in tables_list:
    #     open_in_excel(i)
        