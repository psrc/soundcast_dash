import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from tabs import tab_1
from tabs import tab_2
from tabs import tab_3
from app import app
import pandas as pd
import os
import json

#app = dash.Dash()

#app.config['suppress_callback_exceptions'] = True


mode_dict = {1 : 'walk', 2 : 'bike', 3 : 'sov', 4 : 'hov2', 5 : 'hov3', 6 : 'w_transit', 7 : 'd_transit', 8 : 'school_bus', 9 : 'other', 0 : 'other'}


app.layout = dbc.Container([
    html.H2('Soundcast Validation Dashboard', style = {'position': 'sticky', 'top': '0'}),
    dbc.Tabs(
        [
        dbc.Tab(label="Select Scenario", tab_id="tab-1-example"),
        dbc.Tab(label="Trips", tab_id="tab-2-example"),
        dbc.Tab(label="Tours", tab_id="tab-3-example"),
        ],
        id="tabs-example",
        active_tab="tab-1-example",
        ),
    html.Div(id='trips', style={'display': 'none'}),
    html.Div(id='tours', style={'display': 'none'}),
    html.Div(id='intermediate-value2', style={'display': 'none'}),
    html.Div(id='tabs-content-example')
])

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'active_tab')])
def render_content(tab):
    if tab == 'tab-1-example':
        return tab_1.tab_1_layout
    elif tab == 'tab-2-example':
        return tab_2.tab_2_layout
    elif tab == 'tab-3-example':
        return tab_3.tab_3_layout

# Tab 1 callback
@app.callback(
        [Output('trips', 'children'),
         Output('tours', 'children')],
         [Input('scenario-1-dropdown', 'value'),
          Input('scenario-2-dropdown', 'value')])

def page_1_dropdown(val1, val2):
    trips1 = pd.read_csv(os.path.join('data', val1, 'trips.csv'))
    trips2 = pd.read_csv(os.path.join('data', val2, 'trips.csv'))
    tours1 = pd.read_csv(os.path.join('data', val1, 'tours.csv'))
    tours2 = pd.read_csv(os.path.join('data', val2, 'tours.csv'))
    #print df2.trexpfac.sum()
    trips = {
        val1: trips1.to_json(orient='split'), 
        val2: trips2.to_json(orient='split')
        }
    tours = {
        val1: tours1.to_json(orient='split'), 
        val2: tours2.to_json(orient='split')
        }
    #print datasets.keys()
    return json.dumps(trips), json.dumps(tours)

## Tab 1 callback
#@app.callback(dash.dependencies.Output('intermediate-value2', 'children'),
#              [dash.dependencies.Input('scenario-2-dropdown', 'value')])

#def page_2_dropdown(val):
#    df = pd.read_csv(os.path.join('data', val, 'trips.csv'))
#    print df.columns
#    return df.to_json(orient = 'split')


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug='False',port=8080,host='0.0.0.0')