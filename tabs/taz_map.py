import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import geopandas as gpd
import numpy as np
from app import app
import json

taz_gdf = gpd.read_file('data/data/taz2010nowater.shp')
taz_gdf['id'] = taz_gdf.index
print('here')

#taz_shp = r'C:\Stefan\test\Dash-Choropleth-Example-master\Dash-Choropleth-Example-master\data\lep\taz_mode_choice.shp'
#dff = gpd.read_file(taz_shp)
#dff['transit_mode_share'] = dff['w_transit'] * 100
#dff['sov_mode_share'] = dff['sov'] * 100
#dff['id'] = dff.index
#dff['geometry'] = dff['geometry'].to_crs(epsg=4326)
##dff = dff.head(5)
#geojson_data = json.loads(dff.to_json())


taz_map_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    id='dpurp-dropdown2'
                ),
                html.Br(),
                html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div4'),
            ],
            className='bg-light',

        )
    ],
    className='aside-card'
)]

taz_map_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(id="my-graph"),
                html.Div(id='dummy_div4'),
                #html.Br(),
                #dbc.CardFooter('Trip Departure Hour:'),
                #dcc.Graph(id='trip-deptm-graph'),
            ],

        ),
        #className='card-deck py-4',
        style={"margin-top": "20px"},

    ),

    dbc.Card(
        dbc.CardBody(
            [
                #dbc.CardFooter("Trip Mode Choice"),
                #dcc.Graph(id='mode-choice-graph'),
                #html.Br(),
                html.H2('Trip Departure Hour:'),
                dcc.Graph(id='my-graph2'),

                html.Div(id='dummy_div4'),
            ]
        ),
        style={"margin-top": "20px"},
    )
]


# load drop downs
@app.callback(Output('dpurp-dropdown2', 'options'),
              [Input('dtaz_trips', 'children'),
               Input('dummy_div4', 'children')])
def load_drop_downs(json_data, aux):
    print('taz load drop downs called')
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    dpurp.extend([x for x in df.dpurp.unique()])
    print(dpurp)
    return [{'label': i, 'value': i} for i in dpurp]


#@app.callback(Output('my-graph', 'figure'),
#               [Input('dtaz_trips', 'children'),
#                Input('dpurp-dropdown2', 'value')])

#def update_graph(json_data, dpurp):
#    #print (dff[selected])
#    #dff = gdf.groupby(['iso_alpha', 'country']).mean().reset_index()
#    print ('map!')
#    print (dff.columns)
#    #def title(text):
#    #    if text == "pop":
#    #        return "Poplulation (million)"
#    #    elif text == "gdpPercap":
#    #        return "GDP Per Capita (USD)"
#    #    else:
#    #        return "Life Expectancy (Years)"
#    print (dff['transit_mode_share'])
#    trace = go.Choroplethmapbox(geojson = geojson_data, locations=dff['id'],z=dff['transit_mode_share'],autocolorscale=False,
#                          colorscale="YlGnBu", zauto = False, zmid=2, zmin=0, zmax=15, marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
#                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
#                                    'title': {"text": "transit", "side": "bottom"}})

#    print (type(trace))


#    return {"data": [trace],
#            "layout": go.Layout(title='transit', mapbox_style="open-street-map", mapbox_zoom=7, mapbox_center = {"lat": 47.609, "lon": -122.291}, height=800, geo={'showframe': False,'showcoastlines': False,})}


@app.callback(Output('my-graph', 'figure'),
              [Input('dtaz_trips', 'children'),
               Input('dpurp-dropdown2', 'value'),
               Input('dummy_div4', 'children')])
def update_graph(json_data, dpurp, aux):
    print('update map')
    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    df = pd.DataFrame(df.groupby(['dtaz', 'mode'])['trexpfac'].sum())
    df.reset_index(inplace=True)
    df = df.pivot(index='dtaz', columns='mode', values='trexpfac')
    df.fillna(0, inplace=True)
    df['sum_trips'] = df.sum(axis=1)
    df.reset_index(inplace=True)
    gdf = taz_gdf.copy()
    print(gdf.columns)
    #gdf = gdf.head(5)
    #print (gdf)
    gdf = gdf.merge(df, left_on='TAZ', right_on='dtaz')
    gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)
    geojson_data = json.loads(gdf.to_json())
    #print (gdf.columns)
    print(gdf['Transit'])
    gdf['mode_share'] = (gdf['Transit']/gdf['sum_trips']) * 100
    trace = go.Choroplethmapbox(
        geojson=geojson_data, locations=gdf['id'], z=gdf['mode_share'], autocolorscale=False,
        colorscale="YlGnBu", zauto=False, zmid=12, zmin=0, zmax=15, marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
        colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                  'title': {"text": 'transit', "side": "bottom"}}
    )
    #print(trace)

    return {"data": [trace],
            "layout": go.Layout(title='transit', mapbox_style="open-street-map", mapbox_zoom=7.5, mapbox_center={"lat": 47.609, "lon": -122.291}, height=800, geo={'showframe': False, 'showcoastlines': False, })}


@app.callback(
    Output('my-graph2', 'figure'),
    [Input('my-graph', 'selectedData'),
     Input('dtaz_trips', 'children'),
     Input('dummy_div4', 'children')])
def display_selected_data(selectedData, json_data, aux):

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    data1 = []
    if selectedData is None:
        print('selected data is None')
        df_mode_share = df[['mode', 'trexpfac']].groupby('mode').sum()[['trexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph

        trace1 = go.Bar(
            x=df_mode_share['mode'].copy(),
            y=df_mode_share['trexpfac'].copy(),
            name='test'
            )
        data1.append(trace1)

        layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'mode'},
            yaxis={'title': 'test'},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    else:
        print('map graph')
        x = selectedData['points']
        ids = [y['pointNumber'] for y in x]
        gdf = taz_gdf.copy()
        gdf = gdf.merge(df, left_on='TAZ', right_on='dtaz')
        gdf = gdf[gdf['id'].isin(ids)]
        gdf = gdf[['mode', 'trexpfac']].groupby('mode').sum()[['trexpfac']]
        gdf.reset_index(inplace=True)
        print(len(gdf))
        print(gdf.columns)
        trace1 = go.Bar(
            x=gdf['mode'].copy(),
            y=gdf['trexpfac'].copy(),
            name='test'
            )
        data1.append(trace1)

        layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'mode'},
            yaxis={'title': 'test'},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
        #print(df)
    return {'data': data1, 'layout': layout1}
