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

def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)

tab_day_pattern_filter = [
    dbc.Card(
        [
        dbc.CardHeader(html.H1('Dataset')), 
        dbc.CardBody(
            [
                dbc.Label('Day Pattern Type:'),
                dbc.RadioItems(
                    id='dpatt-dataset-type',
                    options=[{'label': i, 'value': i} for i in ['Tours', 'Trips']],
                    value='Tours'
                ),
                html.Br(),
                html.Div(id='dummy-dataset-type'),
            ],
            className = 'bg-light',
        ), # end of CardBody

        dbc.CardHeader(html.H1('Day Pattern by Person Type')), 
        dbc.CardBody(
            [
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='Escort',
                    id='dpatt-dpurp-dropdown'
                    ),
                html.Br(),
                html.Div(id='dummy_div4'),
            ],
            className = 'bg-light',
      
        ) # end of CardBody
        ], # end of Card
        className='aside-card'
    ), # end of Card
]

tab_day_pattern_layout = [
     dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-perc-dpurp-gen-header'), #"Percent of X by Purpose"
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
                        html.H2(id='dpatt-dpurp-gen-header'), #"X per Person by Purpose"
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
    [Input('dpatt-dataset-type', 'value'),
     Input('tours', 'children'),
     Input('trips', 'children'),
     Input('dummy_div4', 'children')])
def dpurp_dropdown(dataset_type, tours_json, trips_json, aux):
    dpurp = []
    if dataset_type == 'Tours':
        dataset = json.loads(tours_json)
        dataset_dpurp_col = 'pdpurp'
    else:
        dataset = json.loads(trips_json)
        dataset_dpurp_col = 'dpurp'
    key = list(dataset)[0]
    df = pd.read_json(dataset[key], orient='split')
    dpurp.extend([x for x in df[dataset_dpurp_col].unique()])
    return [{'label': i, 'value': i} for i in dpurp]

# dynamic label based on dpurp selection
@app.callback(
    [Output('dpatt-tours-pptyp-purpose-header', 'children'),
     Output('dpatt-perc-dpurp-gen-header', 'children'),
     Output('dpatt-dpurp-gen-header', 'children')],
    [Input('dpatt-dataset-type', 'value'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')])
def update_tours_by_pptype_purpose_header(dataset_type, dpurp, aux, aux1):
    header_pptyp_dpurp = dpurp + ' ' + dataset_type + ' per Person by Person Type'
    header_perc_dpurp_gen = 'Percent of' + ' ' + dataset_type + ' by Purpose'
    header_dpurp_gen = dataset_type + ' per Person by Purpose'
    return header_pptyp_dpurp, header_perc_dpurp_gen, header_dpurp_gen

# all content, render as DashTables + graph
@app.callback(
    [Output('dpatt-table-perc-tours-dpurp-gen-container', 'children'),
     Output('dpatt-table-tours-dpurp-gen-container', 'children'), 
     Output('dpatt-table-tours-purpose-container', 'children'), 
     Output('dpatt-graph-tours-purpose', 'figure')],
    [Input('dpatt-dataset-type', 'value'),
     Input('trips', 'children'),
     Input('tours', 'children'), 
     Input('persons', 'children'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def update_visuals(dataset_type, trips_json, tours_json, pers_json, dpurp, aux, aux1):
    def calc_dpatt_per_person(table, group_cols_list, weight_name, key):
        df = table.copy()
        group_cols_list.append(key)
        df['day_pattern_per_person'] = df[weight_name]/df['psexpfac'] 
        df = df.rename(columns = {'day_pattern_per_person': key})
        df = df[group_cols_list]
        return df

    def calc_delta(table, keyslist, old_colname, new_colname, decimal_places, percent_delta = True):
        format_number_two_dp = functools.partial(format_number, decimal_places = decimal_places)
        table['Difference'] = table[keyslist[0]] - table[keyslist[1]]
        if percent_delta:
            table['Percent Difference'] = (table['Difference']/table[keyslist[1]]) * 100
        # format numbers with separator
        for i in range(1, len(table.columns)):
            table.iloc[:, i] = table.iloc[:, i].apply(format_number_two_dp)
        table = table.rename(columns = {old_colname: new_colname}) 
        return table

    def create_dash_table(id_name, table, index_list, fontsize):
        t = html.Div(
            [dash_table.DataTable(id=id_name,
                                    columns=[{"name": i, "id": i} for i in table.columns],
                                    data=table.to_dict('rows'),
                                    style_cell_conditional = [
                                            {
                                                'if': {'column_id': i},
                                                'textAlign': 'left'
                                                } for i in index_list
                                            ],
                                    style_cell = {
                                        'font-family':'Segoe UI',
                                        'font-size': fontsize,
                                        'text-align': 'center'}
                                    )
            ]
            )
        return t

    # load all data
    trips = json.loads(trips_json)
    tours = json.loads(tours_json)
    pers = json.loads(pers_json)

    if dataset_type == 'Tours':
        dataset = tours
        dataset_weight_col = 'toexpfac'
        dataset_dpurp_col = 'pdpurp'
    else:
        dataset = trips
        dataset_weight_col = 'trexpfac'
        dataset_dpurp_col = 'dpurp'

    datalist = [] # X per person by person type and purpose
    datalist_all_dpurp = [] # X per person by purpose 
    datalist_dpurp_gen = [] # X by purpose
    
    keys = dataset.keys()
    keyslist = list(keys)

    for key in keys: 
        df = pd.read_json(dataset[key], orient='split')

        df_dpurp_gen = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns = {dataset_weight_col: key})
        datalist_dpurp_gen.append(df_dpurp_gen[[dataset_dpurp_col, key]])

        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        df = df.groupby(['pptyp', dataset_dpurp_col]).sum()[[dataset_weight_col]].reset_index().merge(df_pers, on = 'pptyp')

        df_dpurp = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col, 'psexpfac']].reset_index()
        datalist_all_dpurp.append(calc_dpatt_per_person(df_dpurp, [dataset_dpurp_col], dataset_weight_col, key))

        df_ptype = df[df[dataset_dpurp_col] == dpurp]
        datalist.append(calc_dpatt_per_person(df_ptype, ['pptyp', dataset_dpurp_col], dataset_weight_col, key))  
    
    newdf_dpurp_gen = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=dataset_dpurp_col), datalist_dpurp_gen)
    newdf_dpurp = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=dataset_dpurp_col), datalist_all_dpurp)
    newdf = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=['pptyp', dataset_dpurp_col]), datalist)
  
    # create percent of tours by purpose
    tp_tbl = newdf_dpurp_gen.copy()
    for key in keyslist:
        tp_tbl[key] = (tp_tbl[key]/tp_tbl[key].sum()) * 100
    tp_tbl = calc_delta(tp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2, percent_delta = False)
    tp = create_dash_table('dpatt-table-perc-tours-dpurp-gen', tp_tbl, ['Destination Purpose'], '.7vw')

    # create dash tables for tours per person and purpose
    tppp_tbl = newdf_dpurp.copy()
    tppp_tbl = calc_delta(tppp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2)
    tppp = create_dash_table('dpatt-table-tours-dpurp-gen', tppp_tbl, ['Destination Purpose'], '.7vw')

    # create dash table for tours per person by person type and purpose
    datatbl = newdf.copy()
    datatbl= datatbl.drop(dataset_dpurp_col, axis=1)
    datatbl = calc_delta(datatbl, keyslist, 'pptyp', 'Person Type', 2)
    t = create_dash_table('dpatt-table-tours-purposes', datatbl, ['Person Type'], '.6vw')
    
    # create graph
    
    graph_datalist = []
    for key in dataset.keys():
        trace = go.Bar(
            x=newdf['pptyp'].copy(),
            y=newdf[key].copy(),
            name=key
            )
        graph_datalist.append(trace)
    
    layout = go.Layout(
        barmode = 'group',
        xaxis={'type':'category', 'automargin':True},
        yaxis={'title': dpurp + ' ' + dataset_type + ' per Person', 'zeroline':False},
        hovermode='closest',
        autosize=True,
        font=dict(family='Segoe UI', color='#7f7f7f')
        )
    
    return tp, tppp, t, {'data': graph_datalist, 'layout': layout}

