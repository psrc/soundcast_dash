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
                value='Escort',
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
     dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Percent of Tours by Purpose"),
                        html.Br(),
                        html.Div(id='dpatt-table-perc-tours-dpurp-gen-container'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=6
            ), # end Col
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Tours per Person by Purpose"),
                        html.Br(),
                        html.Div(id='dpatt-table-tours-dpurp-gen-container'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=6
            ) # end Col
         ]
        ),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-tours-pptyp-purpose-header'),
                        #html.Div(children=[html.Div(id='dpatt-table-tours-purpose-container'),
                        #                   dcc.Graph(id='dpatt-graph-tours-purpose')],className='inline-container'),
                        html.Div(id='dpatt-table-tours-purpose-container'),
                        #dcc.Graph(id='dpatt-graph-tours-purpose'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=5
            ), # end Col
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(id='dpatt-graph-tours-purpose'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=7
            ), # end Col
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

# dpurp tours per person by person type, render as DashTable + graph
@app.callback(
    [Output('dpatt-table-perc-tours-dpurp-gen-container', 'children'),
     Output('dpatt-table-tours-dpurp-gen-container', 'children'), 
     Output('dpatt-table-tours-purpose-container', 'children'), 
     Output('dpatt-graph-tours-purpose', 'figure')],
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
    datalist = [] # tours per person by person type and purpose
    datalist_all_dpurp = [] # tours per person by purpose
    datalist_dpurp_gen = [] # tours by purpose
    keys = tours.keys()
    keyslist = list(keys)

    for key in keys: 
        df = pd.read_json(tours[key], orient='split')
        # store in list for percent of tours by purpose
        df_dpurp_gen = df.groupby('pdpurp').sum()[['toexpfac']].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns = {'toexpfac': key})
        datalist_dpurp_gen.append(df_dpurp_gen[['pdpurp', key]])

        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        df = df.groupby(['pptyp', 'pdpurp']).sum()[['toexpfac']].reset_index().merge(df_pers, on = 'pptyp')

        df_dpurp = df.groupby('pdpurp').sum()[['toexpfac', 'psexpfac']].reset_index()
        print(df_dpurp.head())
        df_dpurp['tours_per_person'] = df_dpurp['toexpfac']/df_dpurp['psexpfac']
        df_dpurp = df_dpurp.rename(columns = {'tours_per_person': key})
        datalist_all_dpurp.append(df_dpurp[['pdpurp', key]])

        df_ptype = df[df['pdpurp'] == dpurp]
        df_ptype['tours_per_person'] = df_ptype['toexpfac']/df_ptype['psexpfac']
        df_ptype = df_ptype.rename(columns = {'tours_per_person': key})
        datalist.append(df_ptype[['pptyp', 'pdpurp', key]]) 
    
    newdf_dpurp_gen = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on='pdpurp'), datalist_dpurp_gen)
    newdf_dpurp = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on='pdpurp'), datalist_all_dpurp)
    newdf = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=['pptyp', 'pdpurp']), datalist)
    print('finished compilation')

    # create percent of tours by purpose
    print('newdf_dpurp_gen difference')
    tp_tbl = newdf_dpurp_gen.copy()
    for key in keyslist:
        tp_tbl[key] = (tp_tbl[key]/tp_tbl[key].sum()) * 100
    tp_tbl['Difference'] = tp_tbl[keyslist[0]] - tp_tbl[keyslist[1]]
    
    # format numbers with separator
    for i in range(1, len(tp_tbl.columns)):
        tp_tbl.iloc[:, i] = tp_tbl.iloc[:, i].apply(format_number)
    
    tp_tbl = tp_tbl.rename(columns = {'pdpurp': 'Destination Purpose'})
    
    tp = html.Div(
    [dash_table.DataTable(id='dpatt-table-perc-tours-dpurp-gen',
                          columns=[{"name": i, "id": i} for i in tp_tbl.columns],
                          data=tp_tbl.to_dict('rows'),
                          style_cell_conditional = [
                                  {
                                      'if': {'column_id': i},
                                      'textAlign': 'left'
                                      } for i in ['Destination Purpose']
                                  ],
                          style_cell = {
                              'font-family':'Segoe UI',
                              'font-size': '.7vw',
                              'text-align': 'center'}
                          )
    ])

    # create dash tables for tours per person and purpose
    print('newdf_dpurp difference')
    tppp_tbl = newdf_dpurp.copy()
    tppp_tbl['Difference'] = tppp_tbl[keyslist[0]] - tppp_tbl[keyslist[1]]
    tppp_tbl['Percent Difference'] = (tppp_tbl['Difference']/tppp_tbl[keyslist[1]]) * 100
    #add row total
    # format numbers with separator
    for i in range(1, len(tppp_tbl.columns)):
        tppp_tbl.iloc[:, i] = tppp_tbl.iloc[:, i].apply(format_number)
    
    tppp_tbl = tppp_tbl.rename(columns = {'pdpurp': 'Destination Purpose'})

    tppp = html.Div(
    [dash_table.DataTable(id='dpatt-table-tours-dpurp-gen',
                          columns=[{"name": i, "id": i} for i in tppp_tbl.columns],
                          data=tppp_tbl.to_dict('rows'),
                          style_cell_conditional = [
                                  {
                                      'if': {'column_id': i},
                                      'textAlign': 'left'
                                      } for i in ['Destination Purpose']
                                  ],
                          style_cell = {
                              'font-family':'Segoe UI',
                              'font-size': '.7vw',
                              'text-align': 'center'}
                          )
    ])

    # create dash table for tours per person by person type and purpose
    # add diff & %diff cols
    datatbl = newdf.copy()
    datatbl['Difference'] = datatbl[keyslist[0]] - datatbl[keyslist[1]]
    datatbl['Percent Difference'] = (datatbl['Difference']/datatbl[keyslist[1]]) * 100

    # format numbers with separator
    for i in range(2, len(datatbl.columns)):
        datatbl.iloc[:, i] = datatbl.iloc[:, i].apply(format_number)
    
    datatbl= datatbl.drop('pdpurp', axis=1)
    datatbl = datatbl.rename(columns = {'pptyp': 'Person Type'}) #, 'pdpurp': 'Destination Purpose'
    print('creating table tours per person')
    t = html.Div(
    [dash_table.DataTable(id='dpatt-table-tours-purposes',
                          columns=[{"name": i, "id": i} for i in datatbl.columns],
                          data=datatbl.to_dict('rows'),
                          #style_table={'overflowX': 'scroll'},
                          style_cell_conditional = [
                                  {
                                      'if': {'column_id': i},
                                      'textAlign': 'left'
                                      } for i in ['Person Type']
                                  ],
                          style_cell = {
                              'font-family':'Segoe UI',
                              'font-size': '.6vw',
                              'text-align': 'center',
                              'overflow': 'hidden',
                              'textOverflow': 'ellipsis'}
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
    #print(graph_datalist)
    
    layout = go.Layout(
        barmode = 'group',
        xaxis={'type':'category', 'automargin':True},
        yaxis={'title': dpurp + ' Tours per Person', 'zeroline':False},
        hovermode='closest',
        autosize=True,
        font=dict(family='Segoe UI', color='#7f7f7f')
        )
    #print(layout)
    
    return tp, tppp, t, {'data': graph_datalist, 'layout': layout}

