import dash
import dash_bootstrap_components as dbc
import yaml

DEPLOY = True

config = yaml.safe_load(open("config.yaml"))

if DEPLOY:
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/soundcast_dash/')
    app.config.suppress_callback_exceptions = True
    server = app.server
else:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    #server = app.server
    app.config.suppress_callback_exceptions = True