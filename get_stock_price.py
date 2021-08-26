#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: c:\Users\Gunardilin\Desktop\Value Investing Dashboard\get_stock_price.py
# Project: c:\Users\Gunardilin\Desktop\Value Investing Dashboard
# Created Date: Friday, March 5th 2021, 3:24:22 pm
# Author: Gunardi Ali
# -----
# Last Modified: Thursday, August 26th 2021, 7:34:26 pm
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
import datetime as dt
from pandas_datareader import data

def get_stock_price(ticker):
    today = dt.datetime.now()
    stockprice_df = data.DataReader(name=ticker, data_source="yahoo", start=today -
                    dt.timedelta(days=5*365), end=today)
    return stockprice_df

def get_stocks_price(tickers: list):
    today = dt.datetime.now()
    stocksprice_df = data.DataReader(name=tickers, data_source="yahoo", start=today -
                    dt.timedelta(days=5*365), end=today).Close
    return stocksprice_df

def format_stockprice_df(stockprice_df):
    # print(stockprice_df[:5])
    # print(type(stockprice_df))
    return {'data': [{
        'x': stockprice_df.index,
        'y': stockprice_df.Close.values}]}

if __name__ == "__main__":
    print(format_stockprice_df(get_stock_price('AAPL')))