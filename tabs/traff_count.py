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
import plotly.express as px

def datatable_format_percent(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': '.' + str(decimal_places) + '%'}}

def datatable_format_number(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': ',.' + str(decimal_places) + 'f'}}

available_scenarios = [name for name in os.listdir('data')
                       if os.path.isdir(os.path.join('data', name))
                       and name != 'data']

# List of model scenarios
model_scenarios = []
for scen in available_scenarios:
    # Validation data only available for scenario runs, check if it exists before adding to available scen list
    fname_path = os.path.join('data', scen, 'daily_volume_county_facility.csv')
    if os.path.isfile(fname_path):
        model_scenarios.append(scen)

tab_traffic_counts_layout = [
    html.H6('Traffic Counts'),
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id='traffic-totals-header'),
            html.Br(),
            html.Div(id='traffic-totals-container'),
            ]
        ), style={"margin-top": "20px"}
    ),
    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='traffic-graffic-header'),
                        dcc.Graph(id='traffic-graffic-container',
                                figure={ 'data': [], 'layout': go.Layout()}),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ),  # end Row
    dbc.Row(children=[
     dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2(id='counts-scatterplot-header'),
                    dcc.Graph(id='counts-scatterplot-container',
                            figure={ 'data': [], 'layout': go.Layout()}),
                    ]
                ), style={"margin-top": "20px"}
            ),
        width=12
        ),  # end Col
    ]
    ),  # end Row
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id="screenlines-header"),
            html.Br(),
            html.Div(id='screenlines-container'),
            ]
        ), style={"margin-top": "20px"}
    ),
    dbc.Card(
    dbc.CardBody(
        [
            html.H2(id="externals-header"),
            html.Br(),
            html.Div(id='externals-container'),
            ]
        ), style={"margin-top": "20px"}
    ),
    
]

tab_traffic_counts_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
        dbc.CardBody(
            [
                dbc.Label('Validation Scenario:'),
                dcc.Dropdown(
                    value=model_scenarios[0],
                    clearable=False,
                    id='validation-scenario'
                ),
                html.Br(),
            ],
            ), style={"margin-top": "20px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('County:'),
                    dcc.Dropdown(
                        value='All',
                        clearable=False,
                        id='traffic-count-county'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            
            ),
            html.Div(id='dummy_div9'),
        ],
        className='aside-card',
        

    )]

# Traffic Counts Tab
# --------------------------------------------------------------------------------
@app.callback(
    [Output('traffic-count-county', 'options'),
     Output('validation-scenario', 'options')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value')])
def tour2_load_drop_downs(scen1, scen2, scen3):
    scen_list = []
    for scen in [scen1, scen2, scen3]:
        # Validation data only available for scenario runs, check if it exists before adding to available scen list
        fname_path = os.path.join('data', scen, 'daily_volume_county_facility.csv')
        if os.path.isfile(fname_path):
            scen_list.append(scen)

    return [[{'label': i, 'value': i} for i in config['county_list']], [{'label': i, 'value': i} for i in scen_list]]

# dynamic headers
@app.callback(
    [Output('traffic-graffic-header', 'children'),
     Output('counts-scatterplot-header', 'children'),
     Output('traffic-totals-header', 'children'),
     Output('screenlines-header', 'children'),
     Output('externals-header', 'children')],
    [Input('traffic-count-county', 'value')])
def update_headers(county):

    result = []
    header_dict = {}
    traffic_header = 'Traffic Counts '
    scatterplot_header = 'Count Locations '
    traffic_table_header = 'Volume by Facility Type '
    screenline_header = 'Screenlines '
    externals_header = 'External Stations '
    for header in [traffic_header, scatterplot_header, traffic_table_header,
                    screenline_header, externals_header]:
        if county != 'All':
            header += ': ' + county + ' County'
        result.append(header)

    return result

@app.callback(
    [Output('traffic-totals-container', 'children'),
    Output('traffic-graffic-container', 'figure'),
    Output('counts-scatterplot-container', 'figure'),
    Output('screenlines-container', 'children'),
    Output('externals-container', 'children')],
    [Input('traffic-count-county', 'value'),
     Input('validation-scenario', 'value'),
     Input('dummy_div9', 'children')]
    )
def update_visuals(county, selected_scen, aux):

    def create_totals_table(df, groupby_val, selected_scen, county='None'):

        if county != 'All' and county != 'None':
            df = df[df['county'] == county]
        df = df.groupby(groupby_val).sum().reset_index()[[groupby_val,'modeled','observed']]
        df['Percent Difference'] = ((df['modeled'] - df['observed'])/df['observed'])#*100
        #df['Percent Difference'] = df['Percent Difference'].map('{:,.2f}%'.format)
        df = df.sort_values('modeled', ascending=False)
        #for col in ['modeled','observed']:
        #    df[col] = df[col].map('{:,}'.format)
        df.rename(columns={'modeled':'Modeled', 'observed': 'Observed'}, inplace=True)
        column_list =[]
        for col in df.columns:
            if col not in ['Modeled', 'Observed', 'Percent Difference']:
                column_list.append({"name": col, "id": col})
            elif col in ['Modeled', 'Observed']:
                column_list.append(datatable_format_number(col, 0))
            elif col == 'Percent Difference':
                column_list.append(datatable_format_percent(col, 2))

        t = html.Div(
            [dash_table.DataTable(id='traffic-table-totals',
                                  #columns=[{"name": i, "id": i} for i in df.columns],
                                  columns= column_list,
                                  data=df.to_dict('rows'),
                                  sort_action="native",
                                  style_cell={
                                      'font-family': 'Pragmatica Light',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )
        return t

    def create_validation_bar_graph(df, xcol, observed_col, modeled_col, county, 
                                xaxis_title, yaxis_title):
        
        if county != 'All' and county != 'None':
            df = df[df['county'] == county]

        datalist = []
        for idx, colname in enumerate([observed_col, modeled_col]):
            trace = go.Bar(
                x=df[xcol].copy(),
                y=df[colname].copy(),
                name=colname,
                marker_color=config['validation_color_list'][idx]
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

    def create_scatterplot(df, county, xcol, ycol, xaxis_title, yaxis_title):

        if county != 'All':
            df = df[df['county'] == county]

        trace = go.Scatter(
                x=df[xcol].astype('float').copy(),
                y=df[ycol].astype('float').copy(),
                mode='markers',
                line_color=config['validation_color_list'][0]
                )

        layout = go.Layout(
            xaxis={'title': xaxis_title},
            yaxis={'title': yaxis_title},
            hovermode='closest',
            autosize=True,
            margin={'t':20},
            font=dict(family='Pragmatica Light', color='#7f7f7f')
            )
        return {'data': [trace], 'layout': layout}

    totals_table = ''
    agraph = {'data': [], 'layout': go.Layout()}
    scatter_graph = {'data': [], 'layout': go.Layout()}
    screenline_table = ''
    externals_table = ''
    if selected_scen is not None:

        counts_df = pd.read_csv(os.path.join('data',selected_scen, 'daily_volume_county_facility.csv'))
        counts_df.rename(columns={'@facilitytype': 'Facility'}, inplace=True)
        totals_table = create_totals_table(counts_df, 'Facility', selected_scen, county)
        county_counts_df = counts_df.groupby('county').sum().reset_index()
        agraph = create_validation_bar_graph(county_counts_df, 'county', 'observed', 'modeled', county, 'County', 'Daily Volume')
        agraph_header = 'Traffic Counts by County'

        # Scatter plot of counts
        scatter_df = pd.read_csv(os.path.join('data',selected_scen,'daily_volume.csv'))
        scatter_graph = create_scatterplot(scatter_df, county, 'observed', 'modeled', 'Observed', 'Modeled')

        # Screenlines
        screenlines_df = pd.read_csv(os.path.join('data',selected_scen,'screenlines.csv'))
        screenlines_df[['modeled','observed']] = screenlines_df[['modeled','observed']].astype('int')
        screenline_table = create_totals_table(screenlines_df, 'name', selected_scen, county)

        # Externals
        externals_df = pd.read_csv(os.path.join('data',selected_scen,'external_volumes.csv'))
        externals_df[['modeled','observed']] = externals_df[['modeled','observed']].astype('int')
        externals_table = create_totals_table(externals_df, 'location', selected_scen, county)

    return totals_table, agraph, scatter_graph, screenline_table, externals_table
