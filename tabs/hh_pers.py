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
import dash_table
import functools
import plotly.express as px

def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)

# Tab Households and Persons Layout
tab_hh_pers_filter = [
    dbc.Card(
        [
            dbc.CardHeader(html.H1('Graph')),
            dbc.CardBody(
                [
                    dbc.Label('Select dataset:'),
                    dbc.RadioItems(
                        id='hhpers-dataset-type',
                        options=[{'label': i, 'value': i} for i in
                                 ['Household Size', 'Auto Ownership',
                                  'Workers by County']],
                        value='Household Size'
                    ),
                    html.Br(),
                    html.Div(id='hhpers-dummy-dataset-type'),
                ],
            ),  # end of CardBody
        ],
        className='aside-card'
    )  # of Card
    ]

tab_hh_pers_layout = [
    html.H6('HH & Persons'),
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Totals"),
                html.Br(),
                html.Div(id='table-totals-container'),
                ]
            ), style={"margin-top": "20px"}
        ),
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='hhpers-graph-header'),
                        dcc.Graph(id='hhpers-graph-container'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ),  # end Row
    html.Div(id='dummy_div3')
    ]

# Households and Persons tab ------------------------------------------------------------------
@app.callback(
    [Output('table-totals-container', 'children'),
     Output('hhpers-graph-header', 'children'),
     Output('hhpers-graph-container', 'figure')
     ],
    [Input('hhpers-dataset-type', 'value'),
     Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('dummy_div3', 'children')]
    )
def update_visuals(data_type, scenario1, scenario2, scenario3, aux):
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_totals_table(pers_tbl, hh_tbl, wrkrs_tbl):
        # calculate totals and collate into master dictionary
        alldict = {}

        # persons
        keys = pers_tbl.keys()
        dtype = 'Total Persons'
        expfac = 'psexpfac'
        sum = map(lambda x: pd.DataFrame(pers_tbl[x])[expfac].sum(), keys)
        d = dict(zip(keys, sum))
        alldict[dtype] = d

        # households
        hh_sum = map(lambda x: hh_tbl[x]['hhexpfac'].sum(), hh_tbl.keys())
        hh_d = dict(zip(hh_tbl.keys(), hh_sum))
        alldict['Total Households'] = hh_d

        # workers
        pers_df = map(lambda x: pd.DataFrame(pers_tbl[x]), keys)
        pers_dict = dict(zip(keys, pers_df))
        wrkrs_df = map(lambda x: pers_dict[x][pers_dict[x]['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])][expfac].sum(), keys)
        wrkrs_dict = dict(zip(keys, wrkrs_df))
        alldict['Total Workers'] = wrkrs_dict

        df = pd.DataFrame.from_dict(alldict, orient='index').reset_index().rename(columns={'index': ' '})

        # format numbers with separator
        format_number_dp = functools.partial(format_number, decimal_places=0)
        for i in range(1, len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].apply(format_number_dp)

        t = html.Div(
            [dash_table.DataTable(id='table-totals',
                                  columns=[{"name": i, "id": i} for i in df.columns],
                                  data=df.to_dict('rows'),
                                  style_cell={
                                      'font-family': 'Pragmatica Light',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )
        return t

    def create_simple_bar_graph(table, xcol, weightcol, xaxis_title, yaxis_title):
        datalist = []
        for idx, key in enumerate(table.keys()):
            df = table[key]
            df = df[[xcol, weightcol]].groupby(xcol).sum()[[weightcol]]
            df = df.reset_index()

            trace = go.Bar(
                x=df[xcol].copy(),
                y=df[weightcol].copy(),
                name=key,
                marker_color=config['color_list'][idx]
                )
            datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type': 'category'},
            yaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            margin={'t':20},
            font=dict(family='Pragmatica Light', color='#7f7f7f')
            )
        return {'data': datalist, 'layout': layout}

    def create_workers_table(wrkrs_tbl):

        df = pd.DataFrame()
        for key in wrkrs_tbl.keys():
            _df = wrkrs_tbl[key]
            _df = _df.groupby(['person_county','person_work_county']).sum()[['psexpfac']]
            _df['Scenario'] = key
            df = df.append(_df)
        df.rename(columns={'person_county': 'Home County', 'person_work_county': 'Work County'}, inplace=True)

        return df

    scenario_list = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
   
    pers_tbl = compile_csv_to_dict('person_type.csv', vals)
    hh_tbl = compile_csv_to_dict('household_size_vehs_workers.csv', vals)
    wrkrs_tbl = compile_csv_to_dict('work_flows.csv', vals)
    auto_tbl = compile_csv_to_dict('auto_ownership.csv', vals)

    totals_table = create_totals_table(pers_tbl, hh_tbl, wrkrs_tbl)

    if data_type == 'Household Size':
        agraph = create_simple_bar_graph(hh_tbl, 'hhsize', 'hhexpfac', 'Household Size', 'Households')
        agraph_header = 'Household Size'
    elif data_type == 'Auto Ownership':
        agraph = create_simple_bar_graph(auto_tbl, 'hhvehs', 'hhexpfac', 'Number of Vehicles', 'Households')
        agraph_header = 'Auto Ownership'
    elif data_type == 'Workers by County':
        df = create_workers_table(wrkrs_tbl)
        df = df.reset_index()

        agraph = px.bar(
            df,
            height=900,
            #width=950,
            barmode='group',
            facet_row='person_county',
            x='person_work_county',
            y='psexpfac',
            color='Scenario'
        )
        agraph.update_layout(font=dict(family='Pragmatica Light', color='#7f7f7f'))
        agraph.for_each_annotation(lambda a: a.update(text=a.text.replace("Household County=", "")))
        agraph.for_each_trace(lambda t: t.update(name=t.name.replace("Scenario=", "")))
        agraph_header = 'Workers by Household County by Work County'

    return totals_table, agraph_header, agraph
