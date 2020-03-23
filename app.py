import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objs as go

external_stylesheets = [dbc.themes.MATERIA]#[dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

available_scenarios = [name for name in os.listdir('data') if os.path.isdir(os.path.join('data', name)) and name !='data']

mode_dict = {1 : 'walk', 2 : 'bike', 3 : 'sov', 4 : 'hov2', 5 : 'hov3', 6 : 'w_transit', 7 : 'd_transit', 8 : 'school_bus', 9 : 'other', 0 : 'other'}

scenario_select_layout =  dbc.Card(
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
                        {"label": col, "value": col} for col in available_scenarios
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
                        {"label": col, "value": col} for col in available_scenarios
                    ],
                    value=available_scenarios[1],
                ),
            ]
        ),
        ]
            )

    ],
    className = 'aside-card'
)

tab_trips_mc_filter =  [dbc.Card(
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
            #html.Div(id='df', style={'display': 'none'}),
            html.Div(id='dummy_div'),
        ],
        className = 'bg-light',
      
        )],
    className='aside-card'
)  ] 

tab_trips_mc_layout = [
    dbc.Card(
        dbc.CardBody(
            [
                html.H2("Trip Mode Choice"),
                html.Br(),
                dbc.RadioItems(
                    id='mode-share-type',
                    options=[{'label': i, 'value': i} for i in ['Mode Share', 'Trips by Mode']],
                    value='Mode Share',
                    inline=True
                ),
                dcc.Graph(id='mode-choice-graph'),
                #html.Div(id='dummy_div'),
            ],

        ),
        style= {"margin-top": "20px"},
     
    ),

    dbc.Card(
        dbc.CardBody(
            [
                html.H2('Trip Departure Hour:'),
                dcc.Graph(id='trip-deptm-graph'),
            ]
        ),
        style= {"margin-top": "20px"},
    )
]


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
    fluid = True,
    brand="Soundcast Validation Dashboard",
    brand_href="#"

)

scenario_aside = scenario_select_layout
filter_aside = html.Div(id='tabs-content-filter')
content = html.Div(id='tabs-content')

tabs = dbc.Tabs(
    children=[
        dbc.Tab(label="Trips", tab_id="tab-trips-mc"),
        #dbc.Tab(label="Tours", tab_id="tab-3-example"),
        #dbc.Tab(label="HH & Persons", tab_id="tab-4-example"),
        dbc.Tab(label="Day Pattern", tab_id="tab-day-pattern"),
        #dbc.Tab(label="TAZ Map", tab_id="taz-map")
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
                     ]
                    , width=3
                ), # sidebar
                dbc.Col([tabs, content], width=9) # body of visuals
            ] #end row
            ),
        fluid=True
    ),
    className = "main-body-container"
)

hidden_divs = dbc.Container([
    html.Div(id='trips', style={'display': 'none'}),
    html.Div(id='tours', style={'display': 'none'}),
    html.Div(id='persons', style={'display': 'none'}),
    html.Div(id='households', style={'display': 'none'}),
    html.Div(id='dtaz_trips', style={'display': 'none'}),
    html.Div(id='auto_own', style={'display': 'none'}),
    html.Div(id='workers', style={'display': 'none'},)#,
    #html.Div(id='dummy_div')
])

app.layout = html.Div([navbar, main_body, hidden_divs])

# App Callbacks ----------------------------------------------------------------

# filters
@app.callback(Output('tabs-content-filter', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content_filter(tab):
    if tab == 'tab-trips-mc':
        return tab_trips_mc_filter

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-list', 'active_tab')])
def render_content(tab):
    if tab == 'tab-trips-mc':
        return tab_trips_mc_layout

# Scenario Selection callback
@app.callback(
        [Output('trips', 'children'),
         Output('tours', 'children'),
         #Output('persons', 'children'),
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
    #pers1 = pd.read_csv(os.path.join('data', val1, 'person_type.csv'))
    #pers2 = pd.read_csv(os.path.join('data', val2, 'person_type.csv'))
    #hhs1 = pd.read_csv(os.path.join('data', val1, 'household_size_vehs_workers.csv'))
    #hhs2 = pd.read_csv(os.path.join('data', val2, 'household_size_vehs_workers.csv'))
    #dtaz_trips1 = pd.read_csv(os.path.join('data', val1, 'trip_dtaz.csv'))
    #dtaz_trips2 = pd.read_csv(os.path.join('data', val2, 'trip_dtaz.csv'))
    #auto_own1 = pd.read_csv(os.path.join('data', val1, 'auto_ownership.csv'))
    #auto_own2 = pd.read_csv(os.path.join('data', val2, 'auto_ownership.csv'))
    #wrkrs1 = pd.read_csv(os.path.join('data', val1, 'work_flows.csv'))
    #wrkrs2 = pd.read_csv(os.path.join('data', val2, 'work_flows.csv'))
    #print df2.trexpfac.sum()
    trips = {
        val1: trips1.to_json(orient='split'), 
        val2: trips2.to_json(orient='split')
        }
    tours = {
        val1: tours1.to_json(orient='split'), 
        val2: tours2.to_json(orient='split')
        }
    #persons = {
    #    val1: pers1.to_json(orient='split'), 
    #    val2: pers2.to_json(orient='split')
    #    }
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

    #print datasets.keys()
    return json.dumps(trips), json.dumps(tours)#, json.dumps(persons), json.dumps(households), json.dumps(dtaz_trips), json.dumps(auto_own), json.dumps(workers)
    #return trips, tours, persons, households, dtaz_trips, auto_own, workers

# load trip mode choice tab drop downs
@app.callback(
    [Output('person-type-dropdown', 'options'),
     Output('dpurp-dropdown', 'options')],
     [Input('trips', 'children'),
      Input('dummy_div', 'children')
      ])

def load_drop_downs(json_data, aux):
    print ('trip filter callback')
    person_types = ['All']
    dpurp = ['All']

    datasets = json.loads(json_data)
    key = list(datasets)[0]
    df = pd.read_json(datasets[key], orient='split')
    person_types.extend([x for x in df.pptyp.unique()])
    dpurp.extend([x for x in df.dpurp.unique()])
    return [{'label': i, 'value': i} for i in person_types], [{'label': i, 'value': i} for i in dpurp]


@app.callback([Output('mode-choice-graph', 'figure'),
               Output('trip-deptm-graph', 'figure')],
               [Input('trips', 'children'),
                Input('person-type-dropdown', 'value'),
                Input('dpurp-dropdown', 'value'),
                Input('mode-share-type', 'value')])

def update_graph(json_data, person_type, dpurp, share_type):
    print ('trip_update graph callback')
    datasets = json.loads(json_data)
    data1 = []
    data2 = []
    for key in datasets.keys():
        print (key)
        df = pd.read_json(datasets[key], orient='split')
        if person_type != 'All':
            df =df[df['pptyp'] == person_type] 
        if dpurp != 'All':
            df =df[df['dpurp'] == dpurp]
        if share_type == 'Mode Share':
            df_mode_share= df[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        else:
            df_mode_share= df[['mode','trexpfac']].groupby('mode').sum()[['trexpfac']]
        df_mode_share.reset_index(inplace=True)

        # mode choice graph
        trace1 = go.Bar(
            x=df_mode_share['mode'].copy(),
            y=df_mode_share['trexpfac'].copy(),
            name=key
            )
        data1.append(trace1)

        # trip distance histogram
        df_deptm_share= df[['deptm_hr','trexpfac']].groupby('deptm_hr').sum()[['trexpfac']]/df[['trexpfac']].sum() * 100
        #print (df_deptm_share)
        #df_deptm_share= df[['deptm_hr','trexpfac']].groupby('deptm_hr').sum()[['trexpfac']]
        df_deptm_share.reset_index(inplace=True)
       
        trace2 = go.Bar(
            x=df_deptm_share['deptm_hr'],
            y=df_deptm_share['trexpfac'].astype(int),
            name= key
)
        data2.append(trace2)
        #data.append[trace]

    layout1 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'mode'},
            yaxis={'title': share_type, 'zeroline':False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )

    layout2 = go.Layout(
            barmode = 'group',
            xaxis={'title': 'departure hour'},
            yaxis={'title': 'share', 'zeroline':False},
            hovermode='closest',
            autosize=True,
            font=dict(family='Segoe UI', color='#7f7f7f')
            )
    return {'data': data1, 'layout': layout1}, {'data': data2, 'layout': layout2}


#server = app.server
app.run_server()
#if __name__ == '__main__': app.run_server(debug=False,port=8050,host='0.0.0.0')
