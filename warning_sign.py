# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 21:15:44 2021

@author: Gunardilin
"""

def warning_sign (ratio_df):
    warning_list = []
    
    # 1. criteria: epsgrowth < 0
    index_list = ratio_df.index[ratio_df.epsgrowth < 0].tolist()
    epsgrowth_list = ratio_df.epsgrowth[index_list].tolist()
    
    for i in range(len(index_list)):
        warning_list.append('EPS for year {}: {}'.format(index_list[i], 
                                                         epsgrowth_list[i]))
    
    # 2. criteria: ROE < 0.13
    roe_mean = ratio_df.roe.mean()
    if roe_mean < 0.13:
        warning_list.append('roe mean ({:.2f})is less than 0.13'.format(roe_mean))
    
    # 3. criteria: ROA < 0.07
    roa_mean = ratio_df.roa.mean()
    if roa_mean < 0.07:
        warning_list.append('roa mean ({:.2f})is less than 0.07'.format(roa_mean))
    
    # 4. criteria: long term debt < 5 * income
    ratio1 = ratio_df.longtermdebt / ratio_df.netincome
    ratio1index_list = ratio1.index[ratio1 > 5].tolist()
    for i in ratio1index_list:
        warning_list.append('longtermdebt/netincome for year {} ({:.2f}) > 5 times'.
                            format(i, ratio1[i]))
    
    # 5. criteria: Interest Coverage Ratio < 3
    interestcoverage_mean = ratio_df.interestcoverageratio.mean()
    if interestcoverage_mean < 3:
        warning_list.append('Mean interest coverage ratio ({:.2f}) is less than 3'
                            .format(interestcoverage_mean))
    
    return warning_list

if __name__ == '__main__':
    from get_statement import get_statement
    from get_financial_df import get_financial_df, calculate_ratio
    print(warning_sign(calculate_ratio(get_financial_df(get_statement('coke')))))