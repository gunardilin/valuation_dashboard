# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:12:05 2021

@author: Gunardilin
"""

import pandas as pd

def define_ebitda(tables_list):
    if 'ebitda' in tables_list[2].index:
        return tables_list[2].loc['ebitda']
    else:
        return tables_list[2].loc['net income'].values - tables_list[2].loc['total interest expense'].values - tables_list[2].loc['income tax'].values - tables_list[2].loc['depreciation & amortization expense']
    
def get_financial_df(tables_list):
    tables_list[2].rename({'interest expense': 'total interest expense',
                      'income taxes': 'income tax'}, axis='index', inplace=True)
    return pd.DataFrame({'shareholderequity': tables_list[1].loc['total shareholders\' equity'],
              'longtermdebt': tables_list[1].loc['long-term debt'],
              'eps': tables_list[2].loc['eps (basic)'],
              'epsgrowth': tables_list[2].loc['eps (basic) growth'],
              'netincome': tables_list[2].loc['net income'],
              'roa': tables_list[1].loc['total shareholders\' equity / assets'],
              'interestexpense': tables_list[2].loc['total interest expense'],
              'ebitda': define_ebitda(tables_list)
             })

def calculate_ratio(financial_df):
    financial_df['roe'] = financial_df.netincome / financial_df.shareholderequity
    financial_df['interestcoverageratio'] = financial_df.ebitda / financial_df.interestexpense
    return financial_df

if __name__ == "__main__":
    from get_statement import get_statement, open_in_excel
    # open_in_excel(get_financial_df(get_statement('coke')))
    # print(calculate_ratio(get_financial_df(get_statement('coke'))))
    open_in_excel(calculate_ratio(get_financial_df(get_statement('coke'))))