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
    #return "{:,.2f}".format(x)

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

# all content, render as DashTables + graph
@app.callback(
    [Output('dpatt-table-perc-tours-dpurp-gen-container', 'children'),
     Output('dpatt-table-tours-dpurp-gen-container', 'children'), 
     Output('dpatt-table-tours-purpose-container', 'children'), 
     Output('dpatt-graph-tours-purpose', 'figure')],
    [Input('trips', 'children'),
     Input('tours', 'children'), 
     Input('persons', 'children'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def update_visuals(trips_json, tours_json, pers_json, dpurp, aux, aux1):
    
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

    print('compiling all essential data')
    # load all data
    trips = json.loads(trips_json)
    tours = json.loads(tours_json)
    pers = json.loads(pers_json)

    # if dataset selection == tours'toexpfac', else 'trexpfac'

    datalist = [] # tours per person by person type and purpose
    datalist_all_dpurp = [] # tours per person by purpose 
    datalist_dpurp_gen = [] # tours by purpose
    
    keys = tours.keys()
    keyslist = list(keys)

    for key in keys: 
        df = pd.read_json(tours[key], orient='split')

        df_dpurp_gen = df.groupby('pdpurp').sum()[['toexpfac']].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns = {'toexpfac': key})
        datalist_dpurp_gen.append(df_dpurp_gen[['pdpurp', key]])

        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        df = df.groupby(['pptyp', 'pdpurp']).sum()[['toexpfac']].reset_index().merge(df_pers, on = 'pptyp')

        df_dpurp = df.groupby('pdpurp').sum()[['toexpfac', 'psexpfac']].reset_index()
        datalist_all_dpurp.append(calc_dpatt_per_person(df_dpurp, ['pdpurp'], 'toexpfac', key))

        df_ptype = df[df['pdpurp'] == dpurp]
        datalist.append(calc_dpatt_per_person(df_ptype, ['pptyp', 'pdpurp'], 'toexpfac', key)) 
    
    newdf_dpurp_gen = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on='pdpurp'), datalist_dpurp_gen)
    newdf_dpurp = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on='pdpurp'), datalist_all_dpurp)
    newdf = functools.reduce(lambda df1, df2: pd.merge(df1,df2,on=['pptyp', 'pdpurp']), datalist)
    print('finished data compilation')

    # create percent of tours by purpose
    print('newdf_dpurp_gen difference')
    tp_tbl = newdf_dpurp_gen.copy()
    for key in keyslist:
        tp_tbl[key] = (tp_tbl[key]/tp_tbl[key].sum()) * 100
    tp_tbl = calc_delta(tp_tbl, keyslist, 'pdpurp', 'Destination Purpose', 2, percent_delta = False)
    tp = create_dash_table('dpatt-table-perc-tours-dpurp-gen', tp_tbl, ['Destination Purpose'], '.7vw')

    # create dash tables for tours per person and purpose
    print('newdf_dpurp difference')
    tppp_tbl = newdf_dpurp.copy()
    tppp_tbl = calc_delta(tppp_tbl, keyslist, 'pdpurp', 'Destination Purpose', 2)
    tppp = create_dash_table('dpatt-table-tours-dpurp-gen', tppp_tbl, ['Destination Purpose'], '.7vw')

    # create dash table for tours per person by person type and purpose
    print('newdf difference')
    datatbl = newdf.copy()
    datatbl= datatbl.drop('pdpurp', axis=1)
    datatbl = calc_delta(datatbl, keyslist, 'pptyp', 'Person Type', 2)
    t = create_dash_table('dpatt-table-tours-purposes', datatbl, ['Person Type'], '.6vw')
    
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
    
    layout = go.Layout(
        barmode = 'group',
        xaxis={'type':'category', 'automargin':True},
        yaxis={'title': dpurp + ' Tours per Person', 'zeroline':False},
        hovermode='closest',
        autosize=True,
        font=dict(family='Segoe UI', color='#7f7f7f')
        )
    
    return tp, tppp, t, {'data': graph_datalist, 'layout': layout}

