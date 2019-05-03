import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas
import os
from app import app
import dash_bootstrap_components as dbc

#base_dir = os.path.join(os.getcwd(), 'data')
available_scenarios = [name for name in os.listdir('data') if os.path.isdir(os.path.join('data', name))]

tab_1_layout = dbc.Card(
    dbc.CardBody(
        [
             html.H2('Select two scenarios to compare:'),
             html.Br(),
             html.H4('Scenario 1:'),
             dcc.Dropdown(
                options=[{'label': i, 'value': i} for i in available_scenarios],
                value=available_scenarios[0],
                id='scenario-1-dropdown'
                ),
            html.Br(),
            html.H4('Scenario 2:'),
            dcc.Dropdown(
                options=[{'label': i, 'value': i} for i in available_scenarios],
                value=available_scenarios[1],
                id='scenario-2-dropdown'
                ),
        ]
    ),
    className="mt-3",
)

#tab_1_layout = html.Div([
#    html.H2('Select two scenarios to compare:'),
#    html.Br(),
#    html.H4('Scenario 1:'),
#    dcc.Dropdown(
#            options=[{'label': i, 'value': i} for i in available_scenarios],
#            value=available_scenarios[0],
#            id='scenario-1-dropdown'
#        ),
#    html.Br(),
#    html.H4('Scenario 2:'),
#    dcc.Dropdown(
#            options=[{'label': i, 'value': i} for i in available_scenarios],
#            value=available_scenarios[1],
#            id='scenario-2-dropdown'
#        ),
#])

