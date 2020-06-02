import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objs as go

import pandas as pd

intro_text = """
Prototype dashboard
"""

global_width = '70%'
graph_dimensions = ["x", "y", "color", "facet_col", "facet_row"]

# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()  # TODO create data folder within package, remove test_data_path

# Available data
test_csvs = list(DATA_PATH.glob('*.csv'))

# Read data for startup
df = pd.read_csv(test_csvs[0])

# Initialise App
app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True
server = app.server

# Header
header = html.Div(
    id="app-header",
    children=[
        html.Img(src=app.get_asset_url("DRS-header.png"), className="logo"),
    ],
)

# Main App
app.layout = html.Div(
    children=[
        header,
        html.Br(),
        html.Details(
            id="intro-text",
            children=[html.Summary(html.B("About This App")), dcc.Markdown(intro_text)],
        ),
        html.Br(),
        html.Div([
            html.Label('Select CSV'),
            dcc.Dropdown(
                id='csv_dropdown',
                options=[{'label': i.name, 'value': i.name} for i in test_csvs],
                value=test_csvs[0].name,
                placeholder='... Select CSV'
            )],
            style={'width': '20%', 'margin-bottom': '20px'}),
        # Hidden div inside the app that stores the selected csv value as json
        html.Div(id='csv-idx-store', style={'display': 'none'}),
        html.Br(),
        html.Div([dcc.Markdown('''## Table Preview'''),
                  dcc.Markdown("----------------",
                               style={'width': global_width}),
                  ]),
        html.Br(),
        html.Div(id='select_rows',
                 children=[
                     html.Label('Select Rows to Preview'),
                     dcc.RangeSlider(
                         id='row-slider',
                         min=0,
                         max=len(df),
                         value=[0, 5],
                         step=5,
                         marks={'0': '0', str(int(len(df) / 2)): str(int(len(df) / 2)), str(len(df)): str(len(df))}
                     )],
                 style={'width': global_width, 'margin-bottom': '10px'}),
        html.Br(),
        html.Div(id='select_columns',
                 children=[html.Label('Select Columns'),
                           dcc.Dropdown(id='column_dropdown',
                                        options=[{'label': col, 'value': col} for col in df.columns],
                                        value=df.columns[0:10],
                                        multi=True
                                        )],
                 style={'width': global_width, 'margin-bottom': '10px'}),
        html.Br(),
        html.Div(id='table_preview',
                 style={'width': global_width}),
        html.Br(),
        html.Div([dcc.Markdown('''## Missing Data'''),
                  dcc.Markdown("----------------",
                               style={'width': global_width}),
                  dcc.Markdown("Placeholder - Insert missing data report",
                               style={'width': global_width}),
                  ]),
        html.Br(),
        html.Br(),
        html.Div([dcc.Markdown('''## Analysis'''),
                  dcc.Markdown("----------------",
                               style={'width': global_width}),
                  ]),
        html.Br(),
        html.Div(id='graph1_selection',
                 style={"width": global_width}),
        html.Br(),
        dcc.Graph(id="graph1", style={"width": global_width}),
    ]
)


# Interactivity

@app.callback(
    dash.dependencies.Output('csv-idx-store', 'children'),
    [dash.dependencies.Input('csv_dropdown', 'value')])
def select_csv(value):
    csv_idx = [i.name for i in test_csvs].index(value)
    return csv_idx


@app.callback(
    dash.dependencies.Output('select_columns', 'children'),
    [dash.dependencies.Input('csv-idx-store', 'children')])
def update_select_columns(csv_idx):
    csv_path = test_csvs[csv_idx]
    dff = pd.read_csv(csv_path)
    return [html.Label('Select Columns'),
            dcc.Dropdown(id='column_dropdown',
                         options=[{'label': col, 'value': col} for col in dff.columns],
                         value=dff.columns[0:10],
                         multi=True
                         )]


@app.callback(
    dash.dependencies.Output('select_rows', 'children'),
    [dash.dependencies.Input('csv-idx-store', 'children')])
def update_select_rows(csv_idx):
    csv_path = test_csvs[csv_idx]
    dff = pd.read_csv(csv_path)
    l = len(dff)
    return [html.Label('Select Rows to Preview'),
            dcc.RangeSlider(
                id='row-slider',
                min=0,
                max=l,
                value=[0, 5],
                step=5,
                marks={'0': '0', str(int(l / 2)): str(int(l / 2)), str(l): str(l)}
            )]


@app.callback(
    dash.dependencies.Output('table_preview', 'children'),
    [dash.dependencies.Input('csv-idx-store', 'children'),
     dash.dependencies.Input('row-slider', 'value'),
     dash.dependencies.Input('column_dropdown', 'value')])
def update_preview_table(csv_idx, row_value, col_value):
    csv_path = test_csvs[csv_idx]
    dff = pd.read_csv(csv_path)
    subset_df = dff[row_value[0]:row_value[1]]
    if set(col_value).intersection(set(dff.columns)):
        subset_df = subset_df[col_value]
    return html.Div(dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in subset_df.columns],
        data=subset_df.to_dict('records'),
    ),
    )

# Graphs
@app.callback(
    dash.dependencies.Output('graph1_selection', 'children'),
    [dash.dependencies.Input('csv-idx-store', 'children')])
def update_select_columns(csv_idx):
    csv_path = test_csvs[csv_idx]
    dff = pd.read_csv(csv_path)
    options = [{'label': col, 'value': col} for col in dff.columns]
    style_dict = {
        'width':'10%',
        'display':'inline-block',
        'verticalAlign':"middle",
        'margin-right':'2em',
    }
    return html.Div([
        html.Div([d + ":", dcc.Dropdown(id=d, options=options)], style=style_dict) for d in graph_dimensions],
    )


@app.callback(
    dash.dependencies.Output("graph1", "figure"),
    [dash.dependencies.Input('csv-idx-store', 'children'),
     *(dash.dependencies.Input(d, "value") for d in graph_dimensions)])
def make_figure(csv_idx, x, y, color, facet_col, facet_row):
    csv_path = test_csvs[csv_idx]
    dff = pd.read_csv(csv_path)
    return px.scatter(
        dff,
        x=x,
        y=y,
        color=color,
        facet_col=facet_col,
        facet_row=facet_row,
        height=700,
    )


if __name__ == '__main__':
    app.run_server(debug=True)
