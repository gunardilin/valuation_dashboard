#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: c:\Users\Gunardilin\Desktop\Value Investing Dashboard\russel3000.py
# Project: c:\Users\Gunardilin\Desktop\Value Investing Dashboard
# Created Date: Tuesday, March 2nd 2021, 7:18:39 pm
# Author: Gunardi Ali
# -----
# Last Modified: Sunday, April 18th 2021, 4:18:58 pm
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
# import pandas as pd
# import xlwings as xw

# def get_russel3000_info():
#     resp = requests.get("https://www.ishares.com/us/products/239714/ishares-russell-3000-etf#holdings")
#     soup = BeautifulSoup(resp.text, "lxml")
#     stocks_info = []
#     tickers = []
#     securities = []
#     gics_industries = []
    
#     table = soup.find('table', {'class': 'display product-table border-row dataTable no-footer'})
#     for row in table.findAll('tr')[1:]:
#         ticker = row.findAll('td')[0].text
#         security = row.findAll('td')[1].text
#         gics_industry = row.findAll('td')[2].text

#         tickers.append(ticker.lower().replace(r"\n", " "))
#         securities.append(security)
#         gics_industries.append(gics_industry.lower())
        
#     stocks_info.append(tickers)
#     stocks_info.append(securities)
#     stocks_info.append(gics_industries)
    
#     stocks_info_df = pd.DataFrame(stocks_info).T
#     stocks_info_df.columns=['tickers','security','gics_industry']
#     stocks_info_df['seclabels'] = 'Russel3000'
#     return stocks_info_df

import requests
from json import loads
import pandas as pd
from get_statement import open_in_excel

def get_russel3000_info():
    url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?tab=all&fileType=json"
    r = requests.get(url)
    json = loads(r.content.decode('utf-8-sig'))
    df = pd.DataFrame(json['aaData'])
    df2 = df.iloc[:, [0, 1, 2]]
    df2.columns = ['Symbol', 'Security', 'GICS Sector']
    return df2

if __name__ == "__main__":
    open_in_excel(get_russel3000_info())