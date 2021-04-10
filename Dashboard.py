# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 20:17:37 2021

@author: Gunardilin
"""

# from pandas_datareader import data
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
# from datetime import datetime as dt

import pandas as pd
import numpy as np
from get_stock_price import get_stock_price
from sp500 import get_sp500_info, format_for_dashdropdown
from russel3000 import get_russel3000_info
from foreigncompanies import get_foreigncompanies_info
from get_statement import get_statement , open_in_excel
from get_financial_df import get_financial_df, calculate_ratio
from human_readable_format import readable_format, convert_percent

financial_df_table = pd.DataFrame({'Year':[], 'Shareholder Equity':[], 
                                   'Long-Term Debt':[], 'EPS':[],
                                   'EPS-Growth':[], 'Net Income': [],
                                   'ROA':[], 'Interest Expense':[],
                                   'EBITDA':[], 'ROE':[],
                                   'Interest Coverage Ratio': []})

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Stock Tickers'),
    html.H3('Choose a stock ticker:'),
    
    dcc.Dropdown(
        id='my-dropdown',
        # For testing purpose use the following options:
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
            ], value='AAPL'
        
        # For productive deployment use the following options:
        # options=format_for_dashdropdown(pd.concat([get_sp500_info(), 
        #                                           get_russel3000_info(),
        #                                           get_foreigncompanies_info()],
        #                                           ignore_index=True))
    ),
    
    dcc.Graph(id='my-graph', figure={}),
    
    #html.Table(id='financial_df')
    dash_table.DataTable(
        id='financial_df', 
        columns=[{"name": i, "id": i} for i in financial_df_table.columns],
        data=financial_df_table.to_dict('records')
        ),
    html.Br(),
    html.Br(),
    
    # dcc.Slider(
    # min=0,
    # max=10,
    # step=None,
    # marks={
    #     0: '0 °F',
    #     3: '3 °F',
    #     5: '5 °F',
    #     7.65: '7.65 °F',
    #     10: '10 °F'
    # },
    # value=5)
])

# For stock graph
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my-dropdown', component_property='value'))
def update_graph(dropdown_properties):
    df = get_stock_price(dropdown_properties)
    # print("**********", df)
    # print("**********", type(df))
    figure = go.Figure(data=[go.Scatter(x=df.index, y=df.Close, name=dropdown_properties)])
    return figure

# For financial_df table
@app.callback(
    Output(component_id='financial_df', component_property='data'),
    Input(component_id='my-dropdown', component_property='value'))
def generate_financial_df_table(stock_ticker, max_rows=10):
    #global financial_df_table
    financial_df_table = calculate_ratio(get_financial_df(get_statement
                                                          (stock_ticker)))
    # Formating the table output
    df_written = financial_df_table.reset_index()
    
    df_written[['shareholderequity', 'longtermdebt', 'netincome', 
                'interestexpense', 'ebitda']] = df_written[
                    ['shareholderequity', 'longtermdebt', 'netincome', 
                      'interestexpense', 'ebitda']].applymap(readable_format)            
                    
    df_written[['epsgrowth', 'roa', 'roe']] = df_written[
        ['epsgrowth', 'roa', 'roe']].applymap(convert_percent)
    df_written[['eps', 'interestcoverageratio']] = np.round(
        df_written[['eps', 'interestcoverageratio']], 2)
    
    df_written = df_written.rename(columns={
        'index':'Year', 'shareholderequity': 'Shareholder Equity', 
        'longtermdebt': 'Long-Term Debt', 'eps': 'EPS', 'epsgrowth': 
            'EPS-Growth', 'netincome': 'Net Income', 'roa': 'ROA', 
            'interestexpense': 'Interest Expense', 'ebitda': 'EBITDA',
            'roe': 'ROE', 'interestcoverageratio': 'Interest Coverage Ratio'})
    
    # table_header = [html.Tr([html.Th(col) for col in df_written.columns])]
    # # print(table_header)
    
    # table_body = [html.Tr([html.Td(df_written.iloc[i][col]) 
    #                         for col in df_written.columns]) 
    #               for i in range(min(len(df_written), max_rows))]
    # # print(table_body)
    
    # return table_header + table_body
    
    return df_written.to_dict('records')

if __name__ == '__main__':
    app.run_server()