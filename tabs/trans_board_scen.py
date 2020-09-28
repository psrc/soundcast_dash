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
import functools

tab_transit_boardings_scenario_layout = [
    html.H6('Transit Boarding'),
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
            html.H2(id='boardings-header-scenario'),
            html.Br(),
            html.Div(id='boardings-container-scenario'),
            html.Br(),
            html.Div(id='scen-list'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ),  # end Row
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
            html.H2(id='key-route-header-scenario'),
            html.Br(),
            html.Div(id='key-route-boardings-scenario'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ),  # end Row
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
            html.H2(id='light-rail-boardings-header-scenario'),
            html.Br(),
            html.Div(id='light-rail-boardings-scenario'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ),  # end Row

]

tab_transit_boardings_scenario_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('Agency:'),
                    dcc.Dropdown(
                        value='All',
                        clearable=False,
                        id='agency-selection-scenario'
                    ),
                    html.Br(),
                    html.Div(id='dummy_div11'),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            
            ),
        ],
        className='aside-card',
        

    )]

#####################################################
# Transit boardings comparisons across scenarios tab
@app.callback(
    [Output('agency-selection-scenario','options'),
     Output('scen-list','value')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value')])
def transit_load_drop_downs(scen1, scen2, scen3):
    scen_list = []
    for scen in [scen1, scen2, scen3]:
        # Validation data only available for scenario runs, check if it exists before adding to available scen list
        fname_path = os.path.join('data', scen, 'daily_boardings_by_agency.csv')
        if os.path.isfile(fname_path):
            scen_list.append(scen)

    return [[{'label': i, 'value': i} for i in config['agency_list']], scen_list]

@app.callback(
    [Output('boardings-container-scenario', 'children'),
     Output('key-route-boardings-scenario', 'children'),
     Output('light-rail-boardings-scenario', 'children')],
     [Input('scen-list','value'),
     Input('agency-selection-scenario', 'value'),
     Input('dummy_div11', 'children')]
    )
# def update_visuals(scen1, scen2, scen3, agency, aux):
def update_visuals(scen_list, agency, aux):

    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def process_dataset(dataset, agency, scen_list, index_col, join_col):
        result = []
        for scen in scen_list:
            df = pd.DataFrame(dataset[scen])
            if agency != 'All':
                df = df[df['agency'] == agency] 
            df.set_index(index_col, inplace=True)
            df.rename(columns={'modeled_5to20': scen}, inplace=True)
            df.loc['Total'] = df.sum(numeric_only=True, axis=0)
            df[scen] = df[scen].map('{:,.0f}'.format)
            df.reset_index(inplace=True)
            if isinstance(join_col, list):
                col_list = join_col + [scen]
            else:
                col_list = [join_col,scen]

            result.append(df[col_list])        
        result = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=join_col), result)

        return result

    def create_totals_table(id_name, table):
        t = html.Div(
            [
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in table.columns],
                    data=table.to_dict('rows'),
                    style_cell={
                        'font-family': 'Segoe UI',
                        'text-align': 'center'}
                )
            ]
        )
        return t

    dataset = compile_csv_to_dict('daily_boardings_by_agency.csv', scen_list)
    result = process_dataset(dataset, agency, scen_list, index_col='agency', join_col='agency')
    agency_boardings = create_totals_table('boardings-container-scenario', result)

    dataset = compile_csv_to_dict('daily_boardings_key_routes.csv', scen_list)
    result = process_dataset(dataset, agency, scen_list, index_col='description', join_col=['description','agency'])
    key_route_boardings = create_totals_table('key-route-boardings-scenario-scenario', result)

    dataset = compile_csv_to_dict('light_rail_boardings.csv', scen_list)
    result = process_dataset(dataset, agency, scen_list, index_col='station_name', join_col='station_name')
    light_rail_boardings = create_totals_table('light-rail-boardings-scenario', result)

    return agency_boardings, key_route_boardings, light_rail_boardings
