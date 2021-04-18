#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: c:\Users\Gunardilin\Desktop\Value Investing Dashboard\sp500.py
# Project: c:\Users\Gunardilin\Desktop\Value Investing Dashboard
# Created Date: Sunday, February 28th 2021, 3:32:50 pm
# Author: Gunardi Ali
# -----
# Last Modified: Sunday, April 18th 2021, 4:21:14 pm
# Modified By: Gunardi Ali
# -----
# Copyright (c) 2021 Gunardi Ali
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###
# import requests
# from bs4 import BeautifulSoup
import pandas as pd
from get_statement import open_in_excel

# def get_sp500_info():
#     resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
#     soup = BeautifulSoup(resp.text, 'lxml')
#     stocks_info = []
#     tickers = []
#     securities = []
#     gics_industries = []
#     gics_sub_industries = []
#     print(soup)
#     table = soup.find('table', {'class': 'wikitable sortable'})
    
#     for row in table.findAll('tr')[1:]:
#         ticker = row.findAll('td')[0].text
#         security = row.findAll('td')[1].text
#         gics_industry = row.findAll('td')[3].text
#         gics_sub_industry = row.findAll('td')[4].text
    
#         tickers.append(ticker.lower().replace(r"\n", " "))
#         securities.append(security)
#         gics_industries.append(gics_industry.lower())
#         gics_sub_industries.append(gics_sub_industry.lower())
    
#     stocks_info.append(tickers)
#     stocks_info.append(securities)
#     stocks_info.append(gics_industries)
#     stocks_info.append(gics_sub_industries)
    
#     stocks_info_df = pd.DataFrame(stocks_info).T
#     stocks_info_df.columns=['tickers','security','gics_industry','gics_sub_industry']
#     stocks_info_df['seclabels'] = 'SP500'
#     return stocks_info_df

def get_sp500_info():
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df2 = df[0][['Symbol', 'Security', 'GICS Sector']]
    return df2
    
def format_for_dashdropdown(pddataframe):
    # df_mini = pddataframe[:5]
    # for i in range(len(df_mini.index)):
    #     print(i)
    #     print(df_mini.iloc[i, [0, 1]])
    #     print({'label': "{}, {}, {}".format(df_mini.iloc[i].Symbol, 
    #                                         df_mini.iloc[i].Security,
    #                                         df_mini.iloc[i]['GICS Sector']), 
    #            'value': df_mini.iloc[i].Symbol})
    return [{'label': "{}, {}, {}".format(pddataframe.iloc[i].Symbol, 
                                          pddataframe.iloc[i].Security, 
                                          pddataframe.iloc[i]['GICS Sector']), 
             'value': pddataframe.iloc[i].Symbol} 
            for i in range(len(pddataframe.index))]

if __name__ == "__main__":
    open_in_excel(get_sp500_info())
    # print(format_for_dashdropdown(get_sp500_info()))