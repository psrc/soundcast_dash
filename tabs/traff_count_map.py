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

import plotly.offline as py


mapbox_access_token = 'pk.eyJ1IjoiZGlhbmFtYXJ0IiwiYSI6ImNraG9jc2txZTAyZnoydWwxaWpndjlpM3QifQ.E5n0-puztmkO2SJOteSVjQ'

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

tab_traffic_counts_map_layout = [
    html.H6('Traffic Counts Map'),
    
    dbc.Row(children=[
     dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2(id='counts-map-scatterplot-header'),
                    dcc.Graph(id='counts-map-scatterplot-graph-container',
                            figure={ 'data': [], 'layout': go.Layout(xaxis={'title': 'x title'},yaxis={'title': 'y title'})}),
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
                    html.H2(id='counts-map-scatterplot-header'),
                    dcc.Graph(id='counts-map-scatterplot-map-container',
                            config={'displayModeBar': True, 'scrollZoom': True}, style={'padding-bottom':'2px','padding-left':'2px','height':'100vh'}),
                    ]
                ), style={"margin-top": "20px"}
            ),
        width=12
        ),  # end Col
    ]
    ),  # end Row     
    
]

tab_traffic_counts_map_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
        dbc.CardBody(
            [
                dbc.Label('Validation Scenario:'),
                dcc.Dropdown(
                    value=model_scenarios[0],
                    clearable=False,
                    id='validation-scenario-map'
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
                        id='traffic-count-map-county'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            
            ),
            html.Div(id='dummy_div12'),
        ],
        className='aside-card',
        

    )]

# Traffic Counts Tab
# --------------------------------------------------------------------------------
# filters
@app.callback(
    [Output('traffic-count-map-county', 'options'),
     Output('validation-scenario-map', 'options')],
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
    [#Output('traffic-graffic-header', 'children'),
     Output('counts-map-scatterplot-header', 'children')],
    [Input('traffic-count-map-county', 'value')]) # Headers for All (no county selected) is not activated here, therefore no header shows up initially when no specific county is selected.
def update_headers(county):

    result = []
    header_dict = {}

    scatterplot_header = 'Count Locations '
    for header in [scatterplot_header]:
        if county != 'All':
            header += ': ' + county + ' County'
        result.append(header)
    
    return result


@app.callback(
    [Output('counts-map-scatterplot-graph-container', 'figure'),
     Output('counts-map-scatterplot-map-container', 'figure')],
    [Input('traffic-count-map-county', 'value'),
     Input('validation-scenario-map', 'value'),
     Input('dummy_div12', 'children'),
     Input('counts-map-scatterplot-map-container', 'clickData')]
    )
def update_visuals(county, selected_scen, aux, mapsel):

    def create_scatterplot(df, mapselection, county, xcol, ycol, xaxis_title, yaxis_title):

        if county != 'All':
            df = df[df['county'] == county]
            
        if mapselection is None:
            trace = [go.Scatter(
                x=df[xcol].astype('float').copy(),
                y=df[ycol].astype('float').copy(),
                mode='markers',
                line_color=config['validation_color_list'][0]
                )]
        else:
            selection = mapselection['points'][0]['customdata']
        
            sel_df = df.loc[df['@countid'] == selection]
        
            trace1 = go.Scatter(
                    x=df[xcol].astype('float').copy(),
                    y=df[ycol].astype('float').copy(),
                    mode='markers',
                    line_color=config['validation_color_list'][0]
                    )
                    
            trace_selection = go.Scatter(
                    x=sel_df[xcol].astype('float').copy(),
                    y=sel_df[ycol].astype('float').copy(),
                    mode='markers',
                    marker=dict(color='blue', size=10, opacity=.5),

                    )
            
            trace = [trace1, trace_selection]

        layout = go.Layout(
            xaxis={'title': xaxis_title},
            yaxis={'title': yaxis_title},
            hovermode='closest',
            autosize=True,
            margin={'t':20},
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': trace, 'layout': layout}

    def create_scattermap(df, county, index_key, xcol, ycol, observed, modeled):
    
        if county != 'All':
            df = df[df['county'] == county]
            
        locations = [go.Scattermapbox(
                    lon = df[xcol],
                    lat = df[ycol],
                    mode='markers',
                    marker=dict(color=config['validation_color_list'][0], size=10, opacity=.5),
                    unselected={'marker' : {'opacity':1}},
                    selected={'marker' : {'opacity':0.5, 'size':25}},
                    hoverinfo='text',
                    hovertext=df[observed],
                    customdata=df[index_key] # set to the index column name so that I can highlight back to scatter plot graph
        )]
        
        layout = go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Count Locations",font=dict(size=25)),
            mapbox=dict(
                accesstoken = mapbox_access_token,
                bearing=0,
                style='light',
                center=dict(
                    lat=47.60357,
                    lon=-122.32945
                ),
                pitch=10,
                zoom=8,
            ),
        )
        
        return {'data': locations, 'layout': layout}


    scatter_graph = {'data': [], 'layout': go.Layout()}
    scatter_map = {'data': [], 'layout': go.Layout()}
    
    if selected_scen is not None:

        
        
        # Scatter plot of counts
        scatter_df = pd.read_csv(os.path.join('data',selected_scen,'daily_volume.csv'))
        scatter_graph = create_scatterplot(scatter_df, mapsel, county, 'observed', 'modeled', 'Observed', 'Modeled')
        
        # Scatter map of count locations
        scatter_df_nodups = scatter_df.drop_duplicates()
        cnt_loc = pd.read_csv(os.path.join('data/data','count_locations_wgs84.csv'))
        cnt_loc = cnt_loc[['F_countid', 'POINT_X', 'POINT_Y']]
        scattermap_df = scatter_df_nodups.join(cnt_loc.set_index('F_countid'), on= '@countid')
        scatter_map = create_scattermap(scattermap_df, county, '@countid', 'POINT_X', 'POINT_Y', 'observed', 'modeled')

        
    return scatter_graph, scatter_map


# Updates graph when a point is selected in the map    
# @app.callback(
    # Output('counts-map-scatterplot-graph-container', 'figure'),
    # [Input('counts-map-scatterplot-map-container', 'clickData'),
     # Input('traffic-count-map-county', 'value'),
     # Input('validation-scenario-map', 'value'),
     # Input('dummy_div12', 'children')])
# def update_graph_click_data(clickData, county, selected_scen, aux):
    
    # def create_scatterplot(df, sel_df, county, xcol, ycol, xaxis_title, yaxis_title):

        # if county != 'All':
            # df = df[df['county'] == county]

        # trace = go.Scatter(
                # x=df[xcol].astype('float').copy(),
                # y=df[ycol].astype('float').copy(),
                # mode='markers',
                # )
                
        # trace_selection = go.Scatter(
                # x=sel_df[xcol].astype('float').copy(),
                # y=sel_df[ycol].astype('float').copy(),
                # mode='markers',
                # marker=dict(color='red', size=10, opacity=.5)
                # )

        # layout = go.Layout(
            # xaxis={'title': xaxis_title},
            # yaxis={'title': yaxis_title},
            # hovermode='closest',
            # autosize=True,
            # margin={'t':20},
            # font=dict(family='Segoe UI', color='#7f7f7f')
            # )
        # return {'data': [trace, trace_selection], 'layout': layout}
        
    # scatter_graph = {'data': [], 'layout': go.Layout()}
    
    # if selected_scen is not None:
        # # Scatter plot of counts
        # scatter_df = pd.read_csv(os.path.join('data',selected_scen,'daily_volume.csv'))
        # selected_clickData = scatter_df.loc['@countid' == clickData]
        # #scatter_df = pd.read_csv(r'C:\soundcast\soundcast_dash\data\2018_base\daily_volume.csv')
        # scatter_graph = create_scatterplot(scatter_df, selected_clickData, county, 'observed', 'modeled', 'Observed', 'Modeled')
    
    # return scatter_graph
    

    