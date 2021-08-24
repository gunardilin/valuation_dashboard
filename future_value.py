# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 12:31:25 2021

@author: Gunardilin
"""

import numpy as np
import numpy_financial as npf
import pandas as pd
from get_statement import open_in_excel

# def minimum_pe (stockpriceserie, financialdf):
#     stockpricedf = pd.DataFrame(stockpriceserie)
#     stockpricedf['year'] = stockpricedf.index.year
#     price = stockpricedf.groupby('year').tail(1).set_index('year')['Close']
#     priceearning_byyear = pd.DataFrame()
#     financialdf.index.rename('year', inplace=True)
#     priceearning_byyear['eps'] = financialdf['eps']
#     priceearning_byyear.index = priceearning_byyear.index.astype(int)
#     priceearning_byyear = priceearning_byyear.merge(price.to_frame(name='price'), 
#                                                     left_index=True, right_index=True)
    
#     # In case the select company just IPOed on current year x, no stock price 
#     # in x-1 is available. After merging operation, priceearning_byyear will be 
#     # empty, eventhough eps for x-1 is available. Therefore minimum_pe should 
#     # use the last available eps and current share price to generate minimum_pe.
#     if len(priceearning_byyear) == 0:
#         priceearning_byyear= pd.concat([priceearning_byyear, 
#                                         price.to_frame(name='price')])
#         priceearning_byyear.eps.iloc[-1] = financialdf.eps.iloc[-1]
        
#     priceearning_byyear['pe'] = priceearning_byyear['price']/priceearning_byyear['eps']
#     # print('Min PE:', round(priceearning_byyear.pe.min(), 2))
#     return round(priceearning_byyear.pe.min(), 2)

def min_max_avg_pe (stockpriceserie, financialdf):
    stockpricedf = pd.DataFrame(stockpriceserie)
    stockpricedf['year'] = stockpricedf.index.year
    price = stockpricedf.groupby('year').tail(1).set_index('year')['Close']
    priceearning_byyear = pd.DataFrame()
    financialdf.index.rename('year', inplace=True)
    priceearning_byyear['eps'] = financialdf['eps']
    priceearning_byyear.index = priceearning_byyear.index.astype(int)
    priceearning_byyear = priceearning_byyear.merge(price.to_frame(name='price'), 
                                                    left_index=True, right_index=True)
    
    # In case the select company just IPOed on current year x, no stock price 
    # in x-1 is available. After merging operation, priceearning_byyear will be 
    # empty, eventhough eps for x-1 is available. Therefore minimum_pe should 
    # use the last available eps and current share price to generate minimum_pe.
    if len(priceearning_byyear) == 0:
        priceearning_byyear= pd.concat([priceearning_byyear, 
                                        price.to_frame(name='price')])
        priceearning_byyear.eps.iloc[-1] = financialdf.eps.iloc[-1]
        
    priceearning_byyear['pe'] = priceearning_byyear['price']/priceearning_byyear['eps']
    # print(priceearning_byyear)
    # print('Min PE:', round(priceearning_byyear.pe.min(), 2))
    return [round(priceearning_byyear.pe.min(), 2), round(
        priceearning_byyear.pe.max(), 2), round(priceearning_byyear.pe.mean(), 
        2)]

def generate_futureprice (ticker, financialdf, discountrate, marginrate,
                          stockprice_df):
    n_year = 10 # Future year, whose EPS to be calculated.
    lasteps = financialdf.eps.iloc[-1]
    stockpriceserie = stockprice_df['Close']
    
    dfprice = pd.DataFrame(columns=['ticker', 'annualgrowthrate', 'lasteps',
                                    'futureeps'])
    pd.options.display.float_format = '{:20,.2f}'.format
    try:
        n_year = len(financialdf) # Year duration in financialdf
        annualgrowthrate = npf.rate(n_year, 0, -1*financialdf.eps.iloc[0], 
                                    lasteps)
        futureeps = abs(npf.fv(annualgrowthrate, n_year, 0, lasteps))
        for i in range(3):
            dfprice.loc[i] = [ticker, annualgrowthrate, lasteps, futureeps]
        
    except:
        print('EPS does not exist')
    dfprice.set_index('ticker', inplace=True)
    pe_ratios = min_max_avg_pe(stockprice_df, financialdf)
    # dfprice['min_pe'] = pe_ratios[0]
    dfprice['pe'] = pe_ratios
    dfprice['FV'] = dfprice['futureeps'] * dfprice['pe']
    # dfprice['PV'] = abs(npf.pv(discountrate, n_year, 0, dfprice['FV']))
    dfprice['PV'] = npf.pv(discountrate, n_year, 0, dfprice['FV']) * -1
    # print(dfprice[['FV', 'PV']])
    dfprice['marginprice'] = np.where((dfprice['futureeps'] > 0), 
                                      dfprice['PV'] * (1-marginrate), 0)
    dfprice['currentshareprice'] = stockpriceserie[-1]
    dfprice['decision'] = np.where((dfprice['currentshareprice'] < dfprice['marginprice']),
                                   'Buy', 'Sell')
    # open_in_excel(dfprice)
    return dfprice

if __name__ == '__main__':
    from datetime import datetime
    from get_financial_df import get_financial_df, calculate_ratio
    from get_statement import get_statement
    from get_stock_price import get_stock_price
    start = datetime.now()
    ticker = 'aapl'
    discountrate = 0.1
    marginrate = 0.1
    financial_df = calculate_ratio(get_financial_df(get_statement(ticker)))
    stockprice_df = get_stock_price(ticker)

    print(generate_futureprice(ticker, financial_df, discountrate, 
                                       marginrate, stockprice_df))
    open_in_excel(generate_futureprice(ticker, financial_df, discountrate, 
                                      marginrate, stockprice_df))
    print(datetime.now() - start)