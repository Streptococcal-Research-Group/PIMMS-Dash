import logging
import pathlib

import dash_bootstrap_components as dbc
import dash

# Initialise App
app_title = 'PIMMS | Dashboard'
app = dash.Dash(__name__, title=app_title, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions'] = True
server = app.server

# Initialise Logging
logging.basicConfig(level=logging.INFO)


# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath('data').resolve()
TESTDATA_PATH = DATA_PATH.joinpath('uploaded').resolve()

# Plotly standard graph format
plotly_template = 'simple_white'
