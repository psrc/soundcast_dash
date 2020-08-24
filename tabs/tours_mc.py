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

# Tours mode choice Layout
tab_tours_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [

                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='tour-person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='tour-dpurp-dropdown'
                ),
                html.Br(),
                html.Div(
                    [dbc.Label('District:'),
                    dcc.Dropdown(
                        value='All',
                        clearable=False,
                        id='tour-district'
                    ),
                    html.Br(),
                    dbc.Label('Trip End:'),
                    dbc.RadioItems(
                        options=[{'label': i, 'value': i} for i
                                     in ['Origin', 'Destination']],
                        value='Origin',
                        id='tour-end'
                    ),
                    ],
                    className='box-group'
                ), # end Div
                html.Br(),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div2'),
            ],
            #className = 'bg-light',
        )],
    className='aside-card'
)]

tab_tours_mc_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Tour Mode Choice"),
                html.Br(),
                dbc.RadioItems(
                    id='tour-mode-share-type',
                    options=[{'label': i, 'value': i} for i
                             in ['Mode Share', 'Total Tours']],
                    value='Mode Share',
                    inline=True
                ),
                dcc.Graph(id='tour-mode-choice-graph'),
            ],
        ),
        style={"margin-top": "20px"},
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H2('Tour Departure Hour:'),
                html.Br(),
                dbc.RadioItems(
                    id='tour-mode-share-type-deptm',
                    options=[{'label': i, 'value': i} for i
                             in ['Distribution', 'Total Tours']],
                    value='Distribution',
                    inline=True
                ),
                dcc.Graph(id='tour-deptm-graph'),
            ]
        ),
        style={"margin-top": "20px"},
    ),
]

# Tours Mode Choice tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('tour-person-type-dropdown', 'options'),
     Output('tour-dpurp-dropdown', 'options'),
     Output('tour-district', 'options')],
    [Input('dummy_div2', 'children')])
def tour_load_drop_downs(aux):

    return [{'label': i, 'value': i} for i in config['person_type_list']], [{'label': i, 'value': i} for i in config['trip_purpose_list']], [{'label': i, 'value': i} for i in config['district_list']]
 
 
@app.callback([Output('tour-mode-choice-graph', 'figure'),
               Output('tour-deptm-graph', 'figure')],
              [Input('scenario-1-dropdown', 'value'),
               Input('scenario-2-dropdown', 'value'),
               Input('scenario-3-dropdown', 'value'),
               Input('tour-person-type-dropdown', 'value'),
               Input('tour-dpurp-dropdown', 'value'),
               Input('tour-end', 'value'),
               Input('tour-district', 'value'),
               Input('tour-mode-share-type', 'value'),
               Input('tour-mode-share-type-deptm', 'value')])
def tour_update_graph(scenario1, scenario2, scenario3, person_type, dpurp, end, end_district, 
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
                #print(os.path.join('data', scenario_list[x], 'tour_tlvorig_tour_' + end_type + '_district_' + end_district + '.csv'))
                df = pd.read_csv(os.path.join('data', scenario_list[x], 'tour_total_tour_' + end_type + '_district_' + end_district + '.csv'))  
            else:
                df = pd.read_csv(os.path.join('data', scenario_list[x], 'tour_total.csv'))   
            if person_type != 'All':
                df = df[df['pptyp'] == person_type]
            if dpurp != 'All':
                df = df[df['pdpurp'] == dpurp]
            if share_type in ['Distribution','Mode Share']:
                df_mode_share = df[['tmodetp', 'toexpfac']].groupby('tmodetp')\
                    .sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
            else:
                df_mode_share = df[['tmodetp', 'toexpfac']].groupby('tmodetp')\
                    .sum()[['toexpfac']]
            df_mode_share.reset_index(inplace=True)

            # mode choice graph
            trace1 = go.Bar(
                x=df_mode_share['tmodetp'].copy(),
                y=df_mode_share['toexpfac'].copy(),
                #name=key
                name=scenario_list[x]
                )
            data1.append(trace1)

             # trip distance histogram
            if share_type_deptm == 'Distribution':
                df_deptm_share = df[['tlvorg_hr', 'toexpfac']].groupby('tlvorg_hr')\
                    .sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
            else:
                df_deptm_share = df[['tlvorg_hr', 'toexpfac']].groupby('tlvorg_hr')\
                    .sum()[['toexpfac']]
            df_deptm_share.reset_index(inplace=True)

            trace2 = go.Scatter(
                x=df_deptm_share['tlvorg_hr'],
                y=df_deptm_share['toexpfac'].astype(int),
                #name=key
                name=scenario_list[x]
            )
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
    [Output('tour-end', 'options'),
     Output('tour-end', 'value')],
    [Input('tour-district', 'value')]
    )
def disable_tour_ends(tour_dist_choice):
    if tour_dist_choice != 'All':
        o = [{'label': i, 'value': i} for i in ['Origin', 'Destination']]
        v = 'Origin'
    else:
        o = [{'label': i, 'value': i, 'disabled': True} for i in ['Origin', 'Destination']]
        v = None
       
    return o, v