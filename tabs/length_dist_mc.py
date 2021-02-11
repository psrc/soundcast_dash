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

# Length and distance Layout
tab_length_distance_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
            dbc.CardBody(
                [
                    dbc.Label('Format Type:'),
                    dbc.RadioItems(
                        id='distance-format-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Percent', 'Total']],
                        value='Percent'
                    ),
                    html.Br(),
                    html.Div(id='dummy-dataset-type'),
                    html.Div(id='dummy-format-type'),
                ],
                ),  # end of CardBody
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                html.Br(),
                dbc.Label('Mode:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-mode-dropdown'
                ),
                html.Br(),
                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-dpurp-dropdown'
                ),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div6'),
            ],
            #className = 'bg-light',
        )],
    className='aside-card'
)]

tab_length_distance_mc_layout = [
    
    html.H6('Trip Length Distance'),
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='distance-graph1-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        dcc.Graph(id='tour-duration-graph'),
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
                        html.H2(id='distance-graph2-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        dcc.Graph(id='trip-time-graph'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 

]

# Length and Distance tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('distance-person-type-dropdown', 'options'),
     Output('distance-dpurp-dropdown', 'options'),
     Output('distance-mode-dropdown', 'options')],
    [Input('dummy_div6', 'children')])
def tour_load_drop_downs(aux):
    return [{'label': i, 'value': i} for i in config['person_type_list']], [{'label': i, 'value': i} for i in config['trip_purpose_list']], [{'label': i, 'value': i} for i in config['mode_list']]

# dynamic headers
@app.callback(
    [Output('distance-graph1-header', 'children'),
     Output('distance-graph2-header', 'children')],
    [Input('distance-person-type-dropdown', 'value'),
     Input('distance-dpurp-dropdown', 'value'),
     Input('distance-mode-dropdown', 'value'),
     Input('distance-format-type', 'value'),
     ])
def update_headers(person_type, dpurp, mode, format_type):

    result = []
    for chart_type in [' Distance', ' Time']:
        if dpurp != 'All':
            header_graph1 = dpurp + ' Trip ' + chart_type
        else:
            header_graph1 = 'Trip ' + chart_type
        if mode != 'All':
            header_graph1 += ' by ' + mode
        if person_type != 'All':
            header_graph1 += ' for ' + person_type

        result.append(header_graph1)

    return result


@app.callback(
    [Output('tour-duration-graph', 'figure'),
     Output('trip-time-graph', 'figure')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('distance-person-type-dropdown', 'value'),
     Input('distance-dpurp-dropdown', 'value'),
     Input('distance-mode-dropdown', 'value'),
     Input('distance-format-type', 'value'),
     ]
     # Input('dummy_div6', 'children')]
    )
def update_visuals(scenario1, scenario2, scenario3, person_type, dpurp, mode, format_type):
    #print('length and distance graph callback')
    
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_line_graph(table, xcol, weightcol, person_type, mode, dpurp, format_type, xaxis_title, yaxis_title):
        datalist = []
        i = 0
        for key in table.keys():
            df = table[key]
            df = df[df[xcol] > 0]

            # Apply person type, mode, and purpose filters
            for filter_name, filter_value in {'pptyp': person_type, 'mode': mode, 'dpurp': dpurp}.items():
                if filter_value != 'All': 
                    df = df[df[filter_name] == filter_value]

            df = df[[xcol, weightcol]].groupby(xcol).sum()[[weightcol]]
            df = df.reset_index()
            df[weightcol] = df[weightcol].astype('int')

            # Exclude outlying 1% of data
            df['cumulative_share'] = df['trexpfac'].cumsum()/df['trexpfac'].sum()
            df = df[df['cumulative_share'] < 0.99]

            # Calculate shares if selected
            if format_type == 'Percent':
                df[weightcol] = df[weightcol]/df[weightcol].sum()
            
            trace = go.Scatter(
                line_shape='linear',
                x=df[xcol].copy(),
                y=df[weightcol].copy(),
                name=key,
                marker_color=config['color_list'][i]
                )
            datalist.append(trace)
            i+=1

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type': 'linear'},
            yaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    scenario_list  = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
    
    dist_tbl = compile_csv_to_dict('trip_distance.csv', vals)
    time_tbl = compile_csv_to_dict('trip_time.csv', vals)
    agraph = create_line_graph(dist_tbl, 'travdist_bin', 'trexpfac', person_type, mode, 
        dpurp, format_type, 'Trip Distance (miles)', format_type)
    bgraph = create_line_graph(time_tbl, 'travtime_bin', 'trexpfac', person_type, mode, 
        dpurp, format_type,  format_type + ' Travel Time (min.)', format_type)

    return agraph, bgraph
