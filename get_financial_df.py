# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:12:05 2021

@author: Gunardilin
"""

import pandas as pd
import numpy as np

def define_ebitda(tables_list):
    if 'ebitda' in tables_list[2].index:
        return tables_list[2].loc['ebitda']
    else:
        return tables_list[2].loc['net income'].values - tables_list[2].loc['total interest expense'].values - tables_list[2].loc['income tax'].values - tables_list[2].loc['depreciation & amortization expense']
    
def get_financial_df(tables_list):
    tables_list[2].rename({'interest expense': 'total interest expense',
                      'income taxes': 'income tax'}, axis='index', inplace=True)
    table_df =  pd.DataFrame({'shareholderequity': tables_list[1].loc['total shareholders\' equity'],
              'longtermdebt': tables_list[1].loc['long-term debt'],
              'eps': tables_list[2].loc['eps (basic)'],
              'epsgrowth': tables_list[2].loc['eps (basic) growth'],
              'netincome': tables_list[2].loc['net income'],
              'roa': tables_list[1].loc['total shareholders\' equity / assets'],
              'interestexpense': tables_list[2].loc['total interest expense'],
              'ebitda': define_ebitda(tables_list)
             })
    table_df.longtermdebt[table_df.longtermdebt.isnull()] = 0
    table_df.interestexpense[table_df.interestexpense.isnull()] = 0
    
    # Sometimes the dataset is shown in wrong year sequence.
    # Therefore it needs to be sorted by year index and
    # the epsgrowth needs to be calculated manually.
    table_df.sort_index(inplace=True)
    table_df.epsgrowth = table_df.eps.pct_change()
    
    return table_df

def calculate_ratio(financial_df):
    # financial_df.longtermdebt[financial_df.longtermdebt.isnull()] = 0
    # financial_df.interestexpense[financial_df.interestexpense.isnull()] = 0
    financial_df['roe'] = financial_df.netincome / financial_df.shareholderequity
    financial_df['interestcoverageratio'] = financial_df.ebitda / \
        financial_df.interestexpense
    # If interest expense is 0 and ebitda is positive number then interest
    # coverage ratio will be infinite (999999999).
    financial_df[np.isinf(financial_df)] = 999999999
    return financial_df

if __name__ == "__main__":
    from get_statement import get_statement, open_in_excel
    open_in_excel(get_financial_df(get_statement('BYDDY')))
    # print(calculate_ratio(get_financial_df(get_statement('coke'))))
    open_in_excel(calculate_ratio(get_financial_df(get_statement('BYDDY'))))