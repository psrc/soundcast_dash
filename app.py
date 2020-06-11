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

DEPLOY = False

if DEPLOY:
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/soundcast_dash/')
    app.config.suppress_callback_exceptions = True
    server = app.server
else:
    #external_stylesheets = [dbc.themes.BOOTSTRAP]  # [dbc.themes.MATERIA]
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.config.suppress_callback_exceptions = True




def format_number(x, decimal_places):
    formula = "{:,." + str(decimal_places) + "f}"
    return formula.format(x)


available_scenarios = [name for name in os.listdir('data')
                       if os.path.isdir(os.path.join('data', name))
                       and name != 'data']
#available_scenarios.insert(0,"None")
mode_dict = {1: 'walk', 2: 'bike', 3: 'sov', 4: 'hov2', 5: 'hov3',
             6: 'w_transit', 7: 'd_transit', 8: 'school_bus', 9: 'other',
             0: 'other'}
taz_gdf = gpd.read_file('data/data/taz2010nowater.shp')
taz_geog = pd.read_csv(r'data/data/taz_geography.csv')
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

# Trips Mode Choice Layout
tab_trips_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='dpurp-dropdown'
                ),
                html.Br(),
                dbc.Label('Origin District:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='origin-district'
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
                html.Br(),
                dbc.RadioItems(
                    id='mode-share-type-deptm',
                    options=[{'label': i, 'value': i} for i
                             in ['Distribution', 'Total Trips']],
                    value='Distribution',
                    inline=True
                    ),
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
                    clearable=False,
                    id='tour-person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
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
                             in ['Mode Share', 'Total Tours']],
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
                html.Br(),
                dbc.RadioItems(
                    id='tour-mode-share-type-deptm',
                    options=[{'label': i, 'value': i} for i
                             in ['Distribution', 'Total Tours']],
                    value='Distribution',
                    inline=True
                ),
                dcc.Graph(id='tour-deptm-graph'),
            ]
        ),
        style={"margin-top": "20px"},
    ),
]

# Tours 2  Layout
tab_tours2_mc_filter = [dbc.Card(
    [       dbc.CardHeader(html.H1('Filters')),
            dbc.CardBody(
                [
                    dbc.Label('Format Type:'),
                    dbc.RadioItems(
                        id='tour2-format-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Percent', 'Total']],
                        value='Percent'
                    ),
                    html.Br(),
                    html.Div(id='dummy-dataset-type'),
                    html.Div(id='dummy-format-type'),
                ],
                ),  # end of CardBody
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [

                html.Br(),
                dbc.Label('Mode:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='tour2-mode-dropdown'
                ),
                html.Br(),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div8'),
                html.Br(),
                dbc.Label('Purpose:'),
                dcc.Dropdown(
                    value='Work',
                    clearable=False,
                    id='tour2-purpose-dropdown'
                ),
                html.Br(),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div8'),
            ],
            #className = 'bg-light',
        )],
    className='aside-card'
)]

tab_tours2_mc_layout = [



    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='trips-tour-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        dcc.Graph(id='trips-by-tour'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 
        dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='stops-by-tour-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        html.Br(),
                        dbc.RadioItems(
                            id='stops-by-tour-type',
                            options=[{'label': i, 'value': i} for i
                                     in ['Entire Tour','First Half', 'Second Half']],
                            value='Entire Tour',
                            inline=True
                        ),
                        dcc.Graph(id='stops-by-tour'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 

]

# Length and distance Layout
tab_length_distance_mc_filter = [dbc.Card(
    [
        dbc.CardHeader(html.H1('Filters')),
            dbc.CardBody(
                [
                    dbc.Label('Format Type:'),
                    dbc.RadioItems(
                        id='distance-format-type',
                        options=[{'label': i, 'value': i} for i
                                 in ['Percent', 'Total']],
                        value='Percent'
                    ),
                    html.Br(),
                    html.Div(id='dummy-dataset-type'),
                    html.Div(id='dummy-format-type'),
                ],
                ),  # end of CardBody
        dbc.CardHeader(html.H1('Filters')),
        dbc.CardBody(
            [
                html.Br(),
                dbc.Label('Mode:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-mode-dropdown'
                ),
                html.Br(),
                dbc.Label('Person Type:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-person-type-dropdown'
                ),
                html.Br(),
                dbc.Label('Destination Purpose:'),
                dcc.Dropdown(
                    value='All',
                    clearable=False,
                    id='distance-dpurp-dropdown'
                ),
                #html.Div(id='df', style={'display': 'none'}),
                html.Div(id='dummy_div6'),
            ],
            #className = 'bg-light',
        )],
    className='aside-card'
)]

tab_length_distance_mc_layout = [
    

    dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='distance-graph1-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        dcc.Graph(id='tour-duration-graph'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 
        dbc.Row(children=[
         dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(id='distance-graph2-header'), # make header dynamic to dataset type ""
                        # html.Div(id='distance-tot-container'),
                        dcc.Graph(id='trip-time-graph'),
                        ]
                    ), style={"margin-top": "20px"}
                ),
            width=12
            ),  # end Col
        ]
        ), 

]

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


# Tab Work Layout
tab_work_layout = [
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
                    clearable=False,
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
        dbc.Tab(label="Trip Length and Distance", tab_id="tab-length-distance-mc"),
        dbc.Tab(label="Tours", tab_id="tab-tours-mc"),
        dbc.Tab(label="Tours 2", tab_id="tab-tours2-mc"),
        dbc.Tab(label="Day Pattern", tab_id="tab-day-pattern"),
        dbc.Tab(label="Work", tab_id="tab-work"),
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
    html.Div(id='tours_duration', style={'display': 'none'}),
    #html.Div(id='taz_geog', style={'display': 'none'}),
    #html.Div(id='dtaz_trips', style={'display': 'none'}),
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
    elif tab == 'tab-length-distance-mc':
        return tab_length_distance_mc_filter
    elif tab == 'tab-tours-mc':
        return tab_tours_mc_filter
    elif tab == 'tab-tours2-mc':
        return tab_tours2_mc_filter
    elif tab == 'tab-day-pattern':
        return tab_day_pattern_filter
    #elif tab == 'tab-work':
    #    return tab_work_filter
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
    elif tab == 'tab-length-distance-mc':
        return tab_length_distance_mc_layout
    elif tab == 'tab-tours-mc':
        return tab_tours_mc_layout
    elif tab == 'tab-tours2-mc':
        return tab_tours2_mc_layout
    elif tab == 'tab-day-pattern':
        return tab_day_pattern_layout
    elif tab == 'tab-work':
        return tab_work_layout
    elif tab == 'tab-hh-pers':
        return tab_hh_pers_layout
    elif tab == 'taz-map':
        return taz_map_layout


# Scenario Selection callback ------------------------------------------------
@app.callback(
        [Output('trips', 'children'),
         Output('tours', 'children'),
         Output('persons', 'children'),
         ],
        [Input('scenario-1-dropdown', 'value'),
         Input('scenario-2-dropdown', 'value'),
         Input('scenario-3-dropdown', 'value')])
def page_1_dropdown(val1, val2, val3):

    scenario_list = [val1, val2, val3]
    
    trips_dict = {}
    tours_dict = {}
    persons_dict = {}

    for x in range(0, len(scenario_list)):
         if scenario_list[x] is not None:
             print (scenario_list)
             print (scenario_list[x])
             trips = pd.read_csv(os.path.join('data', scenario_list[x], 'trip_purpose_mode.csv'))
             trips_dict[scenario_list[x]] = trips.to_json(orient='split')
             print ('here')

             tours = pd.read_csv(os.path.join('data', scenario_list[x], 'tour_purpose_mode.csv'))
             tours_dict[scenario_list[x]] = tours.to_json(orient='split')
             print ('here2')

             pers = pd.read_csv(os.path.join('data', scenario_list[x], 'person_type.csv'))
             persons_dict[scenario_list[x]] = pers.to_json(orient='split')
             print ('here3')

    return json.dumps(trips_dict), json.dumps(tours_dict), json.dumps(persons_dict) # ,

# Trips Mode Choice tab ------------------------------------------------------
@app.callback(
    [Output('person-type-dropdown', 'options'),
     Output('dpurp-dropdown', 'options'),
     Output('origin-district', 'options')],
    [Input('trips', 'children'),
     Input('dummy_div', 'children')
     ])
def load_drop_downs(json_data, aux):
    #print('trip filter callback')
    person_types = ['All']
    dpurp = ['All']
    o_district = ['All']
    datasets = json.loads(json_data)

    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.dpurp.unique()])
    o_district.extend([x for x in taz_geog.district.unique()])

    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp], [{'label': i, 'value': i} for i in o_district]

@app.callback([Output('mode-choice-graph', 'figure'),
               Output('trip-deptm-graph', 'figure')],
              [Input('trips', 'children'),
               Input('person-type-dropdown', 'value'),
               Input('dpurp-dropdown', 'value'),
               Input('origin-district', 'value'),
               Input('mode-share-type', 'value'),
               Input('mode-share-type-deptm', 'value')])
def update_graph(json_data, person_type, dpurp, o_district, 
                 share_type, share_type_deptm):
    #print('trip_update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []

    for key in datasets.keys():
        #print(key)
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df = df[df['pptyp'] == person_type]
        if dpurp != 'All':
            df = df[df['dpurp'] == dpurp]
        if o_district != 'All':
            df = df[df['trip_o_district'] == o_district]
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
        if share_type_deptm == 'Distribution':
            df_deptm_share = df[['deptm_hr', 'trexpfac']].groupby('deptm_hr')\
                .sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        else:
            df_deptm_share = df[['deptm_hr', 'trexpfac']].groupby('deptm_hr')\
                .sum()[['trexpfac']]
        df_deptm_share.reset_index(inplace=True)

        trace2 = go.Scatter(
            x=df_deptm_share['deptm_hr'],
            y=df_deptm_share['trexpfac'].astype(int),
            name=key)

        data2.append(trace2)

    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'Mode'},
            yaxis={'title': share_type, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode='group',
            xaxis={'title': 'Departure Hour'},
            yaxis={'title': share_type_deptm, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}


# Tours Mode Choice tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('tour-person-type-dropdown', 'options'),
     Output('tour-dpurp-dropdown', 'options')],
    [Input('tours', 'children'),
     Input('dummy_div2', 'children')])
def tour_load_drop_downs(json_data, aux):
    #print('tour filter callback')
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.pdpurp.unique()])
    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('tour-mode-choice-graph', 'figure'),
               Output('tour-deptm-graph', 'figure')],
              [Input('tours', 'children'),
               Input('tour-person-type-dropdown', 'value'),
               Input('tour-dpurp-dropdown', 'value'),
               Input('tour-mode-share-type', 'value'),
               Input('tour-mode-share-type-deptm', 'value')])
def tour_update_graph(json_data, person_type, dpurp, share_type, share_type_deptm):
   #print('tour update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df = df[df['pptyp'] == person_type]
        if dpurp != 'All':
            df = df[df['pdpurp'] == dpurp]
        if share_type in ['Distribution','Mode Share']:
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
        if share_type_deptm == 'Distribution':
            df_deptm_share = df[['tlvorg_hr', 'toexpfac']].groupby('tlvorg_hr')\
                .sum()[['toexpfac']]/df[['toexpfac']].sum() * 100
        else:
            df_deptm_share = df[['tlvorg_hr', 'toexpfac']].groupby('tlvorg_hr')\
                .sum()[['toexpfac']]
        df_deptm_share.reset_index(inplace=True)

        trace2 = go.Scatter(
            x=df_deptm_share['tlvorg_hr'],
            y=df_deptm_share['toexpfac'].astype(int),
            name=key
        )
        data2.append(trace2)
        
    layout1 = go.Layout(
            barmode='group',
            xaxis={'title': 'Mode'},
            yaxis={'title': share_type, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode='group',
            xaxis={'title': 'Departure Hour'},
            yaxis={'title': share_type_deptm, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}


# Tour 2; trips by tour
# Tours Mode Choice tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('tour2-purpose-dropdown', 'options'),
     Output('tour2-mode-dropdown', 'options')],
    [Input('trips', 'children'),
     Input('dummy_div8', 'children')])
def tour2_load_drop_downs(json_data, aux):
    #print('length and distance filter callback')
    mode = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    dpurp = [x for x in df.dpurp.unique()]
    mode.extend([x for x in df['mode'].unique()])

    return [{'label': i, 'value': i} for i in dpurp], [{'label': i, 'value': i} for i in mode]

@app.callback(
    [Output('trips-tour-header', 'children'),
     Output('stops-by-tour-header', 'children')],
    [Input('tour2-mode-dropdown', 'value'),
     Input('tour2-purpose-dropdown', 'value'),
     Input('stops-by-tour-type', 'value')
     ])
def update_headers(mode, dpurp, stop_type):

    result = []
    header_graph1 = 'Trips by Tours: ' + dpurp + ' Tours '    
    if mode != 'All':
        header_graph1 += ' by ' + mode

    result.append(header_graph1)

    header_graph2 = 'Stops on Tour: ' + dpurp + ' Tours ' 
    if mode != 'All':
        header_graph2 += 'by ' + mode 
    header_graph2 += ' | ' + stop_type
    result.append(header_graph2)
    return result

@app.callback([Output('trips-by-tour', 'figure'),
              Output('stops-by-tour', 'figure')],
              [ Input('scenario-1-dropdown', 'value'),
                Input('scenario-2-dropdown', 'value'),
                Input('scenario-3-dropdown', 'value'),
                Input('tour2-format-type', 'value'),
                Input('tour2-mode-dropdown', 'value'),
                Input('tour2-purpose-dropdown', 'value'),
                Input('stops-by-tour-type', 'value')])
def update_visuals(scenario1, scenario2, scenario3, format_type, mode, dpurp, stop_type):
    #print('tours 2 callback')
    
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_bar_chart_horiz(table, xcol, weightcol, format_type, mode, dpurp, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            if key != 'None':
                df = table[key]

                # Apply mode, and purpose filters
                for filter_name, filter_value in {'pdpurp': dpurp, 'tmodetp': mode}.items():
                    if filter_value != 'All':
                        df = df[df[filter_name] == filter_value]
                df = df[xcol+[weightcol]].groupby(xcol).sum()[[weightcol]]

                df = df.reset_index()
                df[weightcol] = df[weightcol].astype('int')

                # Calculate shares if selected
                if format_type == 'Percent':
                    df[weightcol] = df[weightcol]/df[weightcol].sum()

                trace = go.Bar(
                    y=df['dpurp'].copy(),
                    x=df[weightcol].copy(),
                    name=key,
                    orientation='h',
                    )
                datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            yaxis={'type': 'category', 'automargin': True},
            xaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    def create_bar_chart(table, xcol, weightcol, format_type, mode, dpurp, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            if key != 'None':
                df = table[key]

                df['all_stops'] = df['tripsh1'] + df['tripsh2'] 

                # Apply mode, purpose, and tour part filters
                for filter_name, filter_value in {'pdpurp': dpurp, 'tmodetp': mode}.items():
                    if filter_value != 'All':
                        df = df[df[filter_name] == filter_value]
                df = df[[xcol,weightcol]].groupby(xcol).sum()[[weightcol]]

                df = df.reset_index()
                df[weightcol] = df[weightcol].astype('int')

                # Exclude outlying 1% of data
                df = df[df[weightcol].cumsum()/df[weightcol].sum() < 0.99]

                # Calculate shares if selected
                if format_type == 'Percent':
                    df[weightcol] = df[weightcol]/df[weightcol].sum()

                trace = go.Bar(
                    x=df[xcol].astype('int').copy(),
                    y=df[weightcol].copy(),
                    name=key,
                    )
                datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type':'category'},
            yaxis={'title': yaxis_title},
            hovermode='closest',
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    scenario_list  = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
   
    trips_by_tour_tbl = compile_csv_to_dict('trips_by_tour.csv', vals)
    stops_by_tour_tbl = compile_csv_to_dict('tour_stops.csv', vals)
    agraph = create_bar_chart_horiz(trips_by_tour_tbl, ['pdpurp','dpurp'], 'trexpfac', format_type, 
        mode, dpurp, 'Purpose', format_type)

    stop_type_dict = {'Entire Tour': 'all_stops', 'First Half': 'tripsh1', 'Second Half': 'tripsh2'}
    stop_type_val = stop_type_dict[stop_type]
    # Use toggle value to define which tour half is displayed
    bgraph = create_bar_chart(stops_by_tour_tbl, stop_type_val, 'toexpfac', format_type, 
        mode, dpurp, 'Stops', format_type)

    return agraph, bgraph

# Length and Distance tab -----------------------------------------------------
# load drop downs
@app.callback(
    [Output('distance-person-type-dropdown', 'options'),
     Output('distance-dpurp-dropdown', 'options'),
     Output('distance-mode-dropdown', 'options')],
    [Input('trips', 'children'),
     Input('dummy_div6', 'children')])
def tour_load_drop_downs(json_data, aux):
    #print('length and distance filter callback')
    person_types = ['All']
    dpurp = ['All']
    mode = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.dpurp.unique()])
    mode.extend([x for x in df['mode'].unique()])

    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp], [{'label': i, 'value': i} for i in mode]


# dynamic headers
@app.callback(
    [Output('distance-graph1-header', 'children'),
     Output('distance-graph2-header', 'children')],
    [Input('distance-person-type-dropdown', 'value'),
     Input('distance-dpurp-dropdown', 'value'),
     Input('distance-mode-dropdown', 'value'),
     Input('distance-format-type', 'value'),
     ])
def update_headers(person_type, dpurp, mode, format_type):

    result = []
    for chart_type in [' Distance', ' Time']:
        if dpurp != 'All':
            header_graph1 = dpurp + ' Trip ' + chart_type
        else:
            header_graph1 = 'Trip ' + chart_type
        if mode != 'All':
            header_graph1 += ' by ' + mode
        if person_type != 'All':
            header_graph1 += ' for ' + person_type

        result.append(header_graph1)

    return result


@app.callback(
    [Output('tour-duration-graph', 'figure'),
     Output('trip-time-graph', 'figure')],
    [Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('distance-person-type-dropdown', 'value'),
     Input('distance-dpurp-dropdown', 'value'),
     Input('distance-mode-dropdown', 'value'),
     Input('distance-format-type', 'value'),
     ]
     # Input('dummy_div6', 'children')]
    )
def update_visuals(scenario1, scenario2, scenario3, person_type, dpurp, mode, format_type):
    #print('length and distance graph callback')
    
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_line_graph(table, xcol, weightcol, person_type, mode, dpurp, format_type, xaxis_title, yaxis_title):
        datalist = []
        for key in table.keys():
            df = table[key]
            df = df[df[xcol] > 0]

            # Apply person type, mode, and purpose filters
            for filter_name, filter_value in {'pptyp': person_type, 'mode': mode, 'dpurp': dpurp}.items():
                if filter_value != 'All': 
                    df = df[df[filter_name] == filter_value]

            df = df[[xcol, weightcol]].groupby(xcol).sum()[[weightcol]]
            df = df.reset_index()
            df[weightcol] = df[weightcol].astype('int')

            # Exclude outlying 1% of data
            df['cumulative_share'] = df['trexpfac'].cumsum()/df['trexpfac'].sum()
            df = df[df['cumulative_share'] < 0.99]

            # Calculate shares if selected
            if format_type == 'Percent':
                df[weightcol] = df[weightcol]/df[weightcol].sum()
            
            trace = go.Scatter(
                line_shape='linear',
                x=df[xcol].copy(),
                y=df[weightcol].copy(),
                name=key
                )
            datalist.append(trace)

        layout = go.Layout(
            barmode='group',
            xaxis={'title': xaxis_title, 'type': 'linear'},
            yaxis={'title': yaxis_title, 'zeroline': False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f'),
            )
        return {'data': datalist, 'layout': layout}

    scenario_list  = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
    
    dist_tbl = compile_csv_to_dict('trip_distance.csv', vals)
    time_tbl = compile_csv_to_dict('trip_time.csv', vals)
    agraph = create_line_graph(dist_tbl, 'travdist_bin', 'trexpfac', person_type, mode, 
        dpurp, format_type, 'Trip Distance (miles)', format_type)
    bgraph = create_line_graph(time_tbl, 'travtime_bin', 'trexpfac', person_type, mode, 
        dpurp, format_type,  format_type + ' Travel Time (min.)', format_type)

    return agraph, bgraph

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
     Input('trips', 'children'),
     Input('tours', 'children'),
     Input('persons', 'children'),
     Input('dpatt-dpurp-dropdown', 'value'),
     Input('dummy_div4', 'children'),
     Input('dummy_div5', 'children')]
    )
def update_visuals(dataset_type, format_type, trips_json, tours_json, pers_json, dpurp,
                   aux, aux1):
    def calc_dpatt_per_person(table, group_cols_list, weight_name, key):
        df = table.copy()
        group_cols_list.append(key)
        #print('inside the thing')
        #print(df)
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

    def create_graph_data(dataset, table, x_col):
        graph_gen_table = []
        for key in dataset.keys():
            trace = go.Bar(
                x=table[x_col].copy(),
                y=table[key].copy(),
                name=key
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
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
        return layout_gen_table 
    #print('This is the Day Pattern callback')
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
    datalist_perc = [] # X by person type and purpose (percent)
    datalist_all_dpurp = []  # X per person by purpose
    datalist_dpurp_gen = []  # X by purpose (percent)

    keys = dataset.keys()
    keyslist = list(keys)
    if "None" in keyslist: keyslist.remove("None")

    ## create total table
    alldict = {}
    # sum dataset
    dataset_sum = map(lambda x: pd.read_json(dataset[x], orient='split')[dataset_weight_col].sum(), keys)
    dataset_dict = dict(zip(keys, dataset_sum))
    alldict['Total ' + dataset_type] = dataset_dict
    # sum persons
    pkeys = pers.keys()
    dtype = 'Total Persons'
    expfac = 'psexpfac'
    sum = map(lambda x: pd.read_json(pers[x], orient='split')[expfac].sum(), pkeys)
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
        df = pd.read_json(dataset[key], orient='split')

        df_dpurp_gen = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp_gen = df_dpurp_gen.rename(columns={dataset_weight_col: key})
        datalist_dpurp_gen.append(df_dpurp_gen[[dataset_dpurp_col, key]]) # X by purpose (percent)

        df_pers = pd.read_json(pers[key], orient='split')
        df_pers = df_pers.groupby(['pptyp']).sum()[['psexpfac']]
        
        # X per person by purpose
        df_dpurp = df.groupby(dataset_dpurp_col).sum()[[dataset_weight_col]].reset_index()
        df_dpurp['psexpfac'] = df_pers['psexpfac'].sum()
        #print(df_dpurp)
        datalist_all_dpurp.append(calc_dpatt_per_person(df_dpurp, [dataset_dpurp_col], dataset_weight_col, key))
        
        # X per person by person type and purpose 
        df = df.groupby(['pptyp', dataset_dpurp_col]).sum()[[dataset_weight_col]].reset_index().merge(df_pers, on='pptyp')
        df_ptype = df[df[dataset_dpurp_col] == dpurp]
        #print('should not see this')
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

# Work tab ------------------------------------------------------------------
@app.callback(
    Output('table-totals-container-work', 'children')
     ,
    [Input('persons', 'children'),
     Input('scenario-1-dropdown', 'value'),
     Input('scenario-2-dropdown', 'value'),
     Input('scenario-3-dropdown', 'value'),
     Input('work-county-data-type', 'value'),
     Input('dummy_div7', 'children')]
    )
def update_visuals(pers_json, scenario1, scenario2, scenario3, data_type, aux):
    #print('work update graph callback')
    def compile_csv_to_dict(filename, scenario_list):
        dfs = list(map(lambda x: pd.read_csv(os.path.join('data', x, filename)), scenario_list))
        dfs_dict = dict(zip(scenario_list, dfs))
        return(dfs_dict)

    def create_totals_table(work_home_tbl, work_from_home_tours_tbl, data_type):
        #taz_geog = pd.read_csv(r'data/data/taz_geography.csv')

        datalist = []
        datalist2 = []
        for key in work_home_tbl.keys():

            df = work_home_tbl[key]
            wfh_total = df[df['pwpcl'] == df['hhparcel']]['psexpfac'].sum()

            df = df.merge(taz_geog, left_on='pwtaz',right_on='taz')
            df = df.merge(taz_geog, left_on='hhtaz',right_on='taz', suffixes=['_work','_home'])

            # Select only work-from-home people
            df_wfh = df[df['hhparcel'] == df['pwpcl']]
            df = df_wfh.groupby('geog_name_work').sum()[['psexpfac']]

            if data_type == 'Distribution':
                df['psexpfac'] = df['psexpfac']/df['psexpfac'].sum()
                format_number_dp = functools.partial(format_number, decimal_places=2)
                # df['psexpfac'] = df['psexpfac'].apply(format_number_dp)
            else:
                format_number_dp = functools.partial(format_number, decimal_places=0)
                # df['psexpfac'] = df['psexpfac'].apply(functools.partial(format_number, decimal_places=0))
                df.loc['Total',:] = df.sum(axis=0)

            df.rename(columns={'psexpfac': key}, inplace=True)
            df = df.reset_index()

            datalist.append(df)

                
            # Tour Rates
            df = work_from_home_tours_tbl[key]
            df = df[df['hhparcel'] == df['pwpcl']].groupby('pdpurp').sum()[['toexpfac']]
            df = df.reset_index()
            df['toexpfac'] = df['toexpfac']/wfh_total*1.0
            df.rename(columns={'toexpfac': key}, inplace=True)
            datalist2.append(df)

        df_scenarios = pd.merge(datalist[0], datalist[1], on=['geog_name_work'], how='outer')
        if len(datalist) == 3:
            df_scenarios = pd.merge(df_scenarios, datalist[2], on=['geog_name_work'], how='outer')
        #print(df_scenarios)
        df_scenarios.rename(columns={'geog_name_work': 'County'}, inplace=True)

        # format numbers with separator
        for i in range(1, len(df_scenarios.columns)):
            df_scenarios.iloc[:, i] = df_scenarios.iloc[:, i].apply(format_number_dp)

        # Calculate tour rates
        df_tour_scenarios = pd.merge(datalist2[0], datalist2[1], on=['pdpurp'])
        if len(datalist) == 3:
            df_tour_scenarios = pd.merge(df_tour_scenarios, datalist2[2], on=['pdpurp'])
        format_number_dp = functools.partial(format_number, decimal_places=2)
        for i in range(1, len(df_tour_scenarios.columns)):
            df_tour_scenarios.iloc[:, i] = df_tour_scenarios.iloc[:, i].apply(format_number_dp)

        t = html.Div(
            [dash_table.DataTable(id='table-totals-work',
                                  columns=[{"name": i, "id": i} for i in df_scenarios.columns],
                                  data=df_scenarios.to_dict('rows'),
                                  style_cell={
                                      'font-family': 'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  ),
             html.Br(),
             html.H2("Tour Rate by Purpose for Work-From-Home Workers"),
             dash_table.DataTable(id='table-totals-work2',
                                  columns=[{"name": i, "id": i} for i in df_tour_scenarios.columns],
                                  data=df_tour_scenarios.to_dict('rows'),
                                  style_cell={
                                      'font-family': 'Segoe UI',
                                      'font-size': 14,
                                      'text-align': 'center'}
                                  ),
             ]
            )

        return t
   
    scenario_list = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario is not None]
    
    #print(vals)
    work_home_tbl = compile_csv_to_dict('work_home_location.csv', vals)
    work_from_home_tours_tbl = compile_csv_to_dict('work_from_home_tours.csv', vals)

    totals_table = create_totals_table(work_home_tbl, work_from_home_tours_tbl, data_type)

    return totals_table

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
     Input('scenario-3-dropdown', 'value'),
     Input('dummy_div3', 'children')]
    )
def update_visuals(data_type, pers_json, scenario1, scenario2, scenario3, aux):
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
        pers_df = map(lambda x: pd.read_json(pers_tbl[x], orient='split'), keys)
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
            margin={'t':20},
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
        return {'data': datalist, 'layout': layout}

    def create_workers_table(wrkrs_tbl):
        #taz_geog = pd.read_csv(r'data/data/taz_geography.csv')

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

    scenario_list = [scenario1, scenario2, scenario3]
    vals = [scenario for scenario in scenario_list if scenario]
   
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
    #print(dtaz_trips)
    return json.dumps(dtaz_trips)


@app.callback(
    Output('dpurp-dropdown2', 'options'),
    [Input('dtaz_trips', 'children'),
     Input('dummy_div_map', 'children')])  # change dummy div name
def map_load_drop_downs(json_data, aux):
    #print('taz load drop downs called')
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    dpurp.extend([x for x in df.dpurp.unique()])
    #print(dpurp)
    return [{'label': i, 'value': i} for i in dpurp]


@app.callback(
    Output('my-graph', 'figure'),
    [Input('dtaz_trips', 'children'),
     Input('dpurp-dropdown2', 'value'),
     Input('dummy_div_map', 'children')])  # change dummy div name
def map_update_graph(json_data, dpurp, aux):
    #print('update map')
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

    gdf = gdf.merge(df, left_on='TAZ', right_on='dtaz')
    gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)
    geojson_data = json.loads(gdf.to_json())

    gdf['mode_share'] = (gdf['Transit']/gdf['sum_trips']) * 100
    trace = go.Choroplethmapbox(geojson=geojson_data, locations=gdf['id'], z=gdf['mode_share'], autocolorscale=False,
                                colorscale="YlGnBu", zauto=False, zmid=12, zmin=0, zmax=15, marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
                                colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                                'title': {"text": 'transit', "side": "bottom"}})


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
        #print('selected data is None')
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
        #print('map graph')
        x = selectedData['points']
        ids = [y['pointNumber'] for y in x]
        gdf = taz_gdf.copy()
        gdf = gdf.merge(df, left_on='TAZ', right_on='dtaz')
        gdf = gdf[gdf['id'].isin(ids)]
        gdf = gdf[['mode', 'trexpfac']].groupby('mode').sum()[['trexpfac']]
        gdf.reset_index(inplace=True)

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

    return {'data': data1, 'layout': layout1}


# Run app ------------------------------------------------------------------------

#app.run_server(debug=True)
if __name__ == '__main__': app.run_server(debug=True)
