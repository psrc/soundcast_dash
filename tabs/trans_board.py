import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from app import app, config
import dash_table
from collections import OrderedDict
import plotly.express as px

def datatable_format_number(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': ',.' + str(decimal_places) + 'f'}}
    

def datatable_format_percent(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': '.' + str(decimal_places) + '%'}}

available_scenarios = [name for name in os.listdir('data')
                       if os.path.isdir(os.path.join('data', name))
                       and name != 'data']

# List of model scenarios
model_scenarios = []
for scen in available_scenarios:
    # Validation data only available for scenario runs, check if it exists before adding to available scen list
    fname_path = os.path.join('data', scen, 'daily_volume_county_facility.csv')
    if os.path.isfile(fname_path):
        model_scenarios.append(scen)

tab_transit_boardings_layout = [
    html.H6('Transit'),
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id='boardings-header'),
            html.Br(),
            html.Div(id='boardings-container'),
            ]
        ), style={"margin-top": "20px"}
    ),
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id='key-route-header'),
            html.Br(),
            html.Div(id='key-route-boardings'),
            ]
        ), style={"margin-top": "20px"}
    ),
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id='light-rail-boardings-header'),
            html.Br(),
            html.Div(id='light-rail-boardings'),
            ]
        ), style={"margin-top": "20px"}
    ),
    # dbc.Card(
    # dbc.CardBody(
    #     [
    #         html.H2(id='traffic-totals-header'),
    #         html.Br(),
    #         html.Div(id='traffic-totals-container'),
    #         ]
    #     ), style={"margin-top": "20px"}
    # ),

    # dbc.Row(children=[
    #      dbc.Col(
    #         dbc.Card(
    #             dbc.CardBody(
    #                 [
    #         html.H2(id='boardings-header'),
    #         html.Br(),
    #         html.Div(id='boardings-container'),
    #                     ]
    #                 ), style={"margin-top": "20px"}
    #             ),
    #         width=12
    #         ),  # end Col
    #     ]
        # ),  # end Row
    # dbc.Row(children=[
    #      dbc.Col(
    #         dbc.Card(
    #             dbc.CardBody(
    #                 [
    #         html.H2(id='key-route-header'),
    #         html.Br(),
    #         html.Div(id='key-route-boardings'),
    #                     ]
    #                 ), style={"margin-top": "20px"}
    #             ),
    #         width=12
    #         ),  # end Col
    #     ]
    #     ),  # end Row
    # dbc.Row(children=[
    #      dbc.Col(
    #         dbc.Card(
    #             dbc.CardBody(
    #                 [
    #         html.H2(id='light-rail-boardings-header'),
    #         html.Br(),
    #         html.Div(id='light-rail-boardings'),
    #                     ]
    #                 ), style={"margin-top": "20px"}
    #             ),
    #         width=12
    #         ),  # end Col
    #     ]
    #     ),  # end Row

]

tab_transit_boardings_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
        dbc.CardBody(
            [
                dbc.Label('Validation Scenario:'),
                dcc.Dropdown(
                    value=model_scenarios[0],
                    clearable=False,
                    id='validation-scenario-transit'
                ),
                html.Br(),
            ],
            ), style={"margin-top": "20px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('Agency:'),
                    dcc.Dropdown(
                        value='All',
                        clearable=False,
                        id='agency-selection-validation'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            
            ),
            html.Div(id='dummy_div10'),
        ],
        className='aside-card',
        

    )]

####################################
# Transit validation tab
@app.callback(
    [Output('validation-scenario-transit', 'options'),
    Output('agency-selection-validation','options')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value')])
def transit_load_drop_downs(scen1, scen2, scen3):
    scen_list = []
    for scen in [scen1, scen2, scen3]:
        # Validation data only available for scenario runs, check if it exists before adding to available scen list
        fname_path = os.path.join('data', scen, 'daily_volume_county_facility.csv')
        if os.path.isfile(fname_path):
            scen_list.append(scen)

    return [[{'label': i, 'value': i} for i in scen_list], [{'label': i, 'value': i} for i in config['agency_list']]]

@app.callback(
    [Output('boardings-container', 'children'),
     Output('key-route-boardings', 'children'),
     Output('light-rail-boardings', 'children')],
    [Input('agency-selection-validation', 'value'),
     Input('validation-scenario-transit', 'value'),
     Input('dummy_div10', 'children')])
def update_visuals(agency, selected_scen, aux):
    def process_df(df, column_dict, agency, table_id, agency_filter):

        df = df[column_dict.keys()]

        if agency != 'All' and agency_filter is True:

            df = df[df['agency'] == agency]
        if 'perc_diff' not in column_dict.keys():
            df['Percent Difference'] = (df['modeled_5to20']-df['observed_5to20'])/df['observed_5to20']

        df.rename(columns=column_dict, inplace=True)

        df[['Modeled','Observed']] = df[['Modeled','Observed']].astype('int')
        df['Percent Difference'] = (df['Percent Difference']*100).map('{:,.1f}%'.format)
        df = df.sort_values('Modeled', ascending=False)
        for col in ['Modeled','Observed']:
            df[col] = df[col].map('{:,}'.format)

        
        t = html.Div(
        [dash_table.DataTable(columns=[{"name": i, "id": i} for i in df.columns],
                              data=df.to_dict('rows'),
                              sort_action="native",
                              style_cell={
                                  'font-family': 'Segoe UI',
                                  'font-size': 14,
                                  'text-align': 'center'}
                              )]
        )
        print(table_id)
        return t

    if selected_scen is not None:
        column_dict = OrderedDict([('agency','Agency'),
                                ('observed_5to20','Observed'), 
                                ('modeled_5to20','Modeled'),
                                ('perc_diff','Percent Difference')])
        df = pd.read_csv(os.path.join('data',selected_scen, 'daily_boardings_by_agency.csv'))
        agency_table = process_df(df, column_dict, agency, 'boardings-container', agency_filter=True)
        
        column_dict = OrderedDict([('agency','Agency'),
                                    ('description','Description'),
                                    ('observed_5to20','Observed'), 
                                    ('modeled_5to20','Modeled'),
                                    ('perc_diff','Percent Difference')])
        df2 = pd.read_csv(os.path.join('data',selected_scen, 'daily_boardings_key_routes.csv'))
        key_routes_table = process_df(df2, column_dict, agency, 'key-route-boardings', agency_filter=True)

        column_dict = OrderedDict([('station_name','Station'),
                                    ('observed_5to20','Observed'), 
                                    ('modeled_5to20','Modeled')])
        df = pd.read_csv(os.path.join('data',selected_scen, 'light_rail_boardings.csv'))
        lr_table = process_df(df, column_dict, agency, 'light-rail-boardings', agency_filter=False)

    return agency_table, key_routes_table, lr_table

