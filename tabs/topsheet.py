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
                dbc.RadioItems(
                    id='data-type2',
                    options=[{'label': i, 'value': i} for i
                             in ['Time of Day', 'Facility Type']],
                    value='Time of Day',
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
    dbc.Card(
    dbc.CardBody(
            [
                html.H2('Person Totals'),
                dbc.RadioItems(
                    id='data-type3',
                    options=[{'label': i, 'value': i} for i
                             in ['VMT', 'VHT', 'Trips']],
                    value='VMT',
                    inline=True
                    ),
                html.Br(),
                dbc.RadioItems(
                    id='geography-level',
                    options=[{'label': i, 'value': i} for i
                             in ['Regional Geography', 'Race','Income','County']],
                    value='Regional Geography',
                    inline=True
                    ),
                html.Br(),
                dbc.RadioItems(
                    id='person-total',
                    options=[{'label': i, 'value': i} for i
                             in ['Total', 'Per Person']],
                    value='Total',
                    inline=True
                    ),
                html.Br(),
                html.Div(id='person-vmt'),
            ]
        ),
        style={"margin-top": "20px"},
    ),
    html.Div(id='dummy_div8'),
]

@app.callback(
    [Output('vmt-container', 'children'),
     Output('transit-boardings', 'children'),
     Output('person-vmt', 'children')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('data-type', 'value'),
     Input('data-type2', 'value'),
     Input('data-type3', 'value'),
     Input('person-total', 'value'),
     Input('geography-level', 'value'),
     Input('dummy_div7', 'children')])
def update_visuals(scenario1, scenario2, scenario3, data_type, data_type2, data_type3, person_total, geography_level, aux):

    def mylambda(scenario_list, data_type, data_type2):
        """Create a dataframe for all scenario road data, in long format"""
        df = pd.DataFrame()
        person_totals = []

        for x in scenario_list:
            for data_type in ['vmt','vht','delay']:
                fname = os.path.join(r'data', x, data_type+'_facility.csv')
                if os.path.isfile(fname):
                    # Load trip data
                    _df = pd.read_csv(fname)
                    if data_type2 == 'Time of Day':
                        _df['values'] = _df[['arterial','connector','highway']].sum(axis=1)
                        _df['index'] = _df['period']
                    else:
                        _df = _df[['arterial','connector','highway']].sum(axis=0).reset_index()
                        _df.rename(columns={0:'values'}, inplace=True)
                    _df['scenario'] = x
                    _df['data_type'] = data_type
                    df = df.append(_df)

        return df

    def transit_lambda(scenario_list):
        """Create a dataframe for transit boarding data, in long format"""
        df = pd.DataFrame()
        for x in scenario_list:
            fname = os.path.join(r'data', x, 'daily_boardings_by_agency.csv')
            if os.path.isfile(fname):
                _df = pd.read_csv(fname)
                # print(_df)
                _df = _df.groupby('agency').sum()[['modeled_5to20']].reset_index()
                _df['scenario'] = x
                df = df.append(_df)

        return df

    def load_person_vmt(scenario_list, data_type3, person_total, geography_level):
        # print(config)
        df = pd.DataFrame()
        for x in scenario_list:
            fname = os.path.join(r'data', x, 'person_'+data_type3.lower()+'.csv')
            if os.path.isfile(fname):
                total_col = config['data_source_dict'][data_type3]
                geog_level = config['data_source_dict'][geography_level]
                print(geography_level)
                _df = pd.read_csv(fname)
                print(_df.head())
                _df = _df[(_df['dorp'] == 1) & (_df['mode'].isin(['SOV','HOV2','HOV3+']))]
                _df = _df.groupby(geog_level).sum()[[total_col]].reset_index()
                _df['total'] = _df[total_col]
                # If this is VHT, divide by 60 to convert it to hours from minutes
                if data_type3 == 'VHT':
                    _df['total'] = _df['total']/60

                # Divide by total population in this geography if selected
                if person_total == 'Per Person':
                    _df_person = pd.read_csv(os.path.join(r'data', x, 'person_geog.csv'))
                    _df_person = _df_person.groupby(geog_level).sum()[['psexpfac']].reset_index()
                    _df = _df.merge(_df_person, on=geog_level)
                    _df['total'] = _df['total']/_df['psexpfac']
                _df['scenario'] = x
                df = df.append(_df)

        return df

    def create_totals_table(df, data_type, data_type2):
        """ calculate totals and collate into master dictionary """

        df = df[df['data_type'] == data_type]

        # index_col = 'index'
        # if data_type2 == 'Time of Day':
        #     index_col = 'period'
        df_dict = {
            'Time of Day': {
                'dict': {
                    'am': 'AM (5-9am)', 
                    'md': 'Mid-Day (9am-3pm', 
                    'pm': 'PM: 3-6pm', 
                    'ev': 'Evening: 6-8pm', 
                    'ni': 'Night: 8pm-5am' },
                'order': ['am','md','pm','ev','ni']
            },
            'Facility Type': {
            'dict': {
                'arterial': 'Arterial',
                'connector': 'Connector',
                'highway': 'Highway'
                },
            'order': ['highway','arterial','connector']
            }
        }

        df = df.pivot_table(index='index', columns='scenario', values='values', aggfunc='sum')
        df = df.astype('int').round(-3)
        
        df = df.loc[df_dict[data_type2]['order']]
        df = df.reset_index()
        df['index'] = df['index'].map(df_dict[data_type2]['dict'])
        df.rename(columns={'index': data_type2}, inplace=True)
        df.loc['Daily Total']= df.sum(numeric_only=True, axis=0)
        df[data_type2].iloc[-1] = 'Daily Total'

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

    def create_person_vmt_table(df, person_total, geography_level):
        
        geog_level = config['data_source_dict'][geography_level]
        df = df.pivot_table(index=geog_level, columns='scenario', values='total', aggfunc='sum')
        if person_total == 'Total':
            df = df.astype('int').round(-3)
            format_number_dp = functools.partial(format_number, decimal_places=0)
            df = df.reset_index()
            df.loc['Total']= df.sum(numeric_only=True, axis=0)
            df[geog_level].iloc[-1] = 'Total'
        else:
            format_number_dp = functools.partial(format_number, decimal_places=1)
            df = df.reset_index()
        
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


    df = mylambda(scenario_list, data_type, data_type2)
    totals_table = create_totals_table(df, str(data_type).lower(), data_type2)

    df = transit_lambda(scenario_list)
    transit_boardings = create_boardings_table(df)

    df = load_person_vmt(scenario_list, data_type3, person_total, geography_level)
    person_vmt = create_person_vmt_table(df, person_total, geography_level)

    return totals_table, transit_boardings, person_vmt

        

# Choose between time of day and facility type
# allow time of day periods or hours ( maybe ?)

# Table 
# Average Trip Length

# Trip/Tour Mode Share by purp
# default of all

# Other info
# Run date
# Run description?