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

def format_number(x):
    return "{:,.0f}".format(x)

#def format_number(x, decimal_places):
#    formula = "{:,." + str(decimal_places) + "f}"
#    return formula.format(x)

tab_4_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Totals"),
                html.Br(),
                html.Div(id='table-totals-container'),
                ]
            ), style= {"margin-top": "20px"}
        ),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Household Size"),
                        dcc.Graph(id='household-size-graph'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=7
            ), # end Col
        dbc.Col(
              dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Auto Ownership"),
                        dcc.Graph(id='auto-own-graph'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=5
            ) # end Col
        ]
        ), # end Row
    
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("Workers"),
                        html.Br(),
                        html.Div(id='table-wrkr-container'),
                
                        ]
                    ), style= {"margin-top": "20px"}
                ),
            width=5
            ), # end col
        ]),
    
    html.Div(id='dummy_div3')
    ]

@app.callback(
    [Output('table-totals-container', 'children'),
     Output('household-size-graph', 'figure'),
     Output('auto-own-graph', 'figure'),
     Output('table-wrkr-container', 'children')],
     [Input('persons', 'children'),
      Input('households', 'children'),
      Input('workers', 'children'),
      Input('auto_own', 'children'),
      Input('dummy_div3', 'children')]
    )
#def update_visuals(hh_json, auto_json, aux):
def update_visuals(pers_json, hh_json, wrkrs_json, auto_json, aux):
    def create_totals_table(pers_tbl, hh_tbl, wrkrs_tbl):
        # calculate totals and collate into master dictionary
        alldict = {}
        dictlist = [pers_tbl, hh_tbl]
        dtypelist = ['Total Persons', 'Total Households']
        expfaclist = ['psexpfac', 'hhexpfac']
        for adict, dtype, expfac in zip(dictlist, dtypelist, expfaclist):
            keys = list(adict)
            sumlist = map(lambda x: pd.read_json(adict[x], orient = 'split')[expfac].sum(), keys)
            d = dict(zip(keys, sumlist))
            alldict[dtype] = d
    
        wrkr_keys = list(wrkrs_tbl)
        wrkr_dfs = map(lambda x: pd.read_json(wrkrs_tbl[x], orient = 'split'), wrkr_keys)
        wrkr_sumlist = [wrkr_df[wrkr_df['pwtaz'] >= 0]['psexpfac'].sum() for wrkr_df in wrkr_dfs]

        wd = dict(zip(wrkr_keys, wrkr_sumlist))  
        alldict.update({'Total Workers': wd})
        df = pd.DataFrame.from_dict(alldict, orient = 'index').reset_index().rename(columns = {'index': ' '})

        # format numbers with separator
        for i in range(1, len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].apply(format_number)
   
        t = html.Div(
            [dash_table.DataTable(id='table-totals',
                                  columns=[{"name": i, "id": i} for i in df.columns],
                                  data=df.to_dict('rows'),
                                  style_cell = {
                                      'font-family':'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )
        return t

    def create_simple_bar_graph(table, xcol, weightcol, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            df = pd.read_json(table[key], orient='split')
            df = df[[xcol, weightcol]].groupby(xcol).sum()[[weightcol]]
            df = df.reset_index()

            trace = go.Bar(
                x=df[xcol].copy(),
                y=df[weightcol].copy(),
                name=key
                )
            datalist.append(trace)

        layout = go.Layout(
            barmode = 'group',
            xaxis={'title': xaxis_title, 'type':'category'},
            yaxis={'title': yaxis_title, 'zeroline':False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
        return {'data': datalist, 'layout': layout}
    
    def create_workers_table(wrkrs_tbl):
        #workers_tbl = json.loads(wrkrs_tbl)
        taz_geog = pd.read_sql_table('taz_geography', 'sqlite:///R:/e2projects_two/SoundCast/Inputs/dev/db/soundcast_inputs.db')

        datalist = []
        for key in wrkrs_tbl.keys():
            df = pd.read_json(wrkrs_tbl[key], orient='split')
    
            df = df.merge(taz_geog, left_on='hhtaz', right_on='taz')
            df.rename(columns={'geog_name':'hh_county'}, inplace=True)

            df = df.merge(taz_geog, left_on='pwtaz', right_on='taz')
            df.rename(columns={'geog_name':'work_county'}, inplace=True)

            df.drop(['taz_x', 'taz_y'], axis=1, inplace=True)
            df = df.groupby(['hh_county','work_county']).sum()[['psexpfac']]

            df.rename(columns = {'psexpfac': key}, inplace=True)
            df = df.reset_index()
    
            datalist.append(df)
    
        df_scenarios = pd.merge(datalist[0], datalist[1], on = ['hh_county','work_county'])
        df_scenarios.rename(columns = {'hh_county': 'Household County', 'work_county': 'Work County'}, inplace=True)
        # format numbers with separator
        for i in range(2, len(df_scenarios.columns)):
            df_scenarios.iloc[:, i] = df_scenarios.iloc[:, i].apply(format_number)

        t = html.Div(
            [dash_table.DataTable(id='table-workers',
                                  columns=[{"name": i, "id": i} for i in df_scenarios.columns],
                                  data=df_scenarios.to_dict('rows'),
                                  style_cell_conditional = [
                                      {
                                          'if': {'column_id': i},
                                          'textAlign': 'left'
                                          } for i in ['Household County', 'Work County']
                                      ],
                                  style_cell = {
                                      'font-family':'Segoe UI',
                                      'font-size': 11,
                                      'text-align': 'center'}
                                  )
                ]
            )

        return t

    pers_tbl = json.loads(pers_json)
    hh_tbl = json.loads(hh_json)
    wrkrs_tbl = json.loads(wrkrs_json)
    auto_tbl = json.loads(auto_json)

    totals_table = create_totals_table(pers_tbl, hh_tbl, wrkrs_tbl)
    hh_graph = create_simple_bar_graph(hh_tbl, 'hhsize', 'hhexpfac', 'Household Size', 'Households')
    auto_graph = create_simple_bar_graph(auto_tbl, 'hhvehs', 'hhexpfac', 'Number of Vehicles', 'Households')
    wrkr_table = create_workers_table(wrkrs_tbl)
    
    return totals_table, hh_graph, auto_graph, wrkr_table

    
#@app.callback(
#     Output('table-totals-container', 'children'),
#     [Input('persons', 'children'),
#      Input('households', 'children'),
#      Input('workers', 'children')
#      ]
#     )
#def create_totals_table(pers_json, hh_json, wrkrs_json):
#    pers_tbl = json.loads(pers_json)
#    hh_tbl = json.loads(hh_json)
#    wrkrs_tbl = json.loads(wrkrs_json)

#    # calculate totals and collate into master dictionary
#    alldict = {}
#    dictlist = [pers_tbl, hh_tbl]
#    dtypelist = ['Total Persons', 'Total Households']
#    expfaclist = ['psexpfac', 'hhexpfac']
#    for adict, dtype, expfac in zip(dictlist, dtypelist, expfaclist):
#        keys = list(adict)
#        sumlist = map(lambda x: pd.read_json(adict[x], orient = 'split')[expfac].sum(), keys)
#        d = dict(zip(keys, sumlist))
#        alldict[dtype] = d
    
#    wrkr_keys = list(wrkrs_tbl)
#    wrkr_dfs = map(lambda x: pd.read_json(wrkrs_tbl[x], orient = 'split'), wrkr_keys)
#    wrkr_sumlist = [wrkr_df[wrkr_df['pwtaz'] >= 0]['psexpfac'].sum() for wrkr_df in wrkr_dfs]

#    wd = dict(zip(wrkr_keys, wrkr_sumlist))  
#    alldict.update({'Total Workers': wd})
#    df = pd.DataFrame.from_dict(alldict, orient = 'index').reset_index().rename(columns = {'index': ' '})

#    # format numbers with separator
#    for i in range(1, len(df.columns)):
#        df.iloc[:, i] = df.iloc[:, i].apply(format_number)
   
#    t = html.Div(
#        [dash_table.DataTable(id='table-totals',
#                              columns=[{"name": i, "id": i} for i in df.columns],
#                              data=df.to_dict('rows'),
#                              style_cell = {
#                                  'font-family':'Segoe UI',
#                                  'font-size': 14,
#                                  'text-align': 'center'}
#                              )
#         ]
#        )
#    return t

#@app.callback(
#    Output('table-wrkr-container', 'children'),
#     #Output('wrkr-graph', 'figure')   
#    [Input('workers', 'children'),
#     Input('dummy_div3', 'children')]
#    )
#def create_workers_table(workers_json, aux):
#    workers_tbl = json.loads(workers_json)
#    taz_geog = pd.read_sql_table('taz_geography', 'sqlite:///R:/e2projects_two/SoundCast/Inputs/dev/db/soundcast_inputs.db')

#    datalist = []
#    for key in workers_tbl.keys():
#        df = pd.read_json(workers_tbl[key], orient='split')
    
#        df = df.merge(taz_geog, left_on='hhtaz', right_on='taz')
#        df.rename(columns={'geog_name':'hh_county'}, inplace=True)

#        df = df.merge(taz_geog, left_on='pwtaz', right_on='taz')
#        df.rename(columns={'geog_name':'work_county'}, inplace=True)

#        df.drop(['taz_x', 'taz_y'], axis=1, inplace=True)
#        df = df.groupby(['hh_county','work_county']).sum()[['psexpfac']]

#        df.rename(columns = {'psexpfac': key}, inplace=True)
#        df = df.reset_index()
    
#        datalist.append(df)
    
#    df_scenarios = pd.merge(datalist[0], datalist[1], on = ['hh_county','work_county'])
#    df_scenarios.rename(columns = {'hh_county': 'Household County', 'work_county': 'Work County'}, inplace=True)
#    # format numbers with separator
#    for i in range(2, len(df_scenarios.columns)):
#        df_scenarios.iloc[:, i] = df_scenarios.iloc[:, i].apply(format_number)

#    t = html.Div(
#        [dash_table.DataTable(id='table-workers',
#                              columns=[{"name": i, "id": i} for i in df_scenarios.columns],
#                              data=df_scenarios.to_dict('rows'),
#                              style_cell_conditional = [
#                                  {
#                                      'if': {'column_id': i},
#                                      'textAlign': 'left'
#                                      } for i in ['Household County', 'Work County']
#                                  ],
#                              style_cell = {
#                                  'font-family':'Segoe UI',
#                                  'font-size': 11,
#                                  'text-align': 'center'}
#                              )
#            ]
#        )

#    return t

  


        