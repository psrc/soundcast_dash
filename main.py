import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from tabs import tab_1, tab_2, tab_3, tab_4, tab_day_pattern, taz_map
#from tabs import tab_2
#from tabs import tab_3
#from tabs import tab_4
#from tabs import tab_day_pattern
#from tabs import taz_map
from app import app
import pandas as pd
import os
import json
import plotly.graph_objs as go

#app = dash.Dash()

mode_dict = {1 : 'walk', 2 : 'bike', 3 : 'sov', 4 : 'hov2', 5 : 'hov3', 6 : 'w_transit', 7 : 'd_transit', 8 : 'school_bus', 9 : 'other', 0 : 'other'}

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
scenario_aside = tab_1.tab_1_layout
filter_aside = html.Div(id='tabs-content-filter')
content = html.Div(id='tabs-content-example')

tabs = dbc.Tabs(
    children=[
        dbc.Tab(label="Trips", tab_id="tab-2-example"),
        dbc.Tab(label="Tours", tab_id="tab-3-example"),
        dbc.Tab(label="HH & Persons", tab_id="tab-4-example"),
        dbc.Tab(label="Day Pattern", tab_id="tab-day-pattern"),
        dbc.Tab(label="TAZ Map", tab_id="taz-map")
    ],
    id="tabs-example"
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
    html.Div(id='workers', style={'display': 'none'})
])


app.layout = html.Div([navbar, main_body, hidden_divs])


@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'active_tab')])
def render_content(tab):
    if tab == 'tab-2-example':
        return tab_2.tab_2_layout
    elif tab == 'tab-3-example':
        return tab_3.tab_3_layout
    elif tab == 'tab-4-example':
        return tab_4.tab_4_layout
    elif tab == 'tab-day-pattern':
        return tab_day_pattern.tab_day_pattern_layout
    elif tab == 'taz-map':
        return taz_map.taz_map_layout

@app.callback(Output('tabs-content-filter', 'children'),
              [Input('tabs-example', 'active_tab')])
def render_content_filter(tab):
    if tab == 'tab-2-example':
        return tab_2.tab_2_filter
    elif tab == 'tab-3-example':
        return tab_3.tab_3_filter
    elif tab == 'tab-day-pattern':
        return tab_day_pattern.tab_day_pattern_filter
    elif tab == 'taz-map':
        return taz_map.taz_map_filter
    else:
        return None

# Tab 1 callback
@app.callback(
        [Output('trips', 'children'),
         Output('tours', 'children'),
         Output('persons', 'children'),
         Output('households', 'children'),
         Output('dtaz_trips', 'children'),
         Output('auto_own', 'children'),
         Output('workers', 'children')],
         [Input('scenario-1-dropdown', 'value'),
          Input('scenario-2-dropdown', 'value')])

def page_1_dropdown(val1, val2):
    trips1 = pd.read_csv(os.path.join('data', val1, 'trip_purpose_mode.csv'))
    trips2 = pd.read_csv(os.path.join('data', val2, 'trip_purpose_mode.csv'))
    tours1 = pd.read_csv(os.path.join('data', val1, 'tour_purpose_mode.csv'))
    tours2 = pd.read_csv(os.path.join('data', val2, 'tour_purpose_mode.csv'))
    pers1 = pd.read_csv(os.path.join('data', val1, 'person_type.csv'))
    pers2 = pd.read_csv(os.path.join('data', val2, 'person_type.csv'))
    hhs1 = pd.read_csv(os.path.join('data', val1, 'household_size_vehs_workers.csv'))
    hhs2 = pd.read_csv(os.path.join('data', val2, 'household_size_vehs_workers.csv'))
    dtaz_trips1 = pd.read_csv(os.path.join('data', val1, 'trip_dtaz.csv'))
    dtaz_trips2 = pd.read_csv(os.path.join('data', val2, 'trip_dtaz.csv'))
    auto_own1 = pd.read_csv(os.path.join('data', val1, 'auto_ownership.csv'))
    auto_own2 = pd.read_csv(os.path.join('data', val2, 'auto_ownership.csv'))
    wrkrs1 = pd.read_csv(os.path.join('data', val1, 'work_flows.csv'))
    wrkrs2 = pd.read_csv(os.path.join('data', val2, 'work_flows.csv'))
    #print df2.trexpfac.sum()
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
    households = {
         val1: hhs1.to_json(orient='split'), 
         val2: hhs2.to_json(orient='split')
        }
    dtaz_trips = {
         val1: dtaz_trips1.to_json(orient='split'), 
         val2: dtaz_trips2.to_json(orient='split')
        }
    auto_own = {
         val1: auto_own1.to_json(orient='split'), 
         val2: auto_own2.to_json(orient='split')
        }
    workers = {
        val1: wrkrs1.to_json(orient='split'), 
        val2: wrkrs2.to_json(orient='split')
        }

    #print datasets.keys()
    return json.dumps(trips), json.dumps(tours), json.dumps(persons), json.dumps(households), json.dumps(dtaz_trips), json.dumps(auto_own), json.dumps(workers)

## Tab 1 callback
#@app.callback(dash.dependencies.Output('intermediate-value2', 'children'),
#              [dash.dependencies.Input('scenario-2-dropdown', 'value')])

#def page_2_dropdown(val):
#    df = pd.read_csv(os.path.join('data', val, 'trips.csv'))
#    print df.columns
#    return df.to_json(orient = 'split')


#app.css.append_css({
#    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
#})

if __name__ == '__main__': app.run_server(debug=True,port=8050,host='0.0.0.0') #app.run_server(debug=True, port=8051)