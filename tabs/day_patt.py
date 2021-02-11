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
import functools
import dash_table

def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)

# Tab Day Pattern Layout
tab_day_pattern_filter = [
    dbc.Card(
        [
            dbc.CardHeader(html.H1('Select')),
            dbc.CardBody(
                [
                    dbc.Label('Day Pattern Type:'),
                    dbc.RadioItems(
                        id='dpatt-dataset-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Tours', 'Trips']],
                        value='Tours'
                    ),
                    html.Br(),
                    dbc.Label('Format Type:'),
                    dbc.RadioItems(
                        id='dpatt-format-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Percent', 'Per Person']],
                        value='Percent'
                    ),
                    html.Br(),
                    html.Div(id='dummy-dataset-type'),
                    html.Div(id='dummy-format-type'),
                ],
        
            ),  # end of CardBody
            dbc.CardHeader(html.H1('Day Pattern by Person Type'),
                           className='additional-header'),
            dbc.CardBody(
                [
                    dbc.Label('Destination Purpose:'),
                    dcc.Dropdown(
                        value='Work',
                        clearable=False,
                        id='dpatt-dpurp-dropdown'
                    ),
                    html.Br(),
                    html.Div(id='dummy_div4'),
                ],
            )  # end of CardBody
        ],  # end of Card
        className='aside-card'
    ),  # end of Card
]

tab_day_pattern_layout = [
    html.H6('Day Pattern'),
    dbc.Row(children=[
        dbc.Col(            
            # insert top table: Totals
            dbc.Card(
                  dbc.CardBody(
                        [
                            html.H2(id='dpatt-tot-header'), 
                            html.Div(id='dpatt-tot-container'),
                        ]
                        ), style={"margin-top": "20px"}
                ), # end top table card
            )
        ]),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-gen-header'), 
                        html.Div(id='dpatt-table-container')
                    ]
                    ), style={"margin-top": "20px"}
                ), # end card
            #width=6
            ),  # end Col
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(id='dpatt-graph-container')
                    ]
                    ), style={"margin-top": "20px"}
                ),
            #width=6
            )  # end Col
         ]
        ),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-pptyp-purpose-header'),
                        html.Div(id='dpatt-table-pptyp-purpose-container')
                    ]
                ),
                style={"margin-top": "20px"}
            ),
            width=6
        ),  # end Col
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(id='dpatt-graph-pptyp-purpose'),

                    ]
                ), style={"margin-top": "20px"}
            ),
            width=6
        ),  # end Col
    ]
    ),  # end Row

    html.Div(id='dummy_div5'),
]

# Day Pattern tab ------------------------------------------------------------
# load drop downs
@app.callback(
    Output('dpatt-dpurp-dropdown', 'options'),
    [Input('dummy_div4', 'children')])
def dpurp_dropdown(aux):
    return [{'label': i, 'value': i} for i in config['trip_purpose_list'] if i != 'All']

# dynamic headers
@app.callback(
    [Output('dpatt-tot-header', 'children'),
     Output('dpatt-gen-header', 'children'),
     Output('dpatt-pptyp-purpose-header', 'children')],
    [Input('dpatt-dataset-type', 'value'),
     Input('dpatt-format-type', 'value'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')])
def update_headers(dataset_type, format_type, dpurp, aux, aux1):
    tot_header = "All " + dataset_type
    if format_type == 'Percent':
        gen_header = 'Percent of' + ' ' + dataset_type + ' by Purpose'
        header_pptyp_dpurp = 'Percent of ' + dpurp + ' ' + dataset_type + ' by Person Type'
    else:
        gen_header = dataset_type + ' per Person by Purpose'
        header_pptyp_dpurp = dpurp + ' ' + dataset_type + ' per Person by Person Type'

    return tot_header, gen_header, header_pptyp_dpurp 

# all content, render as DashTables + graphs
@app.callback(
    [Output('dpatt-tot-container', 'children'),
     Output('dpatt-table-container', 'children'),
     Output('dpatt-graph-container', 'figure'),
     Output('dpatt-table-pptyp-purpose-container', 'children'),
     Output('dpatt-graph-pptyp-purpose', 'figure')],
    [Input('dpatt-dataset-type', 'value'),
     Input('dpatt-format-type', 'value'),
     Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def update_visuals(dataset_type, format_type, scenario1, scenario2, scenario3, dpurp,
                   aux, aux1):
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)
    def calc_dpatt_per_person(table, group_cols_list, weight_name, key):
        df = table.copy()
        group_cols_list.append(key)
        df['day_pattern_per_person'] = df[weight_name]/df['psexpfac']
        df = df.rename(columns={'day_pattern_per_person': key})
        df = df[group_cols_list]
        return df

    def calc_delta(table, keyslist, old_colname, new_colname, decimal_places,
                   percent_delta=True):
        format_number_two_dp = functools.partial(format_number,
                                                 decimal_places=decimal_places)
        table['Difference'] = table[keyslist[0]] - table[keyslist[1]]
        if percent_delta:
            table['Percent Difference'] = (table['Difference']/table[keyslist[1]]) * 100
        # format numbers with separator
        for i in range(1, len(table.columns)):
            table.iloc[:, i] = table.iloc[:, i].apply(format_number_two_dp)
        table = table.rename(columns={old_colname: new_colname})
        return table

    def create_dash_table(id_name, table, index_list, fontsize):
        t = html.Div(
            [
                dash_table.DataTable(
                    id=id_name,
                    columns=[{"name": i, "id": i} for i in table.columns],
                    data=table.to_dict('rows'),
                    style_cell_conditional=[
                        {
                            'if': {'column_id': i},
                            'textAlign': 'left'
                        } for i in index_list
                    ],
                    style_cell={
                        'font-family': 'Pragmatica Light',
                        'font-size': fontsize,
                        'text-align': 'center'}
                )
            ]
        )
        return t

    def create_graph_data(dataset, table, x_col):
        graph_gen_table = []
        for idx, key in enumerate(dataset.keys()):
            trace = go.Bar(
                x=table[x_col].copy(),
                y=table[key].copy(),
                name=key,
                marker_color=config['color_list'][idx]
                )
            graph_gen_table.append(trace)
        return graph_gen_table

    def create_graph_layout(y_title):
        layout_gen_table = go.Layout(
            barmode='group',
            xaxis={'type': 'category', 'automargin': True},
            yaxis={'title': y_title, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            margin={'t':20},
            font=dict(family='Pragmatica Light', color='#7f7f7f')
            )
        return layout_gen_table 

    scenario_list  = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]

    tours = compile_csv_to_dict('tour_purpose_mode.csv', vals)
    trips = compile_csv_to_dict('trip_purpose_mode.csv', vals)
    pers = compile_csv_to_dict('person_type.csv', vals)

    if dataset_type == 'Tours':
        dataset = tours
        dataset_weight_col = 'toexpfac'
        dataset_dpurp_col = 'pdpurp'
    else:
        dataset = trips
        dataset_weight_col = 'trexpfac'
        dataset_dpurp_col = 'dpurp'

    datalist = []  # X per person by person type and purpose 
    datalist_perc = [] # X by person type and purpose (percent)
    datalist_all_dpurp = []  # X per person by purpose
    datalist_dpurp_gen = []  # X by purpose (percent)

    keys = dataset.keys()
    keyslist = list(keys)
    if "None" in keyslist: keyslist.remove("None")

    ## create total table
    alldict = {}
    # sum dataset
    dataset_sum = map(lambda x: pd.DataFrame(dataset[x])[dataset_weight_col].sum(), keys)
    dataset_dict = dict(zip(keys, dataset_sum))
    alldict['Total ' + dataset_type] = dataset_dict
    # sum persons
    pkeys = pers.keys()
    dtype = 'Total Persons'
    expfac = 'psexpfac'
    sum = map(lambda x: pd.DataFrame(pers[x])[expfac].sum(), pkeys)
    d = dict(zip(pkeys, sum))
    alldict[dtype] = d
    # compile and calculate per person
    df_tot = pd.DataFrame.from_dict(alldict, orient='columns')
    df_tot[dataset_type + ' per Person'] = df_tot['Total ' + dataset_type]/df_tot['Total Persons']
    df_tot[dataset_type + ' per Person'] = df_tot[dataset_type + ' per Person'].round(2)
    df_tot = df_tot.reset_index().rename(columns={'index': 'Scenario'})

    # format numbers with separator
    format_number_dp = functools.partial(format_number, decimal_places=0)
    for i in range(1, len(df_tot.columns)-1):
        df_tot.iloc[:, i] = df_tot.iloc[:, i].apply(format_number_dp)

    tot_table = create_dash_table('dpatt-tot-tbl', df_tot, ['Scenario'], 13) 
         
    # generate 'by Purpose' tables
    for key in keys:
        df = pd.DataFrame(dataset[key])

        df_dpurp_gen = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns={dataset_weight_col: key})
        datalist_dpurp_gen.append(df_dpurp_gen[[dataset_dpurp_col, key]]) # X by purpose (percent)

        df_pers = pd.DataFrame(pers[key])
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        
        # X per person by purpose
        df_dpurp = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp['psexpfac'] = df_pers['psexpfac'].sum()
        datalist_all_dpurp.append(calc_dpatt_per_person(df_dpurp, [dataset_dpurp_col], dataset_weight_col, key))
        
        # X per person by person type and purpose 
        df = df.groupby(['pptyp', dataset_dpurp_col]).sum()[[dataset_weight_col]].reset_index().merge(df_pers, on='pptyp')
        df_ptype = df[df[dataset_dpurp_col] == dpurp]
        datalist.append(calc_dpatt_per_person(df_ptype, ['pptyp', dataset_dpurp_col], dataset_weight_col, key)) 
        
        # X by person type and purpose (percent)
        df_ptype_perc = df_ptype.copy()
        df_ptype_perc = df_ptype_perc[['pptyp', dataset_dpurp_col, dataset_weight_col]]
        df_ptype_perc = df_ptype_perc.rename(columns={dataset_weight_col: key})
        datalist_perc.append(df_ptype_perc)

    newdf_dpurp_gen = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=dataset_dpurp_col), datalist_dpurp_gen) # X by purpose (percent)
    newdf_dpurp = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=dataset_dpurp_col), datalist_all_dpurp)  # X per person by purpose
    newdf = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=['pptyp', dataset_dpurp_col]), datalist) # X per person by person type and purpose 
    newdf_perc = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=['pptyp', dataset_dpurp_col]), datalist_perc) # X by person type and purpose (percent)
    
    ## generate final tables according to filters
    if format_type == 'Percent':
        tp_tbl = newdf_dpurp_gen.copy()
        for key in keyslist:
            tp_tbl[key] = (tp_tbl[key]/tp_tbl[key].sum()) * 100
        tp_tbl = calc_delta(tp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2, percent_delta=False)
   
        gen_table = create_dash_table('dpatt-gen-table-percent', tp_tbl, ['Destination Purpose'], '.7vw')
        graph_data = create_graph_data(dataset, tp_tbl, 'Destination Purpose')
        graph_layout = create_graph_layout('Percent of ' + dataset_type)

        ## create dash table for X by person type and purpose (percent)
        datatbl = newdf_perc.copy()
        datatbl = datatbl.drop(dataset_dpurp_col, axis=1)
        for key in keyslist:
            datatbl[key] = (datatbl[key]/datatbl[key].sum()) * 100
        datatbl = calc_delta(datatbl, keyslist, 'pptyp', 'Person Type', 2, percent_delta=False)

        t = create_dash_table('dpatt-table-pptyp-purposes', datatbl, ['Person Type'], '.6vw')

        # create graph
        graph_data_pers_type = create_graph_data(dataset, datatbl, 'Person Type')
        graph_layout_pers_type = create_graph_layout('Percent of ' + dpurp + ' ' + dataset_type)

    else:
        tp_tbl = newdf_dpurp.copy()
        tp_tbl = calc_delta(tp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2)
        gen_table = create_dash_table('dpatt-gen-table-per-pers', tp_tbl, ['Destination Purpose'], '.7vw')
        graph_data = create_graph_data(dataset, tp_tbl, 'Destination Purpose')
        graph_layout = create_graph_layout(dataset_type + ' per Person')

        ## create dash table for X per person by person type and purpose
        datatbl = newdf.copy()
        datatbl = datatbl.drop(dataset_dpurp_col, axis=1)
        datatbl = calc_delta(datatbl, keyslist, 'pptyp', 'Person Type', 2)
        t = create_dash_table('dpatt-table-pptyp-purposes', datatbl, ['Person Type'], '.6vw')

        # create graph
        graph_data_pers_type = create_graph_data(dataset, newdf, 'pptyp')
        graph_layout_pers_type = create_graph_layout(dpurp + ' ' + dataset_type + ' per Person')

    return tot_table, gen_table, {'data': graph_data, 'layout': graph_layout}, t, {'data': graph_data_pers_type, 'layout': graph_layout_pers_type}
