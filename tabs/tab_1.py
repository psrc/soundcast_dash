import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas
import os
from app import app
import dash_bootstrap_components as dbc

available_scenarios = [name for name in os.listdir('data') if os.path.isdir(os.path.join('data', name))]


tab_1_layout =  dbc.Card(
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
    #className = 'bg-light',
    className = 'aside-card'
)
