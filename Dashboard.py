# -*- coding: utf-8 -*-

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
from warning_sign import warning_sign
from future_value import generate_futureprice

financial_df_table = pd.DataFrame({'Year':[], 'Shareholder Equity':[], 
                                    'Long-Term Debt':[], 'Net Income': [],
                                    'EPS':[], 'EPS-Growth':[], 
                                    'EBITDA':[], 'ROA':[], 'ROE':[],
                                    'Interest Expense':[],
                                    'Interest Coverage Ratio': []})

warning_df_table = pd.DataFrame({'Warning': ['None']})

buy_sell_table = pd.DataFrame({'Company': [], 'Annual Growth Rate': [],
                               'Last EPS': [], 'EPS in 5 years': [],
                               'Min PE': [], 'FV': [], 'PV': [],
                               'Margin Price': [], 'Current Share Price': [],
                               'Buy/Sell': []})

stock_price_df = 0

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
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Kirkland Lake Gold', 'value': 'KL'},
            {'label': 'Schrodinger Inc.', 'value': 'SDGR'}
            ]#, value='AAPL'
        
        # For productive deployment use the following options:
        # options=format_for_dashdropdown(pd.concat([get_sp500_info(), 
        #                                           get_russel3000_info(),
        #                                           get_foreigncompanies_info()],
        #                                           ignore_index=True)) +
        # [{'label': 'Kirkland Lake Gold', 'value': 'KL'}, 
        # {'label': 'Schrodinger Inc.', 'value': 'SDGR'},
        # {'label': 'BYD Co. Ltd.', 'value': 'BYDDY'}]
    ),
    
    dcc.Graph(id='my-graph', figure={}),
    
    html.H3('Critical variables'),
    
    dash_table.DataTable(
        id='financial_df', 
        columns=[{"name": i, "id": i} for i in financial_df_table.columns],
        data=financial_df_table.to_dict('records'), 
        style_header={
            'backgroundColor': 'white', 
            'fontWeight': 'bold'
            }
        ),
    
    html.Br(),
    html.Hr(),
    # html.Br(),
    html.H3('Warnings:'),
    
    dash_table.DataTable(
        id='warning_df',
        columns=[{"name": i, "id": i} for i in warning_df_table.columns],
        data=warning_df_table.to_dict('records'),
        style_header={
            'backgroundColor': 'white', 
            'fontWeight': 'bold'
            },
        style_cell={
            'textAlign': 'left'
            },
        ), 
    
    html.Br(),
    html.Hr(),
    html.H3('[Assumption] Inflation over 5 years:'),
    
    dcc.Slider(
        id='inflation_slider',
        min=0,
        max=100,
        step=5,
        marks={i: '{}%'.format(i) for i in range(0, 100, 5)},
        value=15),
    
    html.Br(),
    # html.Hr(),
    html.H3('[Tolerance] Margin of Safety:'),
    
    dcc.Slider(
        id='margin_slider',
        min=0,
        max=100,
        step=5,
        marks={i: '{}%'.format(i) for i in range(0, 100, 5)},
        value=25),
    
    html.Br(),
    # html.Hr(),
    html.H3('Buy/Sell:'),
    
    dash_table.DataTable(
        id='buy_sell',
        columns=[{"name": i, "id": i} for i in buy_sell_table.columns],
        data=buy_sell_table.to_dict('records'),
        style_header={
            'backgroundColor': 'white', 
            'fontWeight': 'bold'
            },
        style_cell={
            'textAlign': 'left'
            },
        ),
    
    html.Br(),
    html.Hr()
])

# For stock graph 1
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='my-dropdown', component_property='value'),
    prevent_initial_call=True)
def update_graph(dropdown_properties):
    # print('1')
    global stock_price_df
    stock_price_df = get_stock_price(dropdown_properties)
    figure = go.Figure(data=[go.Scatter(x=stock_price_df.index, 
                                        y=stock_price_df.Close, 
                                        name=dropdown_properties)])
    # print('1 finish')
    return figure

# For financial_df table and warning_df_table 2
@app.callback(
    Output(component_id='financial_df', component_property='data'),
    Output(component_id='warning_df', component_property='data'),
    Input(component_id='my-dropdown', component_property='value'),
    prevent_initial_call=True)
def generate_financial_warning_df_table(stock_ticker, max_rows=10):
    # print('2')
    global financial_df_table
    financial_df_table = calculate_ratio(get_financial_df(get_statement
                                                          (stock_ticker)))
    # open_in_excel(financial_df_table)
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
    
    # Generate Warning_df_table
    warning_df_table = pd.DataFrame(warning_sign(financial_df_table), 
                                    columns=['Warning']).to_dict('records')
    # print('2 finish')
    return df_written.to_dict('records'), warning_df_table

# For buy_sell_table 3
@app.callback(
    Output(component_id='buy_sell', component_property='data'),
    Input(component_id='inflation_slider', component_property='value'),
    Input(component_id='margin_slider', component_property='value'),
    Input(component_id='my-dropdown', component_property='value'),
    Input(component_id='financial_df', component_property='data'),
    prevent_initial_call=True)
def generate_decision(inflation, margin, ticker, start):
    # print('3')
    global buy_sell_table
    futureprice_df = generate_futureprice(ticker, financial_df_table, 
                                          inflation/100, margin/100, 
                                          stock_price_df).reset_index()
    buy_sell_table = futureprice_df.rename(columns={
        'ticker': 'Company', 'annualgrowthrate': 'Annual Growth Rate',
        'lasteps': 'Last EPS', 'futureeps': 'EPS in 5 years', 
        'min_pe': 'Min PE', 'marginprice': 'Margin Price',
        'currentshareprice': 'Current Share Price', 'decision': 'Buy/Sell'
        })
    buy_sell_table[['Annual Growth Rate']] = buy_sell_table[['Annual Growth Rate']].applymap(convert_percent)
    buy_sell_table[['Last EPS', 'EPS in 5 years', 'Min PE', 'FV', 'PV', 
                    'Margin Price', 'Current Share Price']] = np.round(
                        buy_sell_table[['Last EPS', 'EPS in 5 years', 'Min PE', 
                                        'FV', 'PV', 'Margin Price', 
                                        'Current Share Price']], 2)
    buy_sell_table_written = buy_sell_table.to_dict('records')
    # print('3 finish')
    return buy_sell_table_written
                        
if __name__ == '__main__':
    app.run_server()