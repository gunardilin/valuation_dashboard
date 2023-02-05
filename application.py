# -*- coding: utf-8 -*-

import flask
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash_table import FormatTemplate
from dash import dash_table

import pandas as pd
import numpy as np
from get_stock_price import get_stocks_price
from get_all_tickers import get_companies_from_sec, format_for_dashdropdown
from get_statement import get_statement
from get_financial_df import get_financial_df, calculate_ratio
from human_readable_format import readable_format, convert_percent
from warning_sign import warning_sign
from future_value import generate_decision_1, growth_pe 

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

percentage = FormatTemplate.percentage(2)

# buy_sell_table might not need to be stored clientside, cos it will not be 
# accessed by other callback.

buy_sell_table_1 = pd.DataFrame({'Company': [],
                               'Last EPS': [], 'EPS in 5 years': [],
                               'Future Value': [],
                               'Present Value': [], 'Margin Price': [], 
                               'Current Share Price': [],'Buy/Sell': []})

stock_price_df = 0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
application = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

application.layout = html.Div([
    html.H1('Company valuation', 
        style={
            'textAlign': 'center'
            }
        ),
    html.H3('Choose stock tickers:'),
    
    dcc.Dropdown(
        id='my-dropdown',
        # For testing purpose use the following options:
        # options=[
        #     {'label': 'Coke', 'value': 'COKE'},
        #     {'label': 'Tesla', 'value': 'TSLA'},
        #     {'label': 'Apple', 'value': 'AAPL'},
        #     {'label': 'Kirkland Lake Gold', 'value': 'KL'},
        #     {'label': 'Schrodinger Inc.', 'value': 'SDGR'},
        #     {'label': 'Coupang', 'value': 'CPNG'},
        #     {'label': 'Facebook', 'value': 'FB'},
        #     {'label': 'Tencent Holdings Limited', 'value': 'TCEHY'}
        #     ],
        #     multi = True,
            # value='AAPL',

        # options=format_for_dashdropdown(pd.concat([ get_sp500_info(), 
        #                                             get_russel3000_info(),
        #                                             get_foreigncompanies_info(),
        #                                             get_russel_microcap_info()],
        #                                             ignore_index=True)) +
        # [{'label': 'Kirkland Lake Gold', 'value': 'KL'}, 
        # {'label': 'Schrodinger Inc.', 'value': 'SDGR'},
        # {'label': 'BYD Co. Ltd.', 'value': 'BYDDY'}, 
        # {'label': 'Tencent Holdings Limited', 'value': 'TCEHY'}],
        # multi=True,

    #     placeholder="You can select multiple companies",
    # ),
        
        # For productive deployment use the following options:
        options=format_for_dashdropdown(get_companies_from_sec()) + [\
            {'label': 'BYD Co. Ltd.', 'value': 'BYDDY'}, 
            {'label': 'Tencent Holdings Limited', 'value': 'TCEHY'}
            ],
        multi=True, 
        placeholder="You can select multiple companies"
    ),
    html.Br(),
    
    dcc.Loading(
        id='loading-1', type='default',
        children = dcc.Graph(id='my-graph', figure={})
    ),
    
    html.Div([
        html.H3('[X-Axis] Graph time horizon:', 
        style={'width': '49%', 'display': 'inline-block'}),
        html.H3('[Y-Axis] Graph mode:',
        style={'width': '49%', 'display': 'inline-block'})
    ]),
    
    html.Div([
        dcc.RadioItems(
            id='view-periode',
            options=[
                {'label': '1M', 'value': '30D'},
                {'label': '3M', 'value': '90D'},
                {'label': '6M', 'value': '180D'},
                {'label': 'YTD', 'value': '1Y'},
                {'label': '1Y', 'value': '365D'},
                {'label': '2Y', 'value': '730D'},
                {'label': '3Y', 'value': '1095D'},
                {'label': '4Y', 'value': '1460D'},
                {'label': 'All', 'value': 'All'}
            ],
            value='All',
            labelStyle={'display': 'inline-block'},
            style={'width': '49%', 'display': 'inline-block'}
        ),
        dcc.RadioItems(
            id='view-mode',
            options=[
                {'label': '$', 'value': '$'},
                {'label': '%', 'value': '%'}
            ],
            value='%',
            labelStyle={'display': 'inline-block'},
            style={'width': '49%', 'display': 'inline-block'}
        )
        ]),
    
    html.Br(),
    html.Hr(),

    html.H3('Critical variables'),
    
    dcc.Loading(
        id='loading-2', type='default',
        children = 
            dash_table.DataTable(
                id='financial_df', 
                columns=[{"name": i, "id": i} for i in financial_df_table.columns],
                data=financial_df_table.to_dict('records'), 
                style_header={
                    'backgroundColor': 'white', 
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                    },
                style_header_conditional=[{
                    'if': {'column_id': col},
                        'textDecoration': 'underline',
                        'textDecorationStyle': 'dotted',
                        } for col in ['ROA', 'ROE', 'Interest Coverage Ratio']
                    ],
                tooltip_header={
                        'ROA': 'Return on Assets: Net Income/Total Assets',
                        'ROE': 'Return on Equity: Net Income/Shareholder Equity',
                        'Interest Coverage Ratio': 'EBITDA/Interest Expense'
                    },
                tooltip_delay=0,
                tooltip_duration=None,
                style_cell={
                    'textAlign': 'left'
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
                        }   
                    ],
                    # fill_width=False,
                # tooltip_header={
                #     i: i for i in financial_df_table.columns
                #     'EPS': 'Earning per Share'
                #     }, 
                )
        # fullscreen=True
    ),
    
    html.Br(),
    html.Hr(),
    # html.Br(),
    html.H3('Warnings:'),
    
    dcc.Loading(
        id='loading-3', type='default',
        children = 
            dash_table.DataTable(
                id='warning_df',
                columns=[{"name": i, "id": i} for i in warning_df_table.columns],
                data=warning_df_table.to_dict('records'),
                style_header={
                    'backgroundColor': 'white', 
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                    },
                style_cell={
                    'textAlign': 'left'
                    },
                fill_width=False
                ) 
        # fullscreen=True
    ),
    
    html.Br(),
    html.Hr(),

    html.Div([
        html.H3('[Assumption] Inflation per year:', 
            style = {'width': '49%', 'display': 'inline-block', 
                'text-align': 'center'}),
            # ‘align-items’: ‘center’, ‘justify-content’: ‘center’
        html.H3('[Tolerance] Margin of Safety:', 
            style={'width': '49%', 'display': 'inline-block',
                'text-align': 'center'})
    ]),
    html.Br(),

    html.Div([
        html.Div(
            dcc.Slider(
                id='inflation_slider',
                min=-4,
                max=8,
                step=0.5,
                marks={i: '{}%'.format(i) for i in range(-4, 9, 1)},
                value=2),
            style={'width': '49%', 'display': 'inline-block'}
        ),
        html.Div(
            dcc.Slider(
                id='margin_slider',
                min=0,
                max=50,
                step=5,
                marks={i: '{}%'.format(i) for i in range(0, 55, 10)},
                value=25),
            style={'width': '49%', 'display': 'inline-block'}
        )
    ]),
    
    html.Br(),

    html.H3('[Parameters] Annual Growth Rate, PE:'),
    html.H6('Entries under "Annual Growth Rate" and "PE" columns can be modified.'),
    dcc.Loading(
        id='loading-4', type='default',
        children = 
            dash_table.DataTable(
                id='growth_pe',
                # columns=[{'name': i, 'id': i} for i in growth_pe_table.columns],
                columns = [
                    dict(id='company', name='Company'),
                    dict(id='historical_growth_rate', 
                        name='Historical EPS Growth Rate\n (min, mean or annualized, max)'),
                    dict(id='historical_pe',
                        name='Historical PE\n (min, mean, max)'),
                    dict(id='annual_growth_rate',
                        name='Annual EPS Growth Rate\n %', type='numeric', 
                        format=percentage, editable=True),
                    dict(id='pe', name='PE', editable=True)
                ],
                data= [],
                style_header={
                    'backgroundColor': 'white', 'fontWeight': 'bold',
                    'textAlign': 'center'},
                style_header_conditional=[
                    {
                    'if': {'column_id': 'historical_growth_rate'},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    },
                    {
                    'if': {'column_id':'annual_growth_rate'},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    "backgroundColor": "rgb(250, 0, 0, 0.25)"
                    },
                    {
                    'if': {'column_id':'pe'},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    "backgroundColor": "rgb(250, 0, 0, 0.25)"
                    },
                        ],
                tooltip_header={
                        'historical_growth_rate': 'If (1 + EPS Growth Rate) > 0\
                             -> Annualized growth rate, if < 0 -> Mean value',
                        'annual_growth_rate': {
                            'value': 'This column is editable. \n\n For 12.7% \
                            Growth Rate, enter: 0.127\n\n![edit]({})'.format(
                                application.get_relative_path('/assets/images/Edit_Icon.jpg')),
                                'type': 'markdown'},
                        'pe': {
                            'value': 'This column is editable.\n\n![edit]({})'.format(\
                                application.get_relative_path('/assets/images/Edit_Icon.jpg')),
                            'type': 'markdown'}
                    },
                tooltip_delay=0,
                tooltip_duration=None,
                style_cell={
                    'whiteSpace': 'pre-line',
                    'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{pe} >= 25',
                            'column_id': 'pe'
                                },
                        'backgroundColor': '#ffbf00',
                        'color': 'black'
                        },
                    {
                        'if': {
                            'filter_query': '{pe} <= 0',
                            'column_id': 'pe'
                                },
                        'backgroundColor': '#FF4136',
                        'color': 'white'
                        },
                    {
                        'if': {
                            'filter_query': '{annual_growth_rate} <= 0',
                            'column_id': 'annual_growth_rate'
                                },
                        'backgroundColor': '#FF4136',
                        'color': 'white'
                        }
                    ],

                tooltip={
                        'annual_growth_rate': {
                            'value': 'This column is editable. \n\n For 12.7% \
                            Growth Rate, enter: 0.127\n\n![edit]({})'.format(
                                application.get_relative_path('/assets/images/Edit_Icon.jpg')),
                                'type': 'markdown'},
                        'pe': {
                            'value': 'This column is editable.\n\n![edit]({})'.format(\
                                application.get_relative_path('/assets/images/Edit_Icon.jpg')),
                            'type': 'markdown'}
                        },
                    
                #     fill_width=False,

            )
    ),

    html.Br(),
    html.Hr(),
    html.H3('Intrinsic value based on EPS:'),

    dcc.Loading(
        id='loading-6', type='default',
        children = 
            dash_table.DataTable(
                id='buy_sell_1',
                columns=[{"name": i, "id": i} for i in buy_sell_table_1.columns],
                data=buy_sell_table_1.to_dict('records'),
                style_header={
                    'backgroundColor': 'white', 
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                    },
                style_header_conditional=[{
                    'if': {'column_id': col},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    } for col in ['EPS in 5 years', 'Future Value', 
                                    'Present Value', 'Margin Price', 
                                    'Buy/Sell']],
                tooltip_header={
                        'EPS in 5 years': 'Last EPS * (1 + Annual Growth Rate)^5.\
                            If 1 + Annual Growth Rate < 0, it will get 0.',
                        'Future Value': 'EPS in 5 years * PE',
                        'Present Value': 'The present value is computed by \
                            solving the equation: future value = present value\
                            * (1 + Inflation per year)^5 years',
                        'Margin Price': 'If EPS in 5 years > 0, Margin Price: \
                            Present Value * (1 - Margin of Safety), \
                            otherwise: 0',
                        'Buy/Sell': 'If Current Share Price < Margin Price: Buy\
                            otherwise: Sell'
                },
                tooltip_delay=0,
                tooltip_duration=None,
                style_cell={
                    'textAlign': 'left'
                    },
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Buy/Sell} contains "Buy"',
                            'column_id': 'Buy/Sell'
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
                    
                    ],
                ),
    ),
    
    
    html.Br(),
    html.Hr(),
    dcc.Store(id='stock_price_df_clientside', data=[]),
    dcc.Store(id='financial_df_table_clientside', data=[])
])

# For stock_price_df_clientside 0
@application.callback(
    Output(component_id='stock_price_df_clientside', component_property='data'),
    Input(component_id='my-dropdown', component_property='value'),
    prevent_initial_call=True)
def update_stock_price_df_clientside(tickers):
    print('0 Start', tickers)
    try:
        if len(tickers) != 0:
            stock_price_df = get_stocks_price(tickers)
            # Change ticker format to be compatible with Marketwatch by
            # replacing "-" with "." E.g. BRK-B -> BRK.B
            newTickers = []
            for i in tickers:
                newTickers.append(i.replace("-", "."))
            if len(tickers) == 1:
                stock_price_df.name = newTickers[0]
            else:
                stock_price_df.columns = newTickers
            return stock_price_df.reset_index().to_dict('records')
        else:
            return []
    except TypeError: # To catch object Nonetype -> TypeError
        return []
    finally:
        print('0 Finish', tickers)

# For stock graph 1
@application.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='stock_price_df_clientside', component_property='data'),
    Input(component_id='view-periode', component_property='value'),
    Input(component_id='view-mode', component_property='value'),
    prevent_initial_call=True)
def update_graph(stock_price_df_clientside, periode, mode):
    print('1 Start')
    if len(stock_price_df_clientside) != 0:
        # Don't execute if df_clientside is empty.
        stock_price_df = pd.DataFrame.from_records(stock_price_df_clientside, \
            index='Date')
        stock_price_df.index = pd.to_datetime(stock_price_df.index)

        if periode == 'All':
            stock_price_in_periode = stock_price_df
        else:
            stock_price_in_periode = stock_price_df.last(periode)

        if mode == '%':
            # a. Normalize stock price to start periode
            # print('1%')
            graph_data_df = stock_price_in_periode.div(stock_price_in_periode.\
                iloc[0]).reset_index()
        else:
            # b. Do not normalize stock price
            # print('1$')
            graph_data_df = stock_price_in_periode.reset_index()
        
        figure = px.line(graph_data_df, x="Date", y=graph_data_df.columns, 
                        hover_data={"Date": "| %d %B %Y"}, title='Stocks Price',
            )
        figure.update_layout(hovermode='x')
        figure.update_xaxes(
            rangeslider_visible = True)

        if periode=='All':
            figure.update_xaxes(
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
        elif periode=='1460D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(count=2, label='2Y', step='year', stepmode='backward'),
                    dict(count=3, label='3Y', step='year', stepmode='backward'),
                    dict(step='all')
                ]))
            )
        elif periode=='1095D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(count=2, label='2Y', step='year', stepmode='backward'),
                    dict(step='all')
                ]))
            )
        elif periode=='730D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(step='all')
                ]))
            )
        elif periode=='365D' or periode=='1Y':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(step='all')
                ]))
            )
        elif periode=='180D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(step='all')
                ]))
            )
        elif periode=='90D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(step='all')
                ]))
            )
        elif periode=='30D':
            figure.update_xaxes(
                rangeselector = dict(buttons = list([
                    dict(step='all')
                ]))
            )
        print('1 finish')
        return figure#, stock_price_df.reset_index().to_dict('records')
    else:
        print('1 finish')
        return {}

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

@application.callback(
    Output(component_id='financial_df', component_property='data'),
    Output(component_id='warning_df', component_property='data'),
    Output(component_id='financial_df_table_clientside', component_property='data'),
    Input(component_id='stock_price_df_clientside', component_property='data'),
    State(component_id='my-dropdown', component_property='value'),
    prevent_initial_call=True)
def generate_financial_warning_df_table(startsignal, stock_tickers):
    print('2 Start')
    try:
        if len(stock_tickers) != 0:
            # Change ticker format to be compatible with Marketwatch by
            # replacing "-" with "." E.g. BRK-B -> BRK.B
            newTickers = []
            for i in stock_tickers:
                newTickers.append(i.replace("-", "."))
            stock_tickers = newTickers
    
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
            df_written.sort_values(by=['Company', 'Year'], inplace=True)
            print('2 finish')
            return df_written.to_dict('records'), warning_df_table.to_dict('records'), \
                financial_df_table.reset_index().to_dict('records')
        else:
            print('2 finish')
            return [], [], []
    except TypeError: # To catch object Nonetype -> TypeError
        print('2 finish')
        return [], [], []

# # For growth_pe table 3
@application.callback(
    Output(component_id='growth_pe', component_property='data'),
    Input(component_id='stock_price_df_clientside', component_property='data'),
    Input(component_id='financial_df_table_clientside', component_property='data'),
    prevent_initial_call=True)
def show_parameters(stock_price_df_clientside, financial_df_clientside):
    print('3 Start')
    if len(stock_price_df_clientside) == 0 or len(financial_df_clientside) == 0:
        print('3A Finish')
        print('3A', len(stock_price_df_clientside))
        print('3A', len(financial_df_clientside))
        return []
    else:
        growth_pe_table = pd.DataFrame(columns=['ticker', 'historic_growthrate',
                                                'historic_pe', 'growthrate', 
                                                'pe'])
        pd.options.display.float_format = '{:20,.2f}'.format

        # Preprocessing clientside-dfs for further process
        stock_price = pd.DataFrame.from_records(stock_price_df_clientside, index="Date")
        stock_price.index = pd.to_datetime(stock_price.index)
        financial_df = pd.DataFrame.from_records(financial_df_clientside, \
            index='index')
        
        # Checking if the financial_df and stock_price df are up to date by
        # comparing with the dropdown value.
        if list(financial_df.Company.unique()) != list(stock_price.columns):
            print('3B Finish')
            return []
        else:
            for i, ticker in enumerate(stock_price.columns):
                # print(stock_price[ticker].head())
                growth_pe_dict = growth_pe(stock_price[ticker], \
                                financial_df[financial_df['Company'] == ticker])
                historic_growthrate_str = ", ".join(map(convert_percent, \
                                                    [growth_pe_dict['growth_min'], 
                                                    growth_pe_dict['growth_mean'],
                                                    growth_pe_dict['growth_max']]))
                
                historic_pe_str = ", ".join([str(growth_pe_dict['pe_min']), 
                                            str(growth_pe_dict['pe_mean']), 
                                            str(growth_pe_dict['pe_max'])])
                # growth_pe_table.loc[i] = [ticker, historic_growthrate_str, 
                #                             historic_pe_str, 
                #                             convert_percent(growth_pe_dict[\
                #                                 'growth_mean']).replace('%', ''),
                #                             growth_pe_dict['pe_mean']]
                growth_pe_table.loc[i] = [ticker, historic_growthrate_str, 
                                            historic_pe_str, 
                                            growth_pe_dict['growth_mean'],
                                            growth_pe_dict['pe_mean']]
            
            print('3C Finish')#, list(growth_pe_table.ticker))

            return growth_pe_table.rename(columns={
                'ticker': 'company', 
                'historic_growthrate': 'historical_growth_rate',
                'historic_pe': 'historical_pe',
                'growthrate': 'annual_growth_rate'
            }).to_dict('records')

# For buy_sell_table_1 5
@application.callback(
    Output(component_id='buy_sell_1', component_property='data'),
    Input(component_id='inflation_slider', component_property='value'),
    Input(component_id='margin_slider', component_property='value'),
    Input(component_id='my-dropdown', component_property='value'),
    Input(component_id='financial_df', component_property='data'),
    Input(component_id='stock_price_df_clientside', component_property='data'),
    Input(component_id='growth_pe', component_property='data'),
    prevent_initial_call=True
)
def buy_sell_decision(inflation, margin, tickers, financial_records, 
                    stock_price_df_clientside, parameter):
    print('5 Start')
    if len(tickers) != 0:
        # Change ticker format to be compatible with Marketwatch by
        # replacing "-" with "." E.g. BRK-B -> BRK.B
        newTickers = []
        for i in tickers:
            newTickers.append(i.replace("-", "."))
        tickers = newTickers

        stock_price = pd.DataFrame.from_records(stock_price_df_clientside, \
            index='Date')
        stock_price.index = pd.to_datetime(stock_price.index)
        financial_df = pd.DataFrame.from_records(financial_records)
        parameter_df = pd.DataFrame.from_records(parameter, index='company')
        decision_df = pd.DataFrame({})
        for ticker in tickers:
            decision_df = pd.concat([decision_df, generate_decision_1(
                                        ticker, 
                                        financial_df[financial_df['Company'] == ticker], 
                                        inflation/100, margin/100, 
                                        stock_price[ticker], 
                                        parameter_df.loc[ticker])])
        decision_df.reset_index(inplace=True)
        # print('decision_df', decision_df)
        decision_table_1 = decision_df.rename(columns={
            'ticker': 'Company', 
            'lasteps': 'Last EPS', 'futureeps': 'EPS in 5 years', 
            'FV': 'Future Value', 
            'PV': 'Present Value', 'marginprice': 'Margin Price',
            'currentshareprice': 'Current Share Price', 'decision': 'Buy/Sell',
            })
        decision_table_1[['EPS in 5 years', 'Future Value', 'Present Value', 
                'Margin Price', 'Current Share Price']] = np.round(
                    decision_table_1[['EPS in 5 years', 'Future Value', 
                        'Present Value', 'Margin Price', 'Current Share Price']],
                         2)
        decision_table_1_written = decision_table_1.to_dict('records')
        print('5 Finish')
        return decision_table_1_written
    else:
        print('5 Finish')
        return []
                        
if __name__ == '__main__':
    # application.run_server(debug=True)
    application.run_server(debug=False)
    
    # To run in Flask server, execute:
    # Create index.py with following content: 
    #       from Dashboard import application
    #       server = application.server
    # Type in Terminal: gunicorn Dashboard:server -b :8000
    # Open http://127.0.0.1:8000
    
    # https://community.plotly.com/t/deploying-your-dash-app-to-heroku-the-magical-guide/46723
    # https://fizzy.cc/deploy-dash-on-server/
    
    # To deploy on AWS Beanstalk:
    # https://www.youtube.com/watch?v=fGxY_Hji8_U&t=101s