# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 10:49:02 2021

@author: Gunardilin
"""

def append_txt (itterable, filename):
    with open(filename +'.txt', 'a') as file:
        file.writelines('\n'.join(itterable))
    pass

if __name__ == '__main__':
    append_txt(['abc', 'cde'], "test")