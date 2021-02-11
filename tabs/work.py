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

def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)

def datatable_format_number(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': ',.' + str(decimal_places) + 'f'}}

def datatable_format_percent(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': '.' + str(decimal_places) + '%'}}

# Tab Work Layout
tab_work_layout = [
    html.H6('Work'),
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Work-From-Home Workers by County"),
                dbc.RadioItems(
                    id='work-county-data-type',
                    options=[{'label': i, 'value': i} for i
                             in ['Total', 'Distribution']],
                    value='Total',
                    inline=True
                    ),
                html.Br(),
                html.Div(id='table-totals-container-work'),
                ]
            ), style={"margin-top": "20px"}
        ),
    html.Div(id='dummy_div7')
]

tab_work_filter = [
    dbc.Card(
        [
            dbc.CardHeader(html.H1('Graph')),
            dbc.CardBody(
                [
                    dbc.Label('Person Type:'),
                    dbc.RadioItems(
                        id='work-person-type',
                        options=[{'label': i, 'value': i} for i in
                                 ['On-site Workers','Work-from-Home Workers',
                                  'Non-Workers']],
                        value='On-site Workers'
                    ),
                    html.Br(),
                ],
            ),  # end of CardBody
        ],
        className='aside-card'
    )  # of Card
    ]

# Work tab ------------------------------------------------------------------
@app.callback(
    Output('table-totals-container-work', 'children'),
    [Input('work-person-type', 'value'),
     Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('work-county-data-type', 'value'),
     Input('dummy_div7', 'children')]
    )
def update_visuals(person_type, scenario1, scenario2, scenario3, data_type, aux):

    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_totals_table(work_home_tbl, work_from_home_tours_tbl, trip_dist_tbl, 
                            person_type_tbl, data_type, person_type):

        datalist = []
        datalist2 = []
        datalist3 = []
        for key in work_home_tbl.keys():
            df = work_home_tbl[key]
            df_pptyp = person_type_tbl[key]
            df.index = df['person_county']
            df.drop('person_county', axis=1, inplace=True)
            person_total = df['psexpfac'].sum()    # Total WFH workers

            if data_type == 'Distribution':
                df['psexpfac'] = df['psexpfac']/df['psexpfac'].sum()
                #df['psexpfac'] = df['psexpfac'].apply(functools.partial(format_percent, decimal_places=1))
            else:
                #format_number_dp = functools.partial(format_number, decimal_places=0)
                df.loc['Total',:] = df['psexpfac'].sum(axis=0)
                #df['psexpfac'] = df['psexpfac'].apply(functools.partial(format_number, decimal_places=0))

            df.rename(columns={'psexpfac': key}, inplace=True)
            df = df.reset_index()
            datalist.append(df)
     
            # Tour Rates
            df = work_from_home_tours_tbl[key]
            if person_type == 'On-site Workers':
                df = df[df['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]
                person_total = df_pptyp[df_pptyp['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]['psexpfac'].sum()
            elif person_type == 'Non-Workers':
                df = df[-df['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]
                person_total = df_pptyp[-df_pptyp['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]['psexpfac'].sum()
            df = df.groupby('pdpurp').sum()[['toexpfac']]
            df = df.reset_index()
            df['toexpfac'] = df['toexpfac']/person_total
            df.rename(columns={'toexpfac': key}, inplace=True)

            datalist2.append(df)

            # Trip Distance
            df = trip_dist_tbl[key]
            if person_type == 'On-site Workers':
                df = df[df['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]
            elif person_type == 'Non-Workers':
                df = df[-df['pptyp'].isin(['Full-Time Worker','Part-Time Worker'])]
            df = df.groupby(['dpurp','travdist_bin']).sum()[['trexpfac']].reset_index()
            df['wt_sum'] = df['trexpfac']*1.0*df['travdist_bin']
            result = {}
            for purp in pd.unique(df['dpurp']):
                _df = df[df['dpurp'] == purp]
                result[purp] = _df['wt_sum'].sum()/_df['trexpfac'].sum()
                
            df = pd.DataFrame.from_dict(result, orient='index').reset_index()
            df.columns = ['Purpose',key]

            datalist3.append(df)

        df_scenarios = pd.merge(datalist[0], datalist[1], on='person_county')
        if len(datalist) == 3:
            df_scenarios = pd.merge(df_scenarios, datalist[2], on='person_county')

        # Calculate tour rates
        df_tour_scenarios = pd.merge(datalist2[0], datalist2[1], on=['pdpurp'])
        if len(datalist) == 3:
            df_tour_scenarios = pd.merge(df_tour_scenarios, datalist2[2], on=['pdpurp'])
        format_number_dp = functools.partial(format_number, decimal_places=2)
        for i in range(1, len(df_tour_scenarios.columns)):
            df_tour_scenarios.iloc[:, i] = df_tour_scenarios.iloc[:, i].apply(format_number_dp)

        df_trip_distance = pd.merge(datalist3[0], datalist3[1], on='Purpose')
        if len(datalist) == 3:
            df_trip_distance = pd.merge(df_trip_distance, datalist3[2], on='Purpose')
        for i in range(1, len(df_trip_distance.columns)):
            df_trip_distance.iloc[:, i] = df_trip_distance.iloc[:, i].apply(format_number_dp)

        tour_rate_header = "Tour Rate by Purpose for " + person_type
        avg_trip_dist_header = "Average Trip Distance by Purpose for " + person_type

        # Formating columns from within dash_table to avoid sorting errors
        cols_df_scenarios = []
        for col in df_scenarios.columns:
            if col == 'person_county':
                cols_df_scenarios.append({"name": col, "id": col})
            elif data_type == 'Distribution':
                cols_df_scenarios.append(datatable_format_percent(col, 1))
            else:
                cols_df_scenarios.append(datatable_format_number(col, 0))
        
        t = html.Div(
            [dash_table.DataTable(id='table-totals-work',
                                  #columns=[{"name": i, "id": i} for i in df_scenarios.columns],
                                  columns= cols_df_scenarios,
                                  data=df_scenarios.to_dict('rows'),
                                  sort_action="native",
                                  style_cell={
                                      'font-family': 'Pragmatica Light',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  ),
            html.Br(),
            html.H2(tour_rate_header),
            dash_table.DataTable(id='table-totals-work2',
                                  columns=[{"name": i, "id": i} for i in df_tour_scenarios.columns],
                                  data=df_tour_scenarios.to_dict('rows'),
                                  sort_action="native",
                                  style_cell={
                                      'font-family': 'Pragmatica Light',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  ),
            html.Br(),
            html.H2(avg_trip_dist_header),
            dash_table.DataTable(id='table-totals-work3',
                                  columns=[{"name": i, "id": i} for i in df_trip_distance.columns],
                                  data=df_trip_distance.to_dict('rows'),
                                  sort_action="native",
                                  style_cell={
                                      'font-family': 'Pragmatica Light',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  ),
             ]
            )

        return t
   
    scenario_list = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
    
    work_home_tbl = compile_csv_to_dict('wfh_county.csv', vals)
    person_type_tbl = compile_csv_to_dict('person_type.csv', vals)
    

    dataset_source = {'On-site Workers': 'non_wfh_tours.csv',
                      'Work-from-Home Workers': 'work_from_home_tours.csv',
                      'Non-Workers':'non_wfh_tours.csv'}
    distance_data_source = {'On-site Workers': 'trip_distance_non_wfh.csv',
                      'Work-from-Home Workers': 'trip_distance_wfh.csv',
                      'Non-Workers':'trip_distance.csv'}
    # Select tours based on filters
    work_from_home_tours_tbl = compile_csv_to_dict(dataset_source[person_type], vals)
    trip_dist_tbl = compile_csv_to_dict(distance_data_source[person_type], vals)

    totals_table = create_totals_table(work_home_tbl, work_from_home_tours_tbl, trip_dist_tbl,
                                        person_type_tbl, data_type, person_type)

    return totals_table
