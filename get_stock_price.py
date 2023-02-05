#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: Friday, March 5th 2021, 3:24:22 pm
# Author: Gunardi Ali
# -----

import datetime as dt
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
from pandas_datareader import data
import pandas as pd

def get_stocks_price(tickers: list):
    today = dt.datetime.now()
    stocksprice_df = data.get_data_yahoo(tickers, \
        start=today - dt.timedelta(days=5*365), end=today).Close
    if type(stocksprice_df) == pd.core.frame.Series:
        stocksprice_df.name=tickers[0]
    return stocksprice_df

def format_stockprice_df(stockprice_df):
    return {'data': [{
        'x': stockprice_df.index,
        'y': stockprice_df.Close.values}]}

if __name__ == "__main__":
    # print(format_stockprice_df(get_stock_price('AAPL')))
    print(get_stocks_price(['AAPL']).head())
    print(get_stocks_price(['AAPL', 'COKE']).head())
    print("Finish")