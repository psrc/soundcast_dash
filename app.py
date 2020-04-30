import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import json
import plotly.graph_objs as go
import plotly.express as px
import functools

external_stylesheets = [dbc.themes.BOOTSTRAP]  # [dbc.themes.MATERIA]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True


def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)


available_scenarios = [name for name in os.listdir('data')
                       if os.path.isdir(os.path.join('data', name))
                       and name != 'data']
mode_dict = {1: 'walk', 2: 'bike', 3: 'sov', 4: 'hov2', 5: 'hov3',
             6: 'w_transit', 7: 'd_transit', 8: 'school_bus', 9: 'other',
             0: 'other'}
taz_gdf = gpd.read_file('data/data/taz2010nowater.shp')
taz_gdf['id'] = taz_gdf.index

# Layout ------------------------------------------------------------------
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
                        ),
                    ]
                ),  # end dbc.FormGroup
            ]
        )  # end dbc.CardBody

    ],
    className='aside-card'
)

# Trips Mode Choice Layout
tab_trips_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    id='person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    id='dpurp-dropdown'
                ),
                html.Br(),
                html.Div(id='dummy_div'),
            ],
            #className = 'bg-light',

        )  # end dbc.CardBody
    ],
    className='aside-card'
    )  # end dbc.Card
    ]

tab_trips_mc_layout = [dbc.Card(
    dbc.CardBody(
        [
            html.H2("Trip Mode Choice"),
            html.Br(),
            dbc.RadioItems(
                id='mode-share-type',
                options=[{'label': i, 'value': i} for i
                         in ['Mode Share', 'Trips by Mode']],
                value='Mode Share',
                inline=True
                ),
            dcc.Graph(id='mode-choice-graph'),
        ],
    ),  # end dbc.CardBody
    style={"margin-top": "20px"},
    ),  # end dbc.Card
    dbc.Card(
        dbc.CardBody(
            [
                html.H2('Trip Departure Hour:'),
                dcc.Graph(id='trip-deptm-graph'),
            ]
        ),
        style={"margin-top": "20px"},
    )
]

# Tours mode choice Layout
tab_tours_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [

                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    id='tour-person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    id='tour-dpurp-dropdown'
                ),
                html.Br(),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div2'),
            ],
            #className = 'bg-light',
        )],
    className='aside-card'
)]

tab_tours_mc_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Tour Mode Choice"),
                html.Br(),
                dbc.RadioItems(
                    id='tour-mode-share-type',
                    options=[{'label': i, 'value': i} for i
                             in ['Mode Share', 'Tours by Mode']],
                    value='Mode Share',
                    inline=True
                ),
                dcc.Graph(id='tour-mode-choice-graph'),
            ],
        ),
        style={"margin-top": "20px"},
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H2('Tour Departure Hour:'),
                dcc.Graph(id='tour-deptm-graph'),
            ]
        ),
        style={"margin-top": "20px"},
    ),
]

# Tab Day Pattern Layout
tab_day_pattern_filter = [
    dbc.Card(
        [
            dbc.CardHeader(html.H1('Dataset')),
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
                    html.Div(id='dummy-dataset-type'),
                ],
            ),  # end of CardBody
            dbc.CardHeader(html.H1('Day Pattern by Person Type'),
                           className='additional-header'),
            dbc.CardBody(
                [
                    dbc.Label('Destination Purpose:'),
                    dcc.Dropdown(
                        value='Escort',
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
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        # "Percent of X by Purpose"
                        html.H2(id='dpatt-perc-dpurp-gen-header'),

                        html.Br(),
                        html.Div(
                            id='dpatt-table-perc-tours-dpurp-gen-container'),

                    ]
                    ), style={"margin-top": "20px"}
                ),
            width=6
            ),  # end Col
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        # "X per Person by Purpose"
                        html.H2(id='dpatt-dpurp-gen-header'),

                        html.Br(),
                        html.Div(
                            id='dpatt-table-tours-dpurp-gen-container'),

                    ]
                    ), style={"margin-top": "20px"}
                ),
            width=6
            )  # end Col
         ]
        ),
    dbc.Row(children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='dpatt-tours-pptyp-purpose-header'),
                        #html.Div(children=[
                        #   html.Div(id='dpatt-table-tours-purpose-container'),
                        #   dcc.Graph(id='dpatt-graph-tours-purpose')],
                        #   className='inline-container'),
                        html.Div(id='dpatt-table-tours-purpose-container'),
                        #dcc.Graph(id='dpatt-graph-tours-purpose'),

                        ]
                ),
                style={"margin-top": "20px"}
            ),
            width=5
        ),  # end Col
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(id='dpatt-graph-tours-purpose'),

                    ]
                ), style={"margin-top": "20px"}
            ),
            width=7
        ),  # end Col
    ]
    ),  # end Row

    html.Div(id='dummy_div5'),
]

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
    #dbc.Row(children=[
    #    dbc.Col(
    #        dbc.Card(
    #            dbc.CardBody(
    #                [
    #                    html.H2("Workers"),
    #                    html.Br(),
    #                    html.Div(id='table-wrkr-container'),
    #                    ]
    #                ), style= {"margin-top": "20px"}
    #            ),
    #        width=5
    #        ), # end col
    #    ]),
    html.Div(id='dummy_div3')
    ]

# Taz Map Layout
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
                html.Div(id='dummy_div_map'),
            ],
            #className = 'bg-light',

        )
    ],
    className='aside-card'
)]

taz_map_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(id="my-graph"),
                html.Div(id='dummy_div_map'),
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

                html.Div(id='dummy_div_map'),
            ]
        ),
        style={"margin-top": "20px"},
    ),
]


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
        dbc.Tab(label="Tours", tab_id="tab-tours-mc"),
        dbc.Tab(label="Day Pattern", tab_id="tab-day-pattern"),
        dbc.Tab(label="HH & Persons", tab_id="tab-hh-pers"),
        dbc.Tab(label="TAZ Map", tab_id="taz-map")
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

hidden_divs = dbc.Container([
    html.Div(id='trips', style={'display': 'none'}),
    html.Div(id='tours', style={'display': 'none'}),
    html.Div(id='persons', style={'display': 'none'}),
    #html.Div(id='households', style={'display': 'none'}),
    html.Div(id='dtaz_trips', style={'display': 'none'}),
    #html.Div(id='auto_own', style={'display': 'none'}),
    #html.Div(id='workers', style={'display': 'none'},)
])

app.layout = html.Div([navbar, main_body, hidden_divs])

# App Callbacks --------------------------------------------------------------

# filters
@app.callback(Output('tabs-content-filter', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content_filter(tab):
    if tab == 'tab-trips-mc':
        return tab_trips_mc_filter
    elif tab == 'tab-tours-mc':
        return tab_tours_mc_filter
    elif tab == 'tab-day-pattern':
        return tab_day_pattern_filter
    elif tab == 'tab-hh-pers':
        return tab_hh_pers_filter
    elif tab == 'taz-map':
        return taz_map_filter
    else:
        return None


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content(tab):
    if tab == 'tab-trips-mc':
        return tab_trips_mc_layout
    elif tab == 'tab-tours-mc':
        return tab_tours_mc_layout
    elif tab == 'tab-day-pattern':
        return tab_day_pattern_layout
    elif tab == 'tab-hh-pers':
        return tab_hh_pers_layout
    elif tab == 'taz-map':
        return taz_map_layout


# Scenario Selection callback ------------------------------------------------
@app.callback(
        [Output('trips', 'children'),
         Output('tours', 'children'),
         Output('persons', 'children'),
         #Output('households', 'children'),
         #Output('dtaz_trips', 'children'),
         #Output('auto_own', 'children'),
         #Output('workers', 'children')
         ],
        [Input('scenario-1-dropdown', 'value'),
         Input('scenario-2-dropdown', 'value')])
def page_1_dropdown(val1, val2):
    trips1 = pd.read_csv(os.path.join('data', val1, 'trip_purpose_mode.csv'))
    trips2 = pd.read_csv(os.path.join('data', val2, 'trip_purpose_mode.csv'))
    tours1 = pd.read_csv(os.path.join('data', val1, 'tour_purpose_mode.csv'))
    tours2 = pd.read_csv(os.path.join('data', val2, 'tour_purpose_mode.csv'))
    pers1 = pd.read_csv(os.path.join('data', val1, 'person_type.csv'))
    pers2 = pd.read_csv(os.path.join('data', val2, 'person_type.csv'))
    #hhs1 = pd.read_csv(os.path.join('data', val1,
    #                                'household_size_vehs_workers.csv'))
    #hhs2 = pd.read_csv(os.path.join('data', val2,
    #                                'household_size_vehs_workers.csv'))
    #dtaz_trips1 = pd.read_csv(os.path.join('data', val1, 'trip_dtaz.csv'))
    #dtaz_trips2 = pd.read_csv(os.path.join('data', val2, 'trip_dtaz.csv'))
    #auto_own1 = pd.read_csv(os.path.join('data', val1, 'auto_ownership.csv'))
    #auto_own2 = pd.read_csv(os.path.join('data', val2, 'auto_ownership.csv'))
    #wrkrs1 = pd.read_csv(os.path.join('data', val1, 'work_flows.csv'))
    #wrkrs2 = pd.read_csv(os.path.join('data', val2, 'work_flows.csv'))
    trips = {
        val1: trips1.to_json(orient='split'),
        val2: trips2.to_json(orient='split')
        }
    tours = {
        val1: tours1.to_json(orient='split'),
        val2: tours2.to_json(orient='split')
        }
    persons = {
        val1: pers1.to_json(orient='split'),
        val2: pers2.to_json(orient='split')
        }
    #households = {
    #     val1: hhs1.to_json(orient='split'),
    #     val2: hhs2.to_json(orient='split')
    #    }
    #dtaz_trips = {
    #     val1: dtaz_trips1.to_json(orient='split'),
    #     val2: dtaz_trips2.to_json(orient='split')
    #    }
    #auto_own = {
    #     val1: auto_own1.to_json(orient='split'),
    #     val2: auto_own2.to_json(orient='split')
    #    }
    #workers = {
    #    val1: wrkrs1.to_json(orient='split'),
    #    val2: wrkrs2.to_json(orient='split')
    #    }
    return json.dumps(trips), json.dumps(tours), json.dumps(persons)  # ,
    #json.dumps(dtaz_trips) #, json.dumps(households), json.dumps(auto_own),
    #json.dumps(workers)


# Trips Mode Choice tab ------------------------------------------------------
@app.callback(
    [Output('person-type-dropdown', 'options'),
     Output('dpurp-dropdown', 'options')],
    [Input('trips', 'children'),
     Input('dummy_div', 'children')
     ])
def load_drop_downs(json_data, aux):
    print('trip filter callback')
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.dpurp.unique()])
    return [{'label': i, 'value': i} for i
            in person_types], [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('mode-choice-graph', 'figure'),
               Output('trip-deptm-graph', 'figure')],
              [Input('trips', 'children'),
               Input('person-type-dropdown', 'value'),
               Input('dpurp-dropdown', 'value'),
               Input('mode-share-type', 'value')])
def update_graph(json_data, person_type, dpurp, share_type):
    print('trip_update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        print(key)
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df = df[df['pptyp'] == person_type]
        if dpurp != 'All':
            df = df[df['dpurp'] == dpurp]
        if share_type == 'Mode Share':
            df_mode_share = df[['mode', 'trexpfac']].groupby('mode')\
                .sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        else:
            df_mode_share = df[['mode', 'trexpfac']].groupby('mode')\
                .sum()[['trexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph
        trace1 = go.Bar(
            x=df_mode_share['mode'].copy(),
            y=df_mode_share['trexpfac'].copy(),
            name=key
            )
        data1.append(trace1)

        # trip distance histogram
        df_deptm_share = df[['deptm_hr', 'trexpfac']].groupby('deptm_hr')\
            .sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        df_deptm_share.reset_index(inplace=True)

        trace2 = go.Bar(
            x=df_deptm_share['deptm_hr'],
            y=df_deptm_share['trexpfac'].astype(int),
            name=key)

        data2.append(trace2)

    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'mode'},
            yaxis={'title': share_type, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode='group',
            xaxis={'title': 'departure hour'},
            yaxis={'title': 'share', 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1},
    {'data': data2, 'layout': layout2}


# Tours Mode Choice tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('tour-person-type-dropdown', 'options'),
     Output('tour-dpurp-dropdown', 'options')],
    [Input('tours', 'children'),
     Input('dummy_div2', 'children')])
def tour_load_drop_downs(json_data, aux):
    print('tour filter callback')
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.pdpurp.unique()])
    return [{'label': i, 'value': i} for i in person_types],
    [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('tour-mode-choice-graph', 'figure'),
               Output('tour-deptm-graph', 'figure')],
              [Input('tours', 'children'),
               Input('tour-person-type-dropdown', 'value'),
               Input('tour-dpurp-dropdown', 'value'),
               Input('tour-mode-share-type', 'value')])
def tour_update_graph(json_data, person_type, dpurp, share_type):
    print('tour update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df = df[df['pptyp'] == person_type]
        if dpurp != 'All':
            df = df[df['pdpurp'] == dpurp]
        if share_type == 'Mode Share':
            df_mode_share = df[['tmodetp', 'toexpfac']].groupby('tmodetp')\
                .sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
        else:
            df_mode_share = df[['tmodetp', 'toexpfac']].groupby('tmodetp')\
                .sum()[['toexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph
        trace1 = go.Bar(
            x=df_mode_share['tmodetp'].copy(),
            y=df_mode_share['toexpfac'].copy(),
            name=key
            )
        data1.append(trace1)

        # trip distance histogram
        df_deptm_share = df[['tlvorg_hr', 'toexpfac']].groupby('tlvorg_hr')\
            .sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
        df_deptm_share.reset_index(inplace=True)

        trace2 = go.Bar(
            x=df_deptm_share['tlvorg_hr'],
            y=df_deptm_share['toexpfac'].astype(int),
            name=key
        )
        data2.append(trace2)

    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'mode'},
            yaxis={'title': share_type, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode='group',
            xaxis={'title': 'departure hour'},
            yaxis={'title': 'share', 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1},
    {'data': data2, 'layout': layout2}


# Day Pattern tab ------------------------------------------------------------
# load drop downs
@app.callback(
    Output('dpatt-dpurp-dropdown', 'options'),
    [Input('dpatt-dataset-type', 'value'),
     Input('tours', 'children'),
     Input('trips', 'children'),
     Input('dummy_div4', 'children')])
def dpurp_dropdown(dataset_type, tours_json, trips_json, aux):
    dpurp = []
    if dataset_type == 'Tours':
        dataset = json.loads(tours_json)
        dataset_dpurp_col = 'pdpurp'
    else:
        dataset = json.loads(trips_json)
        dataset_dpurp_col = 'dpurp'
    key = list(dataset)[0]
    df = pd.read_json(dataset[key], orient='split')
    dpurp.extend([x for x in df[dataset_dpurp_col].unique()])
    return [{'label': i, 'value': i} for i in dpurp]


# dynamic label based on dpurp selection
@app.callback(
    [Output('dpatt-tours-pptyp-purpose-header', 'children'),
     Output('dpatt-perc-dpurp-gen-header', 'children'),
     Output('dpatt-dpurp-gen-header', 'children')],
    [Input('dpatt-dataset-type', 'value'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')])
def update_tours_by_pptype_purpose_header(dataset_type, dpurp, aux, aux1):
    header_pptyp_dpurp = dpurp + ' ' + dataset_type + \
        ' per Person by Person Type'
    header_perc_dpurp_gen = 'Percent of' + ' ' + dataset_type + ' by Purpose'
    header_dpurp_gen = dataset_type + ' per Person by Purpose'
    return header_pptyp_dpurp, header_perc_dpurp_gen, header_dpurp_gen


# all content, render as DashTables + graph
@app.callback(
    [Output('dpatt-table-perc-tours-dpurp-gen-container', 'children'),
     Output('dpatt-table-tours-dpurp-gen-container', 'children'),
     Output('dpatt-table-tours-purpose-container', 'children'),
     Output('dpatt-graph-tours-purpose', 'figure')],
    [Input('dpatt-dataset-type', 'value'),
     Input('trips', 'children'),
     Input('tours', 'children'),
     Input('persons', 'children'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def update_visuals(dataset_type, trips_json, tours_json, pers_json, dpurp,
                   aux, aux1):
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
                        'font-family': 'Segoe UI',
                        'font-size': fontsize,
                        'text-align': 'center'}
                )
            ]
        )
        return t

    # load all data
    trips = json.loads(trips_json)
    tours = json.loads(tours_json)
    pers = json.loads(pers_json)

    if dataset_type == 'Tours':
        dataset = tours
        dataset_weight_col = 'toexpfac'
        dataset_dpurp_col = 'pdpurp'
    else:
        dataset = trips
        dataset_weight_col = 'trexpfac'
        dataset_dpurp_col = 'dpurp'

    datalist = []  # X per person by person type and purpose
    datalist_all_dpurp = []  # X per person by purpose
    datalist_dpurp_gen = []  # X by purpose

    keys = dataset.keys()
    keyslist = list(keys)

    for key in keys:
        df = pd.read_json(dataset[key], orient='split')

        df_dpurp_gen = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns={dataset_weight_col: key})
        datalist_dpurp_gen.append(df_dpurp_gen[[dataset_dpurp_col, key]])

        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        df = df.groupby(['pptyp', dataset_dpurp_col]).sum()[[dataset_weight_col]].reset_index().merge(df_pers, on='pptyp')

        df_dpurp = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col, 'psexpfac']].reset_index()
        datalist_all_dpurp.append(calc_dpatt_per_person(df_dpurp, [dataset_dpurp_col], dataset_weight_col, key))

        df_ptype = df[df[dataset_dpurp_col] == dpurp]
        datalist.append(calc_dpatt_per_person(df_ptype, ['pptyp', dataset_dpurp_col], dataset_weight_col, key))

    newdf_dpurp_gen = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=dataset_dpurp_col), datalist_dpurp_gen)
    newdf_dpurp = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=dataset_dpurp_col), datalist_all_dpurp)
    newdf = functools.reduce(lambda df1, df2: pd.merge(df1, df2, on=['pptyp', dataset_dpurp_col]), datalist)

    # create percent of tours by purpose
    tp_tbl = newdf_dpurp_gen.copy()
    for key in keyslist:
        tp_tbl[key] = (tp_tbl[key]/tp_tbl[key].sum()) * 100
    tp_tbl = calc_delta(tp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2, percent_delta=False)
    tp = create_dash_table('dpatt-table-perc-tours-dpurp-gen', tp_tbl, ['Destination Purpose'], '.7vw')

    # create dash tables for tours per person and purpose
    tppp_tbl = newdf_dpurp.copy()
    tppp_tbl = calc_delta(tppp_tbl, keyslist, dataset_dpurp_col, 'Destination Purpose', 2)
    tppp = create_dash_table('dpatt-table-tours-dpurp-gen', tppp_tbl, ['Destination Purpose'], '.7vw')

    # create dash table for tours per person by person type and purpose
    datatbl = newdf.copy()
    datatbl = datatbl.drop(dataset_dpurp_col, axis=1)
    datatbl = calc_delta(datatbl, keyslist, 'pptyp', 'Person Type', 2)
    t = create_dash_table('dpatt-table-tours-purposes', datatbl, ['Person Type'], '.6vw')

    # create graph

    graph_datalist = []
    for key in dataset.keys():
        trace = go.Bar(
            x=newdf['pptyp'].copy(),
            y=newdf[key].copy(),
            name=key
            )
        graph_datalist.append(trace)

    layout = go.Layout(
        barmode='group',
        xaxis={'type': 'category', 'automargin': True},
        yaxis={'title': dpurp + ' ' + dataset_type + ' per Person', 'zeroline': False},
        hovermode='closest',
        autosize=True,
        font=dict(family='Segoe UI', color='#7f7f7f')
        )

    return tp, tppp, t, {'data': graph_datalist, 'layout': layout}

# Households and Persons tab ------------------------------------------------------------------


@app.callback(
    [Output('table-totals-container', 'children'),
     Output('hhpers-graph-header', 'children'),
     Output('hhpers-graph-container', 'figure')
     ],
    [Input('hhpers-dataset-type', 'value'),
     Input('persons', 'children'),
     Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('dummy_div3', 'children')]
    )
def update_visuals(data_type, pers_json, scenario1, scenario2, aux):
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
        sum = map(lambda x: pd.read_json(pers_tbl[x], orient='split')[expfac].sum(), keys)
        d = dict(zip(keys, sum))
        alldict[dtype] = d

        # households
        hh_sum = map(lambda x: hh_tbl[x]['hhexpfac'].sum(), hh_tbl.keys())
        hh_d = dict(zip(hh_tbl.keys(), hh_sum))
        alldict['Total Households'] = hh_d

        # workers
        wrkrs_sum = map(lambda x: wrkrs_tbl[x][wrkrs_tbl[x]['pwtaz'] >= 0]['psexpfac'].sum(), wrkrs_tbl.keys())
        wrkrs_d = dict(zip(wrkrs_tbl.keys(), wrkrs_sum))
        alldict['Total Workers'] = wrkrs_d

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
                                      'font-family': 'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  )
             ]
            )
        return t

    def create_simple_bar_graph(table, xcol, weightcol, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            df = table[key]
            df = df[[xcol, weightcol]].groupby(xcol).sum()[[weightcol]]
            df = df.reset_index()

            trace = go.Bar(
                x=df[xcol].copy(),
                y=df[weightcol].copy(),
                name=key
                )
            datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type': 'category'},
            yaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
        return {'data': datalist, 'layout': layout}

    def create_workers_table(wrkrs_tbl):
        taz_geog = pd.read_sql_table('taz_geography', 'sqlite:///R:/e2projects_two/SoundCast/Inputs/dev/db/soundcast_inputs.db')

        datalist = []
        for key in wrkrs_tbl.keys():

            df = wrkrs_tbl[key]

            df = df.merge(taz_geog, left_on='hhtaz', right_on='taz')
            df.rename(columns={'geog_name': 'hh_county'}, inplace=True)

            df = df.merge(taz_geog, left_on='pwtaz', right_on='taz')
            df.rename(columns={'geog_name': 'work_county'}, inplace=True)

            df.drop(['taz_x', 'taz_y'], axis=1, inplace=True)
            df = df.groupby(['hh_county', 'work_county']).sum()[['psexpfac']]

            df.rename(columns={'psexpfac': key}, inplace=True)
            df = df.reset_index()

            datalist.append(df)

        df_scenarios = pd.merge(datalist[0], datalist[1], on=['hh_county', 'work_county'])
        df_scenarios.rename(columns={'hh_county': 'Household County', 'work_county': 'Work County'}, inplace=True)
        # format numbers with separator
        format_number_dp = functools.partial(format_number, decimal_places=0)
        for i in range(2, len(df_scenarios.columns)):
            df_scenarios.iloc[:, i] = df_scenarios.iloc[:, i].apply(format_number_dp)
        return df_scenarios
        #t = html.Div(
        #    [dash_table.DataTable(id='table-workers',
        #                          columns=[{"name": i, "id": i} for i in df_scenarios.columns],
        #                          data=df_scenarios.to_dict('rows'),
        #                          style_cell_conditional = [
        #                              {
        #                                  'if': {'column_id': i},
        #                                  'textAlign': 'left'
        #                                  } for i in ['Household County', 'Work County']
        #                              ],
        #                          style_cell = {
        #                              'font-family':'Segoe UI',
        #                              'font-size': 11,
        #                              'text-align': 'center'}
        #                          )
        #        ]
        #    )

        #return t

    vals = [scenario1, scenario2]
    pers_tbl = json.loads(pers_json)
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
        wdf = create_workers_table(wrkrs_tbl)
        wdf_melt = pd.melt(wdf, id_vars=['Household County', 'Work County'],
                           value_vars=vals,
                           var_name='Scenario', value_name='Workers')
        agraph = px.bar(
            wdf_melt,
            height=900,
            #width=950,
            barmode='group',
            facet_row='Household County',
            x='Work County',
            y='Workers',
            color='Scenario'
        )
        agraph.update_layout(font=dict(family='Segoe UI', color='#7f7f7f'))
        agraph.for_each_annotation(lambda a: a.update(text=a.text.replace("Household County=", "")))
        agraph.for_each_trace(lambda t: t.update(name=t.name.replace("Scenario=", "")))
        agraph_header = 'Workers by Household County by Work County'

    return totals_table, agraph_header, agraph


# Taz Map tab ------------------------------------------------------------------
# load drop downs
@app.callback(
    Output('dtaz_trips', 'children'),
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value')]
    )
def map_read_data(scenario1, scenario2):
    dtaz_trips1 = pd.read_csv(os.path.join('data', scenario1, 'trip_dtaz.csv'))
    dtaz_trips2 = pd.read_csv(os.path.join('data', scenario2, 'trip_dtaz.csv'))
    dtaz_trips = {
        scenario1: dtaz_trips1.to_json(orient='split'),
        scenario2: dtaz_trips2.to_json(orient='split')
    }
    return json.dumps(dtaz_trips)


@app.callback(
    Output('dpurp-dropdown2', 'options'),
    [Input('dtaz_trips', 'children'),
     Input('dummy_div_map', 'children')])  # change dummy div name
def map_load_drop_downs(json_data, aux):
    print('taz load drop downs called')
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    dpurp.extend([x for x in df.dpurp.unique()])
    print(dpurp)
    return [{'label': i, 'value': i} for i in dpurp]


@app.callback(
    Output('my-graph', 'figure'),
    [Input('dtaz_trips', 'children'),
     Input('dpurp-dropdown2', 'value'),
     Input('dummy_div_map', 'children')])  # change dummy div name
def map_update_graph(json_data, dpurp, aux):
    print('update map')
    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    df = pd.DataFrame(df.groupby(['dtaz', 'mode'])['trexpfac'].sum())
    df.reset_index(inplace True)
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
    trace = go.Choroplethmapbox(geojson=geojson_data, locations=gdf['id'], z=gdf['mode_share'], autocolorscale=False,
                                colorscale="YlGnBu", zauto=False, zmid=12, zmin=0, zmax=15, marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
                                colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                                'title': {"text": 'transit', "side": "bottom"}})
    #print (trace)

    return {"data": [trace],
            "layout": go.Layout(title='transit', mapbox_style="open-street-map", mapbox_zoom=7.5, mapbox_center={"lat": 47.609, "lon": -122.291}, height=800, geo={'showframe': False, 'showcoastlines': False, })}


@app.callback(
    Output('my-graph2', 'figure'),
    [Input('my-graph', 'selectedData'),
     Input('dtaz_trips', 'children'),
     Input('dummy_div_map', 'children')])  # change dummy div name
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
        #print (df)
    return {'data': data1, 'layout': layout1}


# Run app ------------------------------------------------------------------------

app.run_server(debug=False)
#if __name__ == '__main__': app.run_server(debug=False,port=8050,host='0.0.0.0')
