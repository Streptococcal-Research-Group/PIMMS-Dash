import logging
import pathlib

import dash_bootstrap_components as dbc
import dash
from flask_caching import Cache

# Initialise App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.config['suppress_callback_exceptions'] = True
server = app.server

# Initialise Logging
logging.basicConfig(level=logging.INFO)

# Create cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 10
})

# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath('data').resolve()
UPLOAD_PATH = DATA_PATH.joinpath('uploaded').resolve()

# Plotly standard graph format
plotly_template = 'simple_white'
