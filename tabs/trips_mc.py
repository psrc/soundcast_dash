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


# Trips Mode Choice Layout
tab_trips_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='dpurp-dropdown'
                ),
                html.Br(),
                html.Div(
                    [dbc.Label('District:'),
                    dcc.Dropdown(
                        value='All',
                        clearable=False,
                        id='trip-district'
                    ),
                    html.Br(),
                    dbc.Label('Trip End:'),
                    dbc.RadioItems(
                        options=[{'label': i, 'value': i, 'disabled': True} for i
                                     in ['Origin', 'Destination']],
                        #value='Origin',
                        id='trip-end'
                    
                    ),
                    ],
                    className="box-group"
                ), # end Div
                #html.Br(),
                #dbc.Label('District:'),
                #dcc.Dropdown(
                #    value='All',
                #    clearable=False,
                #    id='trip-district'
                #),
                html.Br(),
                html.Div(id='dummy_div'),
            ],
            #className = 'bg-light',

        )  # end dbc.CardBody
    ],
    className='aside-card'
    )  # end dbc.Card
    ]

tab_trips_mc_layout = [dbc.Card(
    dbc.CardBody(
        [
            html.H2("Trip Mode Choice"),
            html.Br(),
            dbc.RadioItems(
                id='mode-share-type',
                options=[{'label': i, 'value': i} for i
                         in ['Mode Share', 'Trips by Mode']],
                value='Mode Share',
                inline=True
                ),
            dcc.Graph(id='mode-choice-graph'),
        ],
    ),  # end dbc.CardBody
    style={"margin-top": "20px"},
    ),  # end dbc.Card
    dbc.Card(
        dbc.CardBody(
            [
                html.H2('Trip Departure Hour:'),
                html.Br(),
                dbc.RadioItems(
                    id='mode-share-type-deptm',
                    options=[{'label': i, 'value': i} for i
                             in ['Distribution', 'Total Trips']],
                    value='Distribution',
                    inline=True
                    ),
                dcc.Graph(id='trip-deptm-graph'),
            ]
        ),
        style={"margin-top": "20px"},
    )
]

@app.callback(
    [Output('person-type-dropdown', 'options'),
     Output('dpurp-dropdown', 'options'),
     Output('trip-district', 'options')],
    [Input('dummy_div', 'children')
])
def load_drop_downs(aux):

    return [{'label': i, 'value': i} for i in config['person_type_list']], [{'label': i, 'value': i} for i in config['trip_purpose_list']], [{'label': i, 'value': i} for i in config['district_list']]

@app.callback([Output('mode-choice-graph', 'figure'),
               Output('trip-deptm-graph', 'figure')],
              [Input('scenario-1-dropdown', 'value'),
               Input('scenario-2-dropdown', 'value'),
               Input('scenario-3-dropdown', 'value'),
               Input('person-type-dropdown', 'value'),
               Input('dpurp-dropdown', 'value'),
               Input('trip-end', 'value'),
               Input('trip-district', 'value'),
               Input('mode-share-type', 'value'),
               Input('mode-share-type-deptm', 'value')])
def update_graph(scenario1, scenario2, scenario3, person_type, dpurp, end, end_district, 
                 share_type, share_type_deptm):

    data1 = []
    data2 = []
    scenario_list = [scenario1, scenario2, scenario3]
    
    trips_dict = {}
    tours_dict = {}
    persons_dict = {}

    for x in range(0, len(scenario_list)):
        if scenario_list[x] is not None:
            if end_district != 'All':
                end_type = 'o' if end == 'Origin' else 'd'
                df = pd.read_csv(os.path.join('data', scenario_list[x], 'trip_total_trip_' + end_type + '_district_' + end_district + '.csv'))  
            else:
                df = pd.read_csv(os.path.join('data', scenario_list[x], 'trip_total.csv'))   
            if person_type != 'All':
                df = df[df['pptyp'] == person_type]
            if dpurp != 'All':
                df = df[df['dpurp'] == dpurp]
            if share_type == 'Mode Share':
                df_mode_share = df[['mode', 'trexpfac']].groupby('mode')\
                    .sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
            else:
                df_mode_share = df[['mode', 'trexpfac']].groupby('mode')\
                    .sum()[['trexpfac']]
            df_mode_share.reset_index(inplace=True)

        # mode choice graph
            trace1 = go.Bar(
                x=df_mode_share['mode'].copy(),
                y=df_mode_share['trexpfac'].copy(),
                name=scenario_list[x]
            )
            data1.append(trace1)

        # trip distance histogram
            if share_type_deptm == 'Distribution':
                df_deptm_share = df[['deptm_hr', 'trexpfac']].groupby('deptm_hr')\
                    .sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
            else:
                df_deptm_share = df[['deptm_hr', 'trexpfac']].groupby('deptm_hr')\
                    .sum()[['trexpfac']]
            df_deptm_share.reset_index(inplace=True)
            
            trace2 = go.Scatter(
                x=df_deptm_share['deptm_hr'],
                y=df_deptm_share['trexpfac'].astype(int),
                name=scenario_list[x])

            data2.append(trace2)

    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'Mode'},
            yaxis={'title': share_type, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode='group',
            xaxis={'title': 'Departure Hour'},
            yaxis={'title': share_type_deptm, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}

@app.callback(
    [Output('trip-end', 'options'),
     Output('trip-end', 'value')],
    [Input('trip-district', 'value')]
    )
def disable_trip_ends(trip_dist_choice):
    if trip_dist_choice != 'All':
        o = [{'label': i, 'value': i} for i in ['Origin', 'Destination']]
        v = 'Origin'
    else:
        o = [{'label': i, 'value': i, 'disabled': True} for i in ['Origin', 'Destination']]
        v = None
       
    return o, v

