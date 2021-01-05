import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import json
import geopandas as gpd
import numpy as np
from app import app, config
import dash_table
from collections import OrderedDict
import plotly.express as px

def datatable_format_number(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': ',.' + str(decimal_places) + 'f'}}
    

def datatable_format_percent(col, decimal_places):
    return {"name": col, "id": col, 'type':'numeric','format': {'specifier': '.' + str(decimal_places) + '%'}}

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

tab_transit_lines_layout = [
    html.H6("Transit Line Riders' Origin Zones, 7-8 AM"),

    dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(id="transit-od-map"),
                html.Div(id='dummy_div_map'),
            ],

        ),
        #className='card-deck py-4',
        style={"margin-top": "20px"},
),
]

tab_transit_lines_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.Card(
        dbc.CardBody(
            [
                dbc.Label('Validation Scenario:'),
                dcc.Dropdown(
                    value=model_scenarios[0],
                    clearable=False,
                    id='validation-scenario-transit-2'
                ),
                html.Br(),
            ],
            ), style={"margin-top": "20px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('Line ID:'),
                    dcc.Dropdown(
                        value='119150',
                        clearable=False,
                        id='line-selection'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            ),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Label('Transit Mode:'),
                    dcc.Dropdown(
                        value='litrat',
                        clearable=False,
                        id='transit-mode'
                    ),
                    html.Br(),
                ],
                ), 
            style={"margin-top": "20px"}
            #className = 'bg-light',
            ),
            html.Div(id='dummy_div11'),
        ],
        className='aside-card',
        

    )]

####################################
# Transit validation tab
@app.callback(
    [Output('validation-scenario-transit-2', 'options'),
    Output('line-selection','options'),
    Output('transit-mode', 'options')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value')])
def transit_load_drop_downs(scen1, scen2, scen3):
    scen_list = []
    line_od_files = []
    for scen in [scen1, scen2, scen3]:
        # Validation data only available for scenario runs, check if it exists before adding to available scen list
        fname_path = os.path.join('data', scen, 'daily_volume_county_facility.csv')
        if os.path.isfile(fname_path):
            scen_list.append(scen)

            # get minimum list of available transit OD lines and modes
            line_od_files += os.listdir(os.path.join('data',scen,'line_od'))

    
    line_list = np.unique([i.split('_')[0] for i in line_od_files])
    mode_list = config['transit_mode_list']

    return [[{'label': i, 'value': i} for i in scen_list], [{'label': config['transit_line_dict'][i], 'value': i} for i in line_list], [{'label': i, 'value': i} for i in mode_list]]

@app.callback(
    Output('transit-od-map', 'figure'),
    [Input('validation-scenario-transit-2','value'),
    Input('line-selection','value'),
    Input('transit-mode','value'),
     Input('dummy_div_map','children')])
    # [Input('dtaz_trips', 'children'),
    #  Input('dpurp-dropdown2', 'value'),
    #  Input('dummy_div_map', 'children')])  # change dummy div name
def map_update_graph(selected_scen, selected_line, mode, aux):

    # datasets = json.loads(json_data)
    # key = list(datasets)[0]
    # df = pd.read_json(datasets[key], orient='split')
    # df = pd.DataFrame(df.groupby(['dtaz', 'mode'])['trexpfac'].sum())
    df = pd.read_csv(os.path.join('data',selected_scen, 'line_od/'+selected_line+'_'+mode+'.csv'), 
        skiprows=5, header=None, names=['o','d','trips'], delim_whitespace=True)
#         
    # df.reset_index(inplace=True)
    # df = df.pivot(index='dtaz', columns='mode', values='trexpfac')
    # df.fillna(0, inplace=True)
    # df['sum_trips'] = df.sum(axis=1)
    # df.reset_index(inplace=True)
    # gdf = taz_gdf.copy()
    gdf = gpd.read_file(r'data/data/taz2010nowater.shp')

    gdf = gdf.merge(df, left_on='TAZ', right_on='o')
    gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)

    geojson_data = json.loads(gdf.to_json())

    # gdf['mode_share'] = (gdf['Transit']/gdf['sum_trips']) * 100
    trace = go.Choroplethmapbox(geojson=geojson_data, locations=gdf['TAZ'], z=gdf['trips'], autocolorscale=False,
                                colorscale="YlGnBu", zauto=True, marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
                                colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                                'title': {"text": 'transit', "side": "bottom"}})


    return {"data": [trace],
            "layout": go.Layout(title='transit', 
                mapbox_style="white-bg", 
                mapbox_zoom=9, mapbox_center={"lat": 47.609, "lon": -122.291}, 
                height=800, geo={'showframe': False, 'showcoastlines': False, })}

    # return agency_table

