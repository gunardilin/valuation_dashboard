# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:33:16 2021

@author: Gunardilin
"""
import pandas as pd

def minimum_pe (stockpriceserie, financialdf):
    stockpricedf = pd.DataFrame(stockpriceserie)
    stockpricedf['year'] = stockpricedf.index.year
    price = stockpricedf.groupby('year').tail(1).set_index('year')['Close']
    priceearning_byyear = pd.DataFrame()
    financialdf.index.rename('year', inplace=True)
    priceearning_byyear['eps'] = financialdf['eps']
    priceearning_byyear.index = priceearning_byyear.index.astype(int)
    priceearning_byyear = priceearning_byyear.merge(price.to_frame(name='price'), 
                                                    left_index=True, right_index=True)
    priceearning_byyear['pe'] = priceearning_byyear['price']/priceearning_byyear['eps']
    return round(priceearning_byyear.pe.min(), 2)

if __name__ == '__main__':
    from get_statement import get_statement#, open_in_excel
    from get_financial_df import get_financial_df, calculate_ratio
    from get_stock_price import get_stock_price
    ticker = 'aapl'
    stock_price = get_stock_price(ticker)
    financial_df = calculate_ratio(get_financial_df(get_statement(ticker)))
    #open_in_excel(financial_df)
    print(minimum_pe(stock_price, financial_df))