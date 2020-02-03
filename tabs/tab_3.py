import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from app import app
import json

tab_3_filter =  [dbc.Card(
    [
    dbc.CardHeader(html.H1('Filters')), 
    dbc.CardBody(
        [
            
            dbc.Label('Person Type:'),
            dcc.Dropdown(
                value='All',
                id='tour-person-type-dropdown'
            ),
            html.Br(),
            dbc.Label('Destination Purpose:'),
            dcc.Dropdown(
                value='All',
                id='tour-dpurp-dropdown'
                ),
            html.Br(),
            html.Div(id='df', style={'display': 'none'}),
            html.Div(id='dummy_div2'),
        ],
        className = 'bg-light',
      
        )],
    className='aside-card'
)   ]

tab_3_layout = [
dbc.Card(
    dbc.CardBody(
        [
            html.H2("Tour Mode Choice"),
            html.Br(),
            dbc.RadioItems(
                id='tour-mode-share-type',
                options=[{'label': i, 'value': i} for i in ['Mode Share', 'Tours by Mode']],
                value='Mode Share',
                inline=True
            ),
            dcc.Graph(id='tour-mode-choice-graph'),
            #html.Br(),
            #dbc.CardFooter('Trip Departure Hour:'),
            #dcc.Graph(id='trip-deptm-graph'),

        ],

    ),
    #className='card-deck py-4',
    style= {"margin-top": "20px"},
     
),

dbc.Card(
    dbc.CardBody(
        [
            #dbc.CardFooter("Trip Mode Choice"),
            #dcc.Graph(id='mode-choice-graph'),
            #html.Br(),
            html.H2('Tour Departure Hour:'),
            dcc.Graph(id='tour-deptm-graph'),

            #html.Div(id='dummy_div'),
        ]
    ),
    style= {"margin-top": "20px"},
),
]

# load drop downs
@app.callback(
    [Output('tour-person-type-dropdown', 'options'),
              Output('tour-dpurp-dropdown', 'options')],
               [Input('tours', 'children'),
                Input('dummy_div2', 'children')])

def tour_load_drop_downs(json_data, aux):
    print ('tour filter callback')
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.pdpurp.unique()])
    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('tour-mode-choice-graph', 'figure'),
               Output('tour-deptm-graph', 'figure')],
               [Input('tours', 'children'),
                Input('tour-person-type-dropdown', 'value'),
                Input('tour-dpurp-dropdown', 'value'),
                Input('tour-mode-share-type', 'value')])

def tour_update_graph(json_data, person_type, dpurp, share_type):
    print ('tour update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df =df[df['pptyp'] == person_type] 
        if dpurp != 'All':
            df =df[df['pdpurp'] == dpurp]
        if share_type == 'Mode Share':
            df_mode_share= df[['tmodetp','toexpfac']].groupby('tmodetp').sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
        else:
            df_mode_share= df[['tmodetp','toexpfac']].groupby('tmodetp').sum()[['toexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph
        trace1 = go.Bar(
            x=df_mode_share['tmodetp'].copy(),
            y=df_mode_share['toexpfac'].copy(),
            name=key
            )
        data1.append(trace1)

        # trip distance histogram
        df_deptm_share= df[['tlvorg_hr','toexpfac']].groupby('tlvorg_hr').sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
        #print (df_deptm_share)
        #df_deptm_share= df[['deptm_hr','trexpfac']].groupby('deptm_hr').sum()[['trexpfac']]
        df_deptm_share.reset_index(inplace=True)
       
        trace2 = go.Bar(
            x=df_deptm_share['tlvorg_hr'],
            y=df_deptm_share['toexpfac'].astype(int),
            name= key
)
        data2.append(trace2)
        #data.append[trace]

    layout1 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'mode'},
            yaxis={'title': share_type},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'departure hour'},
            yaxis={'title': 'share'},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}

