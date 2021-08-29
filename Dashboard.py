# -*- coding: utf-8 -*-

# from pandas_datareader import data
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
# from datetime import datetime as dt

import pandas as pd
import numpy as np
from get_stock_price import get_stocks_price
from sp500 import get_sp500_info, format_for_dashdropdown
from russel3000 import get_russel3000_info
from foreigncompanies import get_foreigncompanies_info
from get_statement import get_statement , open_in_excel
from get_financial_df import get_financial_df, calculate_ratio
from human_readable_format import readable_format, convert_percent
from warning_sign import warning_sign
from future_value import generate_futureprice

financial_df_table = pd.DataFrame({'Company':[], 'Year':[], 
                                    'Shareholder Equity':[], 
                                    'Long-Term Debt':[], 'Net Income': [],
                                    'EPS':[], 'EPS-Growth':[], 
                                    'EBITDA':[], 'ROA':[], 'ROE':[],
                                    'Interest Expense':[],
                                    'Interest Coverage Ratio': []})

# warning_df_table is not necessary to be stored clientside, since no following
# callback needs input from it.
warning_df_table = pd.DataFrame({'Company': ['None'], 'Warning': ['None']})

# buy_sell_table might not need to be stored clientside, cos it will not be 
# accessed by other callback.
buy_sell_table = pd.DataFrame({'Company': [], 'Annual Growth Rate': [],
                               'Last EPS': [], 'EPS in 10 years': [],
                               'PE': [], 'Future Value': [],
                               'Present Value': [], 'Margin Price': [], 
                               'Current Share Price': [],'Buy/Sell': []})

stock_price_df = 0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H1('Company valuation'),
    html.H3('Choose stock tickers:'),
    
    dcc.Dropdown(
        id='my-dropdown',
        # For testing purpose use the following options:
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Kirkland Lake Gold', 'value': 'KL'},
            {'label': 'Schrodinger Inc.', 'value': 'SDGR'}
            ],
            multi = True,
            # value='AAPL',
        
        # For productive deployment use the following options:
        # options=format_for_dashdropdown(pd.concat([get_sp500_info(), 
        #                                           get_russel3000_info(),
        #                                           get_foreigncompanies_info()],
        #                                           ignore_index=True)) +
        # [{'label': 'Kirkland Lake Gold', 'value': 'KL'}, 
        # {'label': 'Schrodinger Inc.', 'value': 'SDGR'},
        # {'label': 'BYD Co. Ltd.', 'value': 'BYDDY'}, 
        # {'label': 'Tencent Holdings Limited', 'value': 'TCEHY'}],
        # multi=True
    ),
    html.Div([
        html.H3('Graph time horizon:', 
        style={'width': '49%', 'display': 'inline-block'}),
        html.H3('Graph mode:',
        style={'width': '49%', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        dcc.RadioItems(
            id='view-periode',
            options=[
                {'label': '1M', 'value': '1M'},
                {'label': '3M', 'value': '3M'},
                {'label': '6M', 'value': '6M'},
                {'label': 'YTD', 'value': 'YTD'},
                {'label': '1Y', 'value': '1Y'},
                {'label': '2Y', 'value': '2Y'},
                {'label': '3Y', 'value': '3Y'},
                {'label': '4Y', 'value': '4Y'},
                {'label': 'All', 'value': 'All'},
            ],
            value='All',
            labelStyle={'display': 'inline-block'},
            style={'width': '49%', 'display': 'inline-block'},
        ),
        dcc.RadioItems(
            id='view-mode',
            options=[
                {'label': '$', 'value': '$'},
                {'label': '%', 'value': '%'},
            ],
            value='%',
            labelStyle={'display': 'inline-block'},
            style={'width': '49%', 'display': 'inline-block'},
        ),
        ]),
    
    dcc.Graph(id='my-graph', figure={}),
    
    html.H3('Critical variables'),
    
    dash_table.DataTable(
        id='financial_df', 
        columns=[{"name": i, "id": i} for i in financial_df_table.columns],
        data=financial_df_table.to_dict('records'), 
        style_header={
            'backgroundColor': 'white', 
            'fontWeight': 'bold'
            },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{EPS} <= 0',
                    'column_id': 'EPS'
                        },
                'backgroundColor': '#FF4136',
                'color': 'white'
                },
            
            {
                'if': {
                    'filter_query': '{Net Income} contains "-"',
                    'column_id': 'Net Income',
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
                },
            {
                'if': {
                    'filter_query': '{EPS-Growth} contains "-"',
                    'column_id': 'EPS-Growth'
                        },
                'backgroundColor': '#FF4136',
                'color': 'white'
                },   
            ],
        # tooltip_header={
        #     i: i for i in financial_df_table.columns
        #     'EPS': 'Earning per Share'
        #     }, 
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
    html.H3('[Assumption] Inflation over next 10 years:'),
    
    dcc.Slider(
        id='inflation_slider',
        min=0,
        max=100,
        step=5,
        marks={i: '{}%'.format(i) for i in range(0, 100, 5)},
        value=20),
    
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
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Buy/Sell} contains "Buy"',
                    'column_id': 'Buy/Sell',
                },
                'backgroundColor': '#3D9970',
                'color': 'white'
                },
            {
                'if': {
                    'filter_query': '{Buy/Sell} contains "Sell"',
                    'column_id': 'Buy/Sell'
                        },
                'backgroundColor': '#FF4136',
                'color': 'white'
                },
            {
                'if': {
                    'filter_query': '{PE} >= 25',
                    'column_id': 'PE'
                        },
                'backgroundColor': '#ffbf00',
                'color': 'black'
                },
            {
                'if': {
                    'filter_query': '{PE} <= 0',
                    'column_id': 'PE'
                        },
                'backgroundColor': '#FF4136',
                'color': 'white'
                },
            
            ],
            tooltip_data=[
                {
                    'PE': 'Minimum PE'
                },
                {
                    'PE': 'Maximum PE'
                },
                {
                    'PE': 'Mean PE'
                },
            ],
            tooltip_header={
                # i: i for i in buy_sell_table.columns
               'PE': 'Price Earning Ratio'
                },
            # tooltip_delay=0,
            # tooltip_duration=2
        ),
    
    html.Br(),
    html.Hr(),
    dcc.Store(id='stock_price_df_clientside', data=[]),
    dcc.Store(id='financial_df_table_clientside', data=[]),
])

# For stock graph 1
@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Output(component_id='stock_price_df_clientside', component_property='data'),
    Input(component_id='my-dropdown', component_property='value'),
    prevent_initial_call=True)
def update_graph(tickers):
    if len(tickers) != 0:
        # print('1')
        stock_price_df = get_stocks_price(tickers)
        df_normalized = stock_price_df.div(stock_price_df.iloc[0]).reset_index()
        figure = px.line(df_normalized, x="Date", y=tickers, hover_data={
            "Date": "| %d %B %Y"}, title='Stocks Price',
            )
        figure.update_layout(hovermode='x')
        figure.update_xaxes(
            rangeslider_visible = True,
            rangeselector = dict(buttons = list([
                dict(count=1, label='1M', step='month', stepmode='backward'),
                dict(count=3, label='3M', step='month', stepmode='backward'),
                dict(count=6, label='6M', step='month', stepmode='backward'),
                dict(count=1, label='YTD', step='year', stepmode='todate'),
                dict(count=1, label='1Y', step='year', stepmode='backward'),
                dict(count=2, label='2Y', step='year', stepmode='backward'),
                dict(count=3, label='3Y', step='year', stepmode='backward'),
                dict(count=4, label='4Y', step='year', stepmode='backward'),
                dict(step='all')
            ]))
        )
        # print('1 finish')
        return figure, stock_price_df.reset_index().to_dict('records')
    else:
        return [], []

# For financial_df table and warning_df_table 2
def company_ratio (ticker):
    # Generate Critical-Variable_df
    df_ratio = calculate_ratio(get_financial_df(get_statement(ticker)))
    # Generate Warning_df
    df_warning = pd.DataFrame(warning_sign(df_ratio), 
                                columns=['Warning'])
    df_ratio['Company'] = ticker
    df_warning['Company'] = ticker
    return df_ratio, df_warning

@app.callback(
    Output(component_id='financial_df', component_property='data'),
    Output(component_id='warning_df', component_property='data'),
    Output(component_id='financial_df_table_clientside', component_property='data'),
    Input(component_id='my-dropdown', component_property='value'),
    # Input(component_id='stock_price_df_clientside', component_property='data'),
    prevent_initial_call=True)
def generate_financial_warning_df_table(stock_tickers):
    if len(stock_tickers) != 0:
        # print('2')
        # financial_df_table = calculate_ratio(get_financial_df(get_statement
        #                                                       (stock_ticker)))
        # company_ratio = lambda ticker: calculate_ratio(get_financial_df(
        #     get_statement(ticker)))
        financial_df_table = pd.DataFrame({})
        warning_df_table = pd.DataFrame({})
        for i in stock_tickers:
            new_content = company_ratio(i)
            financial_df_table = pd.concat([financial_df_table, new_content[0]])
            warning_df_table = pd.concat([warning_df_table, new_content[1]])
        
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
        # warning_df_table = pd.DataFrame(warning_sign(financial_df_table), 
        #                                 columns=['Warning'])
        # warning_df_table['Company'] = stock_ticker
        # print('2 finish')
        return df_written.to_dict('records'), warning_df_table.to_dict('records'), \
            financial_df_table.reset_index().to_dict('records')
    else:
        return [], [], []

# For buy_sell_table 3
@app.callback(
    Output(component_id='buy_sell', component_property='data'),
    Input(component_id='inflation_slider', component_property='value'),
    Input(component_id='margin_slider', component_property='value'),
    Input(component_id='my-dropdown', component_property='value'),
    Input(component_id='financial_df', component_property='data'), # Start signal no. 1
    Input(component_id='stock_price_df_clientside', component_property='data'), # Also necessary as start signal no. 2
    State(component_id='financial_df_table_clientside', component_property='data'),
    prevent_initial_call=True)
def generate_decision(inflation, margin, tickers, start1, stock_price_df_clientside,
                      financial_df_clientside):
    if len(tickers) != 0:
        # print('3')
        # Formating stock_price_df_clientside
        stock_price = pd.DataFrame.from_records(stock_price_df_clientside, \
            index='Date')
        stock_price.index = pd.to_datetime(stock_price.index)
        # print('*** Ticker:', ticker)
        # print('*** Inflation in 10 Y:', inflation)
        # print('*** Margin of Safety:', margin)
        # print('*** Stock price:', stock_price.tail())
        
        # Formating financial_df_clientside
        financial_df = pd.DataFrame.from_records(financial_df_clientside, \
            index='index')
        # print('*** Financial DF:\n', financial_df.tail())
        futureprice_df = pd.DataFrame({})
        for ticker in tickers:
            # print(financial_df[financial_df['Ticker'] == ticker])
            futureprice_df = pd.concat([futureprice_df, generate_futureprice(
                                        ticker, 
                                        financial_df[financial_df['Company'] == ticker], 
                                        inflation/100, margin/100, 
                                        stock_price[ticker])])
            # print(futureprice_df)
            # print(futureprice_df.pe)
        futureprice_df.reset_index(inplace=True)
        # print(futureprice_df)
        buy_sell_table = futureprice_df.rename(columns={
            'ticker': 'Company', 'annualgrowthrate': 'Annual Growth Rate',
            'lasteps': 'Last EPS', 'futureeps': 'EPS in 10 years', 
            'pe': 'PE', 'marginprice': 'Margin Price',
            'currentshareprice': 'Current Share Price', 'decision': 'Buy/Sell',
            'PV': 'Present Value', 'FV': 'Future Value'
            })
        buy_sell_table[['Annual Growth Rate']] = buy_sell_table[[
            'Annual Growth Rate']].applymap(convert_percent)
        buy_sell_table[['Last EPS', 'EPS in 10 years', 'PE', 
                        'Future Value', 'Present Value', 
                        'Margin Price', 'Current Share Price']] = np.round(
                            buy_sell_table[['Last EPS', 'EPS in 10 years', 
                                            'PE', 
                                            'Future Value', 'Present Value', 
                                            'Margin Price', 
                                            'Current Share Price']], 2)
        buy_sell_table_written = buy_sell_table.to_dict('records')
        # print('3 finish')
        return buy_sell_table_written
    else:
        return []
                        
if __name__ == '__main__':
    app.run_server(debug=False)
    