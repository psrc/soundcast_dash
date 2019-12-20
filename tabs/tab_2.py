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


#df = pd.read_csv(r':\SoundCast\Dash\tab_multi_page\data\Survey\trips.csv')
#person_types = ['All']
#person_types.extend([x for x in df.pptyp.unique()])

#person_types = ['Child Age 0-4', 'Child Age 5-15', 'Full-Time Worker',
#       'High School Student Age 16+', 'Non-Working Adult Age 65+',
#       'Non-Working Adult Age <65', 'Part-Time Worker',
#       'University Student']


tab_2_layout = [dbc.Card(
    dbc.CardBody(
        [
            #html.H2(['Trip Mode Choice']),
            dbc.CardTitle('Filters'),
            dbc.Label('Person Type:'),
            dcc.Dropdown(
            #options=[{'label': i, 'value': i} for i in person_types],
                value='All',
                id='person-type-dropdown'
            ),
            html.Br(),
            dbc.Label('Destination Purpose:'),
            dcc.Dropdown(
                #options=[{'label': i, 'value': i} for i in person_types],
                value='All',
                id='dpurp-dropdown'
                ),
            html.Br(),
            #html.Div(id='output-container-button'),
            html.Div(id='df', style={'display': 'none'}),
            #dbc.CardFooter("Trip Mode Choice"),
            ##html.H4(['Trip Mode Choice:']),
            #dcc.Graph(id='mode-choice-graph'),
            #html.Br(),
            #dbc.CardFooter('Trip Departure Hour:'),
            #dcc.Graph(id='trip-deptm-graph'),

            #html.Div(id='dummy_div'),
        ],
        className = 'bg-light',
      
        ),
    className='card sticky-top',
    #className='card-deck mt-4',
),

#html.Br(),

dbc.Card(
    dbc.CardBody(
        [
            dbc.CardTitle("Trip Mode Choice"),
            html.Br(),
            dcc.RadioItems(
                id='mode-share-type',
                options=[{'label': i, 'value': i} for i in ['Mode Share', 'Trips by Mode']],
                value='Mode Share',
            ),
            dcc.Graph(id='mode-choice-graph'),
            #html.Br(),
            #dbc.CardFooter('Trip Departure Hour:'),
            #dcc.Graph(id='trip-deptm-graph'),

            html.Div(id='dummy_div'),
        ],

    ),
    #className='card-deck py-4',
    style= {"margin-top": "20px"},
     
),

#html.Br(),
#html.Br(),

dbc.Card(
    dbc.CardBody(
        [
            #dbc.CardFooter("Trip Mode Choice"),
            #dcc.Graph(id='mode-choice-graph'),
            #html.Br(),
            dbc.CardFooter('Trip Departure Hour:'),
            dcc.Graph(id='trip-deptm-graph'),

            #html.Div(id='dummy_div'),
        ]
    ),
    style= {"margin-top": "20px"},
),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
]
#tab_2_layout = html.Div([
#   html.H2(['Trip Mode Choice']),
#   html.H4(['Person Type:']),
#    dcc.Dropdown(
#        #options=[{'label': i, 'value': i} for i in person_types],
#        value='All',
#            id='person-type-dropdown'
#        ),
#    html.Br(),
#    html.H4(['Destination Purpose:']),
#    dcc.Dropdown(
#        #options=[{'label': i, 'value': i} for i in person_types],
#        value='All',
#            id='dpurp-dropdown'
#        ),
#    #html.Div(id='output-container-button'),
#    html.Div(id='df', style={'display': 'none'}),
#    dcc.Graph(id='mode-choice-graph'),
#    dcc.Graph(id='trip-deptm-graph'),

#    html.Div(id='dummy_div'),
#    #html.Div(id='dropdown-output'),
#    #html.Div(id='intermediate-value'),
#    #dcc.Graph(id='indicator-graphic',
#    #          style={'width': '50%'}),
#    #html.P(['We are on page three']),
#])




# load drop downs
@app.callback(
    [Output('person-type-dropdown', 'options'),
              Output('dpurp-dropdown', 'options')],
               [Input('trips', 'children'),
                Input('dummy_div', 'children')])

def load_drop_downs(json_data, aux):
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.dpurp.unique()])
    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('mode-choice-graph', 'figure'),
               Output('trip-deptm-graph', 'figure')],
               [Input('trips', 'children'),
                Input('person-type-dropdown', 'value'),
                Input('dpurp-dropdown', 'value'),
                Input('mode-share-type', 'value'),
                Input('dummy_div', 'children')])

def update_graph(json_data, person_type, dpurp, share_type, aux):
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df =df[df['pptyp'] == person_type] 
        if dpurp != 'All':
            df =df[df['dpurp'] == dpurp]
        if share_type == 'Mode Share':
            df_mode_share= df[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        else:
            df_mode_share= df[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph
        trace1 = go.Bar(
            x=df_mode_share['mode'].copy(),
            y=df_mode_share['trexpfac'].copy(),
            name=key
            )
        data1.append(trace1)

        # trip distance histogram
        df_deptm_share= df[['deptm_hr','trexpfac']].groupby('deptm_hr').sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        print (df_deptm_share)
        #df_deptm_share= df[['deptm_hr','trexpfac']].groupby('deptm_hr').sum()[['trexpfac']]
        df_deptm_share.reset_index(inplace=True)
       
        trace2 = go.Bar(
            x=df_deptm_share['deptm_hr'],
            y=df_deptm_share['trexpfac'].astype(int),
            name= key
)
        data2.append(trace2)
        #data.append[trace]

    layout1 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'mode'},
            yaxis={'title': share_type},
            hovermode='closest',
            )

    layout2 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'departure hour'},
            yaxis={'title': 'share'},
            hovermode='closest',
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}

    #df1 = pd.read_json(json_df1, orient='split')
    #df1= df1[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]/df1[['trexpfac']].sum() * 100
    #df1.reset_index(inplace=True)
    #df1.replace({'mode':mode_dict}, inplace=True)

    #df2 = pd.read_json(json_df2, orient='split')
    #df2= df2[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]/df2[['trexpfac']].sum() * 100
    #df2.reset_index(inplace=True)
    #df2.replace({'mode':mode_dict}, inplace=True)
   
    #trace1 = go.Bar(
    #        x=df1['mode'],
    #        y=df1['trexpfac']
    #        )

    #trace2 = go.Bar(
    #        x=df2['mode'],
    #        y=df2['trexpfac']
    #        )
    
    #data = [trace1, trace2]
            
    