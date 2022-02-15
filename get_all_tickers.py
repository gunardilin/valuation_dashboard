#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /Users/GunardiLin/Desktop/valuation_dashboard/get_all_tickers.py
# Project: /Users/GunardiLin/Desktop/valuation_dashboard
# Created Date: Monday, October 11th 2021, 9:59:45 pm
# Author: Gunardi Ali
# -----
# Last Modified: Tuesday, February 15th 2022, 10:40:02 pm
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
from sqlite3 import Error
import pandas as pd
import urllib.request as request
import json

def get_companies_from_sec():
    URL1 = 'https://www.sec.gov/files/company_tickers_exchange.json'
    URL2 = 'https://www.sec.gov/files/company_tickers.json'

    try:
        sec_dict = request.urlopen(URL1)
        mode = '1'
    except:
        sec_dict = request.urlopen(URL2)
        mode = '2'
    for line in sec_dict:
        decoded_line = line.decode("utf-8")
    company_dict = json.loads(decoded_line)
    if mode == '1':
        company_df = pd.DataFrame(company_dict['data'],columns=['cik', 'Security',
            'Symbol', 'exchange'])
    elif mode == '2':
        company_df = pd.DataFrame.from_dict(company_dict, orient='index')
        company_df.rename(columns={"cik_str": "cik", "ticker": "Symbol", \
            "title": "Security"}, inplace=True)
    return company_df[['Symbol', 'Security']]

def format_for_dashdropdown(pddataframe):
    return [{'label': "{}, {}".format(pddataframe.iloc[i].Symbol, 
                                        pddataframe.iloc[i].Security), 
             'value': pddataframe.iloc[i].Symbol} 
            for i in range(len(pddataframe.index))]

if __name__ == "__main__":
    print(format_for_dashdropdown(get_companies_from_sec().head()))