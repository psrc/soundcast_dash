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
 # = [dbc.Card(
 #    [
 #        dbc.CardHeader(html.H1('Filters')),
 #        dbc.CardBody(
 #            [
 #                dbc.Label('Aggregation Type'),
 #                dcc.Dropdown(
 #                    value='rg',
 #                    clearable=False,
 #                    id='agg-type'
 #                ),
 #            ],
 #            #className = 'bg-light',

 #        )  # end dbc.CardBody
 #    ],
 #    className='aside-card'
 #    )  # end dbc.Card
 #    ]

mode_choice_geog_layout = [
    html.H6('Mode Choice by Home Geography'),
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Trip Mode Choice"),
                html.Br(),
                dcc.Dropdown(
                    id='mode-share-type',
                    clearable=False,
                    value='Transit',
                    ),
                dcc.Graph(id='mode-choice-geog-graph'),
            ],
        ),  # end dbc.CardBody
        style={"margin-top": "20px"},
        ),  # end dbc.Card
]

mode_choice_geog_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('Geography Type:'),
                    dcc.Dropdown(
                        value='rg',
                        clearable=False,
                        id='agg-type'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            ),
            html.Div(id='dummy_div'),
        ],
        className='aside-card',
        

    )]

@app.callback(
    [Output('agg-type', 'options'),
    Output('mode-share-type', 'options')],
    [Input('dummy_div', 'children')])
def load_drop_downs(aux):

    mode_list = config['mode_list']
    mode_list = mode_list[mode_list!='All']   # Mode must be specified, drop "All" option
    return [[{'label': config['geog_col'][i]['label'], 'value': i} for i in config['geog_col']], [{'label': i, 'value': i} for i in config['mode_list']]]

@app.callback(Output('mode-choice-geog-graph', 'figure'),
              [Input('scenario-1-dropdown', 'value'),
               Input('scenario-2-dropdown', 'value'),
               Input('scenario-3-dropdown', 'value'),
               Input('agg-type', 'value'),
               Input('mode-share-type', 'value')])
def update_graph(scenario1, scenario2, scenario3, agg_type, selected_mode):

    data1 = []
    data2 = []
    scenario_list = [scenario1, scenario2, scenario3]
    
    trips_dict = {}
    tours_dict = {}
    persons_dict = {}

    for x in range(0, len(scenario_list)):
        if scenario_list[x] is not None:
            df = pd.read_csv(os.path.join('data',scenario_list[x],'mode_share_'+agg_type+'.csv'))
            agg_col = config['geog_col'][agg_type]['col']
            df_sum = df['trexpfac'].sum()
            df = df[df['mode'] == selected_mode]
            df = df.groupby(agg_col).sum()[['trexpfac']]
            df = df.reset_index()
            df['mode_share'] = df['trexpfac']/df_sum

        # mode choice graph
            trace1 = go.Bar(
                x=df[agg_col].copy(),
                y=df['mode_share'].copy(),
                name=scenario_list[x]
            )
            data1.append(trace1)

    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': agg_col},
            yaxis={'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    return {'data': data1, 'layout': layout1}