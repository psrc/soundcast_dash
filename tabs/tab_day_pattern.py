import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from app import app
import json
import functools

def format_number(x):
    return "{:,.2f}".format(x)

tab_day_pattern_filter = [dbc.Card(
    [
    dbc.CardHeader(html.H1('Tours by Person Type Selection')), 
    dbc.CardBody(
        [
            dbc.Label('Destination Purpose:'),
            dcc.Dropdown(
                value='School',
                id='dpatt-dpurp-dropdown'
                ),
            html.Br(),
            #html.Div(id='df', style={'display': 'none'}),
            html.Div(id='dummy_div4'),
        ],
        className = 'bg-light',
      
        )],
    className='aside-card'
)   ]

tab_day_pattern_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Per Person Totals"),
                html.Br(),
                html.Div(id='dpatt-table-per-person-total'),
                ]
            ), style= {"margin-top": "20px"}
        ),
     dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Tours by Purpose"),
                        html.Div(id='dpatt-table-tours-purpose-general-container'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=12
            ), # end Col
         ]
        ),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-tours-pptyp-purpose-header'), #make label dynamic to dpurp 
                        html.Div(id='dpatt-table-tours-purpose-container'),
                        dcc.Graph(id='dpatt-graph-tours-purpose'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=12 #4
            ), # end Col
        #dbc.Col(
        #      dbc.Card(
        #        dbc.CardBody(
        #            [
        #                dcc.Graph(id='dpatt-graph-tours-purpose'),
        #                ]
        #            ), style= {"margin-top": "20px"}
        #        ),
        #    width=8
        #    ) # end Col
        ]
        ), # end Row
        
    html.Div(id='dummy_div5'),
    ]

# load drop downs
@app.callback(
    Output('dpatt-dpurp-dropdown', 'options'),
    [Input('tours', 'children'),
     Input('dummy_div4', 'children')])
def dpurp_dropdown(json_data, aux):
    print ('Day Pattern: tour filter callback')
    dpurp = []

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    print(key)
    df = pd.read_json(datasets[key], orient='split')
    dpurp.extend([x for x in df.pdpurp.unique()])
    print(dpurp)
    return [{'label': i, 'value': i} for i in dpurp]

# dynamic label based on dpurp selection
@app.callback(
    Output('dpatt-tours-pptyp-purpose-header', 'children'),
    [Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children')])
def update_tours_by_pptype_purpose_header(dpurp, aux):
    return dpurp + " Tours Per Person by Person Type"

# render as DashTable + graph
@app.callback(
    [Output('dpatt-table-tours-purpose-container', 'children'), Output('dpatt-graph-tours-purpose', 'figure')],
    [Input('tours', 'children'),
     Input('persons', 'children'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def create_table_tours_by_ptype_dpurp(tours_json, pers_json, dpurp, aux, aux1):
    print('compile tours per person data')
    tours = json.loads(tours_json)
    pers = json.loads(pers_json)
    datalist = []

    for key in tours.keys():
        df = pd.read_json(tours[key], orient='split')
        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        df = df.groupby(['pptyp', 'pdpurp']).sum()[['toexpfac']].reset_index().merge(df_pers, on = 'pptyp')
        df = df[df['pdpurp'] == dpurp]
        df['tours_per_person'] = df['toexpfac']/df['psexpfac']
        df = df.rename(columns = {'tours_per_person': key})
        datalist.append(df[['pptyp', 'pdpurp', key]]) 

    newdf = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=['pptyp', 'pdpurp']), datalist)
    print('finished compilation')

    # create dash table
    # format numbers with separator
    datatbl = newdf.copy()
    for i in range(2, len(datatbl.columns)):
        datatbl.iloc[:, i] = datatbl.iloc[:, i].apply(format_number)
    
    datatbl= datatbl.drop('pdpurp', axis=1)
    print(datatbl)
    print(newdf)
    datatbl = datatbl.rename(columns = {'pptyp': 'Person Type'}) #, 'pdpurp': 'Destination Purpose'
    print('creating table tours per person')
    t = html.Div(
    [dash_table.DataTable(id='dpatt-table-tours-purposes',
                          columns=[{"name": i, "id": i} for i in datatbl.columns],
                          data=datatbl.to_dict('rows'),
                          style_cell_conditional = [
                                  {
                                      'if': {'column_id': i},
                                      'textAlign': 'left'
                                      } for i in ['Person Type']
                                  ],
                          style_cell = {
                              'font-family':'Segoe UI',
                              'font-size': 12,
                              'text-align': 'center'}
                          )
      ])
    
    # create graph
    print('creating graph tours per person')
    
    graph_datalist = []
    for key in tours.keys():
        trace = go.Bar(
            x=newdf['pptyp'].copy(),
            y=newdf[key].copy(),
            name=key
            )
        graph_datalist.append(trace)
    print(graph_datalist)
    
    layout = go.Layout(
        barmode = 'group',
        xaxis={'type':'category'},#'title': 'Person Type', 
        yaxis={'title': dpurp + ' Tours per Person', 'zeroline':False},
        hovermode='closest',
        autosize=True,
        font=dict(family='Segoe UI', color='#7f7f7f')
        )
    print(layout)
    
    return t, {'data': graph_datalist, 'layout': layout}

