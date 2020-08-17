import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from tabs import trips_mc, length_dist_mc, tours_mc, tours_2, day_patt, work
from app import app, config
from collections import OrderedDict
import dash_html_components as html
import dash_core_components as dcc
#import dash_table
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import json
#import plotly.graph_objs as go
import plotly.express as px
#import functools
#import yaml

#def format_number(x, decimal_places):
#    formula = "{:,." + str(decimal_places) + "f}"
#    return formula.format(x)

def format_percent(x, decimal_places):
    # formula = "{:. " + str(decimal_places) + "f%}"
    formula = '{:.'+str(decimal_places)+'%}'
    return formula.format(x)    


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

#available_scenarios.insert(0,"None")
mode_dict = {1: 'walk', 2: 'bike', 3: 'sov', 4: 'hov2', 5: 'hov3',
             6: 'w_transit', 7: 'd_transit', 8: 'school_bus', 9: 'other',
             0: 'other'}
taz_gdf = gpd.read_file('data/data/taz2010nowater.shp')
taz_geog = pd.read_csv(r'data/data/taz_geography.csv')
taz_gdf['id'] = taz_gdf.index

# Scenario Selection Layout
scenario_select_layout = dbc.Card(
    [
        dbc.CardHeader(html.H1("Select Scenarios")),
        dbc.CardBody(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Scenario 1"),
                        dcc.Dropdown(
                            id="scenario-1-dropdown",
                            options=[
                                {"label": col, "value": col} for col
                                in available_scenarios
                            ],
                            value=available_scenarios[0],
                            clearable=False
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("Scenario 2"),
                        dcc.Dropdown(
                            id="scenario-2-dropdown",
                            options=[
                                {"label": col, "value": col} for col
                                in available_scenarios
                            ],
                            value=available_scenarios[1],
                            clearable=True
                        ),
                    ]
                ),  # end dbc.FormGroup
                dbc.FormGroup(
                    [
                        dbc.Label("Scenario 3"),
                        dcc.Dropdown(
                            id="scenario-3-dropdown",
                            options=[
                                {"label": col, "value": col} for col
                                in available_scenarios
                            ],
                            value=available_scenarios[2],
                            clearable=True
                        ),
                    ]
                ),  # end dbc.FormGroup
            ]
        )  # end dbc.CardBody

    ],
    className='aside-card'
)
# Main Layout
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Page 1", header=True),
                dbc.DropdownMenuItem("Page 2", href="#")
            ],
            nav=True,
            in_navbar=True,
            label="Other",
        ),
    ],
    fluid=True,
    brand="Soundcast Validation Dashboard",
    brand_href="#"
)

scenario_aside = scenario_select_layout
filter_aside = html.Div(id='tabs-content-filter')
content = html.Div(id='tabs-content')

tabs = dbc.Tabs(
    children=[
        dbc.Tab(label="Trips", tab_id="tab-trips-mc"),
        dbc.Tab(label="Trip Length and Distance", tab_id="tab-length-distance-mc"),
        dbc.Tab(label="Tours", tab_id="tab-tours-mc"),
        dbc.Tab(label="Tours 2", tab_id="tab-tours2-mc"),
        dbc.Tab(label="Day Pattern", tab_id="tab-day-pattern"),
        dbc.Tab(label="Work", tab_id="tab-work"),
        dbc.Tab(label="HH & Persons", tab_id="tab-hh-pers"),
        dbc.Tab(label="TAZ Map", tab_id="taz-map"),
        dbc.Tab(label="Traffic Counts", tab_id="traffic-counts"),
        dbc.Tab(label="Transit Boardings", tab_id="transit-boardings"),
        dbc.Tab(label="Transit Boardings Scenario", tab_id="transit-boardings-scenario")
    ],
    id="tabs-list"
)

main_body = html.Div(
    dbc.Container(
        dbc.Row(
            children=[
                dbc.Col(
                    [
                     dbc.Row(
                        dbc.Col(scenario_aside),
                        ),
                     dbc.Row(
                         dbc.Col(filter_aside)
                         )
                    ],
                    width=3
                ),  # sidebar
                dbc.Col([tabs, content], width=9)  # body of visuals
            ]  # end row
            ),
        fluid=True
    ),
    className="main-body-container"
)

app.layout = html.Div([navbar, main_body])

# App Callbacks --------------------------------------------------------------
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content(tab):
    if tab == 'tab-trips-mc':
        return trips_mc.tab_trips_mc_layout
    elif tab == 'tab-length-distance-mc':
        return length_dist_mc.tab_length_distance_mc_layout
    elif tab == 'tab-tours-mc':
        return tours_mc.tab_tours_mc_layout
    elif tab == 'tab-tours2-mc':
        return tours_2.tab_tours2_mc_layout
    elif tab == 'tab-day-pattern':
        return day_patt.tab_day_pattern_layout
    elif tab == 'tab-work':
        return work.tab_work_layout
    #elif tab == 'tab-hh-pers':
    #    return tab_hh_pers_layout
    #elif tab == 'taz-map':
    #    return taz_map_layout
    #elif tab == 'traffic-counts':
    #    return tab_traffic_counts_layout
    #elif tab == 'transit-boardings':
    #    return tab_transit_boardings_layout
    #elif tab == 'transit-boardings-scenario':
    #    return tab_transit_boardings_scenario_layout

# filters
@app.callback(Output('tabs-content-filter', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content_filter(tab):
    if tab == 'tab-trips-mc':
        return trips_mc.tab_trips_mc_filter
    elif tab == 'tab-length-distance-mc':
        return length_dist_mc.tab_length_distance_mc_filter
    elif tab == 'tab-tours-mc':
        return tours_mc.tab_tours_mc_filter
    elif tab == 'tab-tours2-mc':
        return tours_2.tab_tours2_mc_filter
    elif tab == 'tab-day-pattern':
        return day_patt.tab_day_pattern_filter
    elif tab == 'tab-work':
       return work.tab_work_filter
    #elif tab == 'tab-hh-pers':
    #    return tab_hh_pers_filter
    #elif tab == 'taz-map':
    #    return taz_map_filter
    #elif tab == 'traffic-counts':
    #    return tab_traffic_counts_filter
    #elif tab == 'transit-boardings':
    #    return tab_transit_boardings_filter
    #elif tab == 'transit-boardings-scenario':
    #    return tab_transit_boardings_scenario_filter
    else:
        return None

if __name__ == '__main__': app.run_server(debug=True)