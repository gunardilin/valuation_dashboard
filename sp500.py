#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: Sunday, February 28th 2021, 3:32:50 pm
# Author: Gunardi Ali
# -----
import pandas as pd
from get_statement import open_in_excel

def get_sp500_info():
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df2 = df[0][['Symbol', 'Security', 'GICS Sector']]
    return df2
    
def format_for_dashdropdown(pddataframe):
    return [{'label': "{}, {}, {}".format(pddataframe.iloc[i].Symbol, 
                                          pddataframe.iloc[i].Security, 
                                          pddataframe.iloc[i]['GICS Sector']), 
             'value': pddataframe.iloc[i].Symbol} 
            for i in range(len(pddataframe.index))]

if __name__ == "__main__":
    open_in_excel(get_sp500_info())
    # print(format_for_dashdropdown(get_sp500_info()))