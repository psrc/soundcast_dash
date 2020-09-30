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

# Tours 2  Layout
tab_tours2_mc_filter = [dbc.Card(
    [       dbc.CardHeader(html.H1('Filters')),
            dbc.CardBody(
                [
                    dbc.Label('Format Type:'),
                    dbc.RadioItems(
                        id='tour2-format-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Percent', 'Total']],
                        value='Percent'
                    ),
                    html.Br(),
                    html.Div(id='dummy-dataset-type'),
                    html.Div(id='dummy-format-type'),
                ],
                ),  # end of CardBody

        ],
    className='aside-card'
)]

tab_tours2_mc_layout = [
    html.H6('Trips and Stops by Tour (Tour 2 tab)'),
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='trips-tour-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        html.Br(),
                        dcc.Dropdown(
                            id='tour2-mode-dropdown',
                            options=[{'label': i, 'value': i} for i
                                     in config['mode_list']],
                            value='All',
                            clearable=False
                        ),
                        dcc.Graph(id='trips-by-tour'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 
        dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='stops-by-tour-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        html.Br(),
                        dbc.RadioItems(
                            id='stops-by-tour-type',
                            options=[{'label': i, 'value': i} for i
                                     in ['Entire Tour','First Half', 'Second Half']],
                            value='Entire Tour',
                            inline=True
                        ),
                        html.Br(),
                        dcc.Dropdown(
                            id='stops-by-tour-purpose',
                            options=[{'label': i, 'value': i} for i
                                     in config['trip_purpose_list']],
                            value='All',
                            clearable=False
                        ),
                        dcc.Graph(id='stops-by-tour'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 

]

# Tour 2; trips by tour
# Tours Mode Choice tab -----------------------------------------------------

@app.callback(
    [Output('trips-tour-header', 'children'),
     Output('stops-by-tour-header', 'children')],
    [Input('tour2-mode-dropdown', 'value'),
     Input('stops-by-tour-purpose', 'value'),
     Input('stops-by-tour-type', 'value')
     ])
def update_headers(mode, dpurp, stop_type):

    result = []
    header_graph1 = 'Trips by Tours: ' + dpurp + ' Tours '    
    if mode != 'All':
        header_graph1 += ' by ' + mode

    result.append(header_graph1)

    header_graph2 = 'Stops on Tour: ' + dpurp + ' Tours' 
    header_graph2 += ' | ' + stop_type
    result.append(header_graph2)
    return result

@app.callback([Output('trips-by-tour', 'figure'),
              Output('stops-by-tour', 'figure')],
              [ Input('scenario-1-dropdown', 'value'),
                Input('scenario-2-dropdown', 'value'),
                Input('scenario-3-dropdown', 'value'),
                Input('tour2-format-type', 'value'),
                Input('tour2-mode-dropdown', 'value'),
                Input('stops-by-tour-type', 'value'),
                Input('stops-by-tour-purpose', 'value')])
def update_visuals(scenario1, scenario2, scenario3, format_type, mode, stop_type, radio_dpurp):
    
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_bar_chart_horiz(table, xcol, weightcol, format_type, mode, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            if key != 'None':
                df = table[key]
                # df.drop(['mode','pdpurp'], axis=1, inplace=True)
                
                # Apply mode, and purpose filters
                for filter_name, filter_value in {'tmodetp': mode}.items():
                    if filter_value != 'All':
                        df = df[df[filter_name] == filter_value]

                df = df[xcol+[weightcol]].groupby(xcol).sum()[[weightcol]]

                df = df.reset_index()
                df[weightcol] = df[weightcol].astype('int')

                # Calculate shares if selected
                if format_type == 'Percent':
                    df[weightcol] = df[weightcol]/df[weightcol].sum()
                # print(df.head())
                trace = go.Bar(
                    y=df['dpurp'].copy(),
                    x=df[weightcol].copy(),
                    name=key,
                    orientation='h',
                    )
                datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            yaxis={'type': 'category', 'automargin': True},
            xaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    def create_bar_chart(table, xcol, weightcol, format_type, radio_dpurp, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            if key != 'None':
                df = table[key]

                df['all_stops'] = df['tripsh1'] + df['tripsh2'] 

                # Apply mode, purpose, and tour part filters
                for filter_name, filter_value in {'pdpurp': radio_dpurp}.items():
                    if filter_value != 'All':
                        df = df[df[filter_name] == filter_value]
                df = df[[xcol,weightcol]].groupby(xcol).sum()[[weightcol]]

                df = df.reset_index()
                df[weightcol] = df[weightcol].astype('int')

                # Exclude outlying 1% of data
                df = df[df[weightcol].cumsum()/df[weightcol].sum() < 0.99]

                # Calculate shares if selected
                if format_type == 'Percent':
                    df[weightcol] = df[weightcol]/df[weightcol].sum()

                trace = go.Bar(
                    x=df[xcol].astype('int').copy(),
                    y=df[weightcol].copy(),
                    name=key,
                    )
                datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type':'category'},
            yaxis={'title': yaxis_title},
            hovermode='closest',
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    scenario_list  = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
   
    trips_by_tour_tbl = compile_csv_to_dict('trips_by_tour.csv', vals)
    stops_by_tour_tbl = compile_csv_to_dict('tour_stops_outbound.csv', vals)
    agraph = create_bar_chart_horiz(trips_by_tour_tbl, ['dpurp'], 'trexpfac', format_type, 
        mode, 'Purpose', format_type)

    stop_type_dict = {'Entire Tour': 'all_stops', 'First Half': 'tripsh1', 'Second Half': 'tripsh2'}
    stop_type_val = stop_type_dict[stop_type]
    # Use toggle value to define which tour half is displayed
    bgraph = create_bar_chart(stops_by_tour_tbl, stop_type_val, 'toexpfac', format_type, 
        radio_dpurp, 'Stops', format_type)

    return agraph, bgraph
