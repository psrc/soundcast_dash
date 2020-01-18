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
    return "{:,.2f}".format(x)

tab_4_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Totals"),
                html.Br(),
                html.Div(id='table-totals-container')
                ]
            ), style= {"margin-top": "20px"}
        )
    ]

@app.callback(
     Output('table-totals-container', 'children'),
     [Input('persons', 'children'),
      Input('households', 'children')]
     )
def create_totals_table(pers_json, hh_json):
    pers_tbl = json.loads(pers_json)
    hh_tbl = json.loads(hh_json)

    # calculate totals and collate into master dictionary
    alldict = {}
    dictlist = [pers_tbl, hh_tbl]
    dtypelist = ['Total Persons', 'Total Households']
    for adict, dtype in zip(dictlist, dtypelist):
        keys = list(adict)
        y = 'psexpfac' if adict == pers_tbl else 'hhexpfac' # if more than 2 data dicts?...
        sumlist = map(lambda x: pd.read_json(adict[x], orient = 'split')[y].sum(), keys)
        d = dict(zip(keys, sumlist))
        alldict[dtype] = d

    df = pd.DataFrame.from_dict(alldict, orient = 'index').reset_index().rename(columns = {'index': ' '})

    # format numbers with separator
    for i in range(1, len(df.columns)):
        df.iloc[:, i] = df.iloc[:, i].apply(format_number)
   
    t = html.Div([dash_table.DataTable(id='table-totals',
                              columns=[{"name": i, "id": i} for i in df.columns],
                                data=df.to_dict('rows'),
                                style_cell = {
                                    'font-family':'Segoe UI',
                                    'font-size': 14,
                                    'text-align': 'center'}
                                )])
    return t
        