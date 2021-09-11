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

# def min_max_avg_pe (stockpriceserie, financialdf):
#     # print('Inputs for minmax:')
#     # print('a1')
#     # print(stockpriceserie.head())
#     # print('a2')
#     # print(financialdf.head())
#     stockpricedf = pd.DataFrame(stockpriceserie)
#     stockpricedf['year'] = stockpricedf.index.year

#     price = stockpricedf.groupby('year').tail(1).set_index('year').iloc[:,0]
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
#     # print(priceearning_byyear)
#     # print('Min PE:', round(priceearning_byyear.pe.min(), 2))
#     return [round(priceearning_byyear.pe.min(), 2), round(
#         priceearning_byyear.pe.max(), 2), round(priceearning_byyear.pe.mean(), 
#         2)]

# def generate_futureprice (ticker, financialdf, discountrate, marginrate,
#                           stockpriceserie):
#     n_year = 10 # Future year, whose EPS to be calculated.
#     lasteps = financialdf.eps.iloc[-1]
    
#     dfprice = pd.DataFrame(columns=['ticker', 'annualgrowthrate', 'lasteps',
#                                     'futureeps'])
#     pd.options.display.float_format = '{:20,.2f}'.format
#     try:
#         n_year = len(financialdf) # Year duration in financialdf
#         annualgrowthrate = npf.rate(n_year, 0, -1*financialdf.eps.iloc[0], 
#                                     lasteps)
#         futureeps = abs(npf.fv(annualgrowthrate, n_year, 0, lasteps))
#         for i in range(3):
#             dfprice.loc[i] = [ticker, annualgrowthrate, lasteps, futureeps]
        
#     except:
#         print('EPS does not exist')
#     dfprice.set_index('ticker', inplace=True)
#     pe_ratios = min_max_avg_pe(stockpriceserie, financialdf)
#     # dfprice['min_pe'] = pe_ratios[0]
#     dfprice['pe'] = pe_ratios
#     dfprice['FV'] = dfprice['futureeps'] * dfprice['pe']
#     # dfprice['PV'] = abs(npf.pv(discountrate, n_year, 0, dfprice['FV']))
#     dfprice['PV'] = npf.pv(discountrate, n_year, 0, dfprice['FV']) * -1
#     # print(dfprice[['FV', 'PV']])
#     dfprice['marginprice'] = np.where((dfprice['futureeps'] > 0), 
#                                       dfprice['PV'] * (1-marginrate), 0)
#     dfprice['currentshareprice'] = stockpriceserie[-1]
#     dfprice['decision'] = np.where((dfprice['currentshareprice'] < dfprice['marginprice']),
#                                    'Buy', 'Sell')
#     # open_in_excel(dfprice)
#     return dfprice

def growth_pe (stockpriceserie, financialdf):
    growth_pe = {}
    lasteps = financialdf.eps.iloc[-1]
    try:
        n_year = len(financialdf) # Year duration in financialdf
        growth_pe['growth_min'] = financialdf['epsgrowth'].min()
        growth_pe['growth_mean'] = round(npf.rate(n_year, 0, 
                                            -1*financialdf.eps.iloc[0], 
                                            lasteps), 4)
        growth_pe['growth_max'] = financialdf['epsgrowth'].max()

        pe_historical = min_mean_max_pe(stockpriceserie, financialdf)
        growth_pe['pe_min'] = pe_historical[0]
        growth_pe['pe_mean'] = pe_historical[1]
        growth_pe['pe_max'] = pe_historical[2]
        # print('growth_pe', growth_pe)
        return growth_pe
    except:
        print('EPS does not exist.')
        return {}

def min_mean_max_pe (stockpriceserie, financialdf):
    # print('Inputs for minmean:')
    # print('b1')
    # print(stockpriceserie.head())
    # print('b2')
    # print(financialdf.head())
    stockpricedf = pd.DataFrame(stockpriceserie)
    stockpricedf['year'] = stockpricedf.index.year

    price = stockpricedf.groupby('year').tail(1).set_index('year').iloc[:,0]
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
    if len(priceearning_byyear) == 0 or \
        priceearning_byyear.notnull().values.sum() != 0:
        # This if statement is executed if the priceearning_byyear is empty or
        # if eps is available and no stockprice is available. This is the case,
        # for company that is just ipoed. Such company supply the eps for previous
        # years before ipo and pre-ipo the stock price is not available. 
        # E.g. Coupang in year 2021.
        priceearning_byyear= pd.concat([priceearning_byyear, 
                                        price.to_frame(name='price')])
        priceearning_byyear.eps.iloc[-1] = financialdf.eps.iloc[-1]
        
    priceearning_byyear['pe'] = priceearning_byyear['price']/priceearning_byyear['eps']
    # print(priceearning_byyear)
    # print('Min PE:', round(priceearning_byyear.pe.min(), 2))
    return [round(priceearning_byyear.pe.min(), 2), round(
        priceearning_byyear.pe.mean(), 2), round(priceearning_byyear.pe.max(), 
        2)]

def generate_decision_1 (ticker, financialdf, discountrate, marginrate,
                          stockpriceserie, parameters):
    lasteps = financialdf.EPS.iloc[-1]
    
    dfprice = pd.DataFrame(columns=['ticker', 'lasteps', 'futureeps']) 

    pd.options.display.float_format = '{:20,.2f}'.format
    # print('parameters', parameters)
    annualgrowthrate = float(parameters.annual_growth_rate)
    pe_ratio = float(parameters.pe)
    n_future_year = 5
    try:
        futureeps = abs(npf.fv(annualgrowthrate, n_future_year, 0, lasteps))
        # print('5.1', [ticker, lasteps, futureeps])
        dfprice.loc[0] = [ticker, lasteps, futureeps]
        # print('5.2')
    except:
        # print('Last EPS:', lasteps)
        # print('Annual Growth Rate:', annualgrowthrate)
        print('EPS does not exist or annual growth rate is missing.')
    dfprice.set_index('ticker', inplace=True)
    dfprice['pe'] = pe_ratio
    dfprice['FV'] = dfprice['futureeps'] * dfprice['pe']
    dfprice['PV'] = npf.pv(discountrate, n_future_year, 0, dfprice['FV']) * -1
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
    # discountrate = 0.1
    # marginrate = 0.1
    financial_df = calculate_ratio(get_financial_df(get_statement(ticker)))
    # stockprice_df = get_stock_price(ticker)
    stockprice_df = get_stock_price(ticker).Close
    result = growth_pe(ticker, stockprice_df, financial_df)
    print(result)

    # print(generate_futureprice(ticker, financial_df, discountrate, 
    #                                    marginrate, stockprice_df))
    # open_in_excel(generate_futureprice(ticker, financial_df, discountrate, 
    #                                   marginrate, stockprice_df))
    print(datetime.now() - start)