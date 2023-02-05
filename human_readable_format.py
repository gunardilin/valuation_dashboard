# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 21:04:21 2021

@author: Gunardilin
"""

import math

millnames = ['',' Thousand',' Million',' Billion',' Trillion']

def readable_format(n):
    if str(n) == "nan":
        return 'NaN'
    else:
        n = float(n)
        millidx = max(0,min(len(millnames)-1,
                            int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    
        return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

def convert_percent(n):
    #print(n)
    if str(n) == "nan":
        return 'NaN'
    else:
        return '{:.2f}%'.format(float(n)*100)

if __name__ == '__main__':
    
    dec_list = ['0.1102', '0.234532', '-0.0037', '0.56']
    result = map(convert_percent, dec_list)
    print(list(result))