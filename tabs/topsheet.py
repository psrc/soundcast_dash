import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table
import numpy as np
import functools
from app import app, config

def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)

def create_tooltip(cell):
    num = float(cell)
    return num

# Topsheet Tab Layout
topsheet_filter = []

topsheet_layout = [
    html.H6('VMT, VHT, Delay'),
    dbc.Card(
        dbc.CardBody(
            [
                dbc.RadioItems(
                    id='data-type',
                    options=[{'label': i, 'value': i} for i
                             in ['VMT', 'VHT', 'Delay']],
                    value='VMT',
                    inline=True
                    ),
                html.Br(),
                html.Div(id='vmt-container'),
                ]
            ), style={"margin-top": "20px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2('Transit Boardings'),
                    html.Br(),
                    html.Div(id='transit-boardings'),
                ]
            ),
            style={"margin-top": "20px"},
        ),
    html.Div(id='dummy_div7'),

]



# Households and Persons tab ------------------------------------------------------------------
@app.callback(
    [Output('vmt-container', 'children'),
     Output('transit-boardings', 'children')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('data-type', 'value'),
     Input('dummy_div7', 'children')])
def update_visuals(scenario1, scenario2, scenario3, data_type, aux):

    def mylambda(scenario_list):
        df = pd.DataFrame()
        for x in scenario_list:
            for data_type in ['vmt','vht','delay']:
                _df = pd.read_csv(os.path.join(r'data', x, data_type+'_facility.csv'))
                _df['values'] = _df[['arterial','connector','highway']].sum(axis=1)
                _df = _df.groupby('period').sum()[['values']].reset_index()
                _df['scenario'] = x
                _df['data_type'] = data_type
                df = df.append(_df)
        return df


    def transit_lambda(scenario_list):
        df = pd.DataFrame()
        for x in scenario_list:
            _df = pd.read_csv(os.path.join(r'data', x, 'daily_boardings_by_agency.csv'))
            print(_df)
            _df = _df.groupby('agency').sum()[['modeled_5to20']].reset_index()
            _df['scenario'] = x
            df = df.append(_df)
        print(df)
        return df

    def create_totals_table(df, data_type):
        # calculate totals and collate into master dictionary

        df = df[df['data_type'] == data_type]

        # df = mylambda(filename, scenario_list, data_type)
        df = df.pivot_table(index='period', columns='scenario', values='values', aggfunc='sum')

        df = df.astype('int').round(-3)
        df = df.loc[['am','md','pm','ev','ni']]
        df = df.reset_index()
        df['period'] = df['period'].map({'am': 'AM (5-9am)', 'md': 'Mid-Day (9am-3pm', 'pm':
            'PM: 3-6pm', 'ev': 'Evening: 6-8pm', 'ni': 'Night: 8pm-5am' })
        df.rename(columns={'period': 'Time of Day'}, inplace=True)
        df.loc['Daily Total']= df.sum(numeric_only=True, axis=0)
        df['Time of Day'].iloc[-1] = 'Daily Total'


        # format numbers with separator
        format_number_dp = functools.partial(format_number, decimal_places=0)
        for i in range(1, len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].apply(format_number_dp)
        # print(df)
        t = html.Div(
            [dash_table.DataTable(id='blah-blah',
                                  columns=[{"name": i, "id": i} for i in df.columns],
                                  data=df.to_dict('rows'),
                                  style_cell={
                                      'font-family': 'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )

        return t

    def create_boardings_table(df):

        df = df.pivot_table(index='agency', columns='scenario', values='modeled_5to20', aggfunc='sum')
        df = df.reset_index()
        df.loc['Total Boardings']= df.sum(numeric_only=True, axis=0)
        df['agency'].iloc[-1] = 'Total Boardings'

        # format numbers with separator
        format_number_dp = functools.partial(format_number, decimal_places=0)
        for i in range(1, len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].apply(format_number_dp)

        t = html.Div(
            [dash_table.DataTable(id='blah-blah2',
                                  columns=[{"name": i, "id": i} for i in df.columns],
                                  data=df.to_dict('rows'),
                                  style_cell={
                                      'font-family': 'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )

        return t

    scenario_list = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]


    big_df = mylambda(scenario_list)
    totals_table = create_totals_table(big_df, str(data_type).lower())

    transit_df = transit_lambda(scenario_list)
    transit_boardings = create_boardings_table(transit_df)

    return totals_table, transit_boardings

        

# Choose between time of day and facility type
# allow time of day periods or hours ( maybe ?)

# Table 
# Link to Daysim tab?
# VMT per Person
# Trips per Person
# Average Trip Length

# Transit Boardings by Agency
# link to transit

# Trip/Tour Mode Share by purp
# default of all

# Other info
# Run date
# Run description?