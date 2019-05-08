import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from tabs import tab_1
from tabs import tab_2
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
        ],
        id="tabs-example",
        active_tab="tab-1-example",
        ),
    html.Div(id='intermediate-value', style={'display': 'none'}),
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

# Tab 1 callback
@app.callback(Output('intermediate-value', 'children'),
              [Input('scenario-1-dropdown', 'value'),
               Input('scenario-2-dropdown', 'value')])

def page_1_dropdown(val1, val2):
    df1 = pd.read_csv(os.path.join('data', val1, 'trips.csv'))
    #return df1.to_json(orient = 'split')
    df2 = pd.read_csv(os.path.join('data', val2, 'trips.csv'))
    #print df1.trexpfac.sum()
    #print df2.trexpfac.sum()
    datasets = {
         val1: df1.to_json(orient='split'),
         val2: df2.to_json(orient='split'),
     }
    return json.dumps(datasets)

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