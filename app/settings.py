import pathlib

# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Plotly standard graph format
plotly_template = 'simple_white'