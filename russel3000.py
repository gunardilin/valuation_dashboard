#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: Tuesday, March 2nd 2021, 7:18:39 pm
# Author: Gunardi Ali
# -----

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

def get_russel_microcap_info():
    url = "https://www.ishares.com/us/products/239716/ishares-microcap-etf/1467271812596.ajax?tab=all&fileType=json"
    r = requests.get(url)
    json = loads(r.content.decode('utf-8-sig'))
    df = pd.DataFrame(json['aaData'])
    df2 = df.iloc[:, [0, 1, 2]]
    df2.columns = ['Symbol', 'Security', 'GICS Sector']
    return df2

if __name__ == "__main__":
    open_in_excel(get_russel_microcap_info())