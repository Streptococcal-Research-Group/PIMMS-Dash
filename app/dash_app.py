import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

import pandas as pd

app_title = 'Pimms Dashboard'

# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Available data
test_csvs = list(DATA_PATH.glob('*.csv'))
info_columns = ['seq_id', 'locus_tag', 'type', 'gene', 'start', 'end', 'feat_length', 'product']

# Initialise App
app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True
server = app.server


# Header
def create_header(title):
    return html.Div(id='app-header', children=[
            html.A(
                id='drs-link', children=[
                    html.H1('DRS |'),
                ],
                href="https://digitalresearch.nottingham.ac.uk/",
                style={'display': 'inline-block',
                       'margin-left': '10px',
                       'margin-right': '10px',
                       'text-decoration': 'none',
                       'align': 'center'
                       }
            ),
            html.H2(
                title,
                style={'display': 'inline-block', }
            ),
            html.A(
                id='uni-link', children=[
                    html.H1('UoN'),
                ],
                href="https://www.nottingham.ac.uk/",
                style={'display': 'inline-block',
                       'float': 'right',
                       'margin-right': '10px',
                       'text-decoration': 'none',
                       'color': '#FFFFFF',
                       }
            ),
        ],
        style={'width': '100%', 'display': 'inline-block'}
        )


# First tab on control panel. About App and link to paper.
def control_about_tab():
    return html.Div(children=[
                html.H3(children="PIMMS",
                        style={'font-weight': '400', 'font-size': '20pt',
                               'margin-bottom': '30px', 'text-align': 'center'}
                        ),
                dcc.Markdown("""
                ### Pragmatic Insertional Mutation Mapping system mapping pipeline
                The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been
                developed for simple conditionally essential genome discovery experiments in bacteria.
                Capable of using raw sequence data files alongside a FASTA sequence of the
                reference genome and GFF file, PIMMS will generate a tabulated output of each coding
                sequence with corresponding mapped insertions accompanied with normalized results
                enabling streamlined analysis. This allows for a quick assay of the genome to identify
                conditionally essential genes on a standard desktop computer prioritizing results for
                further investigation.
                """,
                style={'font-weight': '200', 'font-size': '10pt', 'line-height':'1.6'}),
                html.Div([
                    'Reference: ',
                    html.A('PIMMS paper',
                           href='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4391243/pdf/fgene-06-00139.pdf',
                           style={'color': '#FFFFFF'})
                ]),
            ], style={'margin-left': '10px', 'text-align': 'Left'}),


# Second tab on control panel select data for processing.
def control_data_tab():
    return html.Div(children=[
                html.Div(children=[
                    html.Div(className='bac-dropdown-name', children='Bacterial Species',
                             style={'margin-right': '2em', 'verticalAlign': "middle"}),
                    dcc.Dropdown(
                        id='bac-species-dropdown',
                        options=[
                            {'label': 'Species A', 'value': 'specA'},
                            {'label': 'Species B', 'value': 'specB'},
                            {'label': 'Species C', 'value': 'specC'},
                            {'label': 'Species D', 'value': 'specD'}
                        ],
                        value='specA',
                        style={'width': '140px', 'verticalAlign': "middle",
                               'border': 'solid 1px #545454', 'color': 'black'}
                    )
                ], style={'display': 'flex', 'marginTop': '5px', 'justify-content': 'center',
                          'align-items': 'center'}),
                html.Hr(),
                html.Br(),
                html.H3(children='Select upload data', style={'text-align': 'center'}),
                html.Br(),
                html.Div(id='uploaded-data', children=[
                    html.Div(id='up-control-block', children=[
                        html.Div(children='Select control'),
                        dcc.Dropdown(
                            id="control-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in test_csvs],
                            value=0,
                            style={'width': '140px', 'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        ),
                    ], style={'marginRight': '10px'}),
                    html.Div(id='up-test-block', children=[
                        html.Div(children='Select test'),
                        dcc.Dropdown(
                            id="test-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in test_csvs],
                            value=0,
                            style={'width': '140px', 'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        ),
                    ], style={'marginRight': '10px'}),
                    ], style={'display': 'flex', 'marginTop': '5px',
                              'justify-content': 'center', 'align-items': 'center'}
                    ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Button(
                    "Run Selection",
                    id="run-button",
                    style={'display': 'block', 'text-align': 'center', 'padding': '10px',
                           'margin':'auto'}
                ),
                ]),


def merge_control_test(control_df, test_df, on):
    assert (set(on).issubset(control_df.columns)), 'On columns are not present in control_df'
    assert (set(on).issubset(test_df.columns)), 'On columns are not present in test_df'
    ctrl_data_cols = set(control_df.columns) - set(on)
    test_data_cols = set(test_df.columns) - set(on)
    new_control_names = [(i, i + '_control') for i in list(ctrl_data_cols)]
    new_test_names = [(i, i + '_test') for i in list(test_data_cols)]
    control_df.rename(columns=dict(new_control_names), inplace=True)
    test_df.rename(columns=dict(new_test_names), inplace=True)
    df_m = pd.merge(test_df, control_df, how='inner', on=on)
    return df_m


def create_datatable(df_c, df_t):
    df_m = merge_control_test(df_c, df_t, on=info_columns)
    return dash_table.DataTable(id='main_table',
                columns=[{"name": ["Information", i.replace("_", " ")], "id": i, "deletable": True} for i in df_m.columns if i in info_columns] + \
                        [{"name": ['Control', i.replace("_", " ")], "id": i, "selectable": True} for i in df_m.columns if i.endswith('_control')] + \
                        [{"name": ['Test', i.replace("_", " ")], "id": i, "selectable": True} for i in df_m.columns if i.endswith('_test')],
                data=df_m.to_dict('records'),
                merge_duplicate_headers=True,
                filter_action="native",
                sort_mode="multi",
                column_selectable="multi",
                style_table={'height': '525px', 'overflowX': 'scroll', 'overflowY': 'auto'},
                style_cell={
                    'minWidth': '50px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'product'},
                        'overflow': 'hidden',
                        'text-overflow': 'ellipsis',
                        'white-space': 'nowrap'}],
                style_data={
                    'lineHeight': '15px'
                },
                page_size=50,
                sort_action="native",
            )


# Main App
app.layout = html.Div(id='main-app', children=[
                create_header(app_title),
                # Control-Tabs
                html.Div(id='control-tabs', children=[
                    dcc.Tabs(id='tabs', value='tab1', children=[
                        dcc.Tab(
                            label='About',
                            value='tab1',
                            children=control_about_tab(),
                            style={'color': '#000000'}
                        ),
                        dcc.Tab(
                            label='Import Data',
                            value='tab2',
                            children=control_data_tab(),
                            style={'color': '#000000'}
                        ),
                    ]),
                ], style={'display': 'inline-block',
                          'width': '350px',
                          'height': '525px',
                          'margin': '35px',
                          'margin-right': '0px',
                          'background-color': '#333652',
                          'font-size': '10pt',
                          'float': 'left'}
                ),

                html.Div(id='table_preview',
                         style={'display': 'inline-block',
                                'height': '525px',
                                'margin': '35px',
                                'width': '65%',
                                'background-color': '#333652',
                                'font-size': '10pt',
                                'color': 'black'}
                ),
            ])


#Callbacks
@app.callback(
    Output('table', 'style_data_conditional'),
    [Input('table', 'selected_columns')]
)
def update_styles(selected_columns):
    if selected_columns is None:
        return []
    else:
        return [{
            'if': { 'column_id': i },
            'background_color': '#D2F3FF'
        } for i in selected_columns]

@app.callback(
    Output('table_preview', 'children'),
    [Input('run-button', 'n_clicks'),
     Input('test-dropdown', 'value'),
     Input('control-dropdown', 'value')]
)
def onclick(n_clicks,test_path, control_path):
    if n_clicks is not None:
        if test_path not in [0, None] and control_path not in [0, None]:
            test_csv_idx = [i.name for i in test_csvs].index(test_path)
            control_csv_idx = [i.name for i in test_csvs].index(control_path)
            df_c = pd.read_csv(test_csvs[test_csv_idx])
            df_t = pd.read_csv(test_csvs[control_csv_idx])
            return create_datatable(df_c, df_t)
    return html.Div('Select data for import', style={'color': 'white', 'margin': '10px'})


if __name__ == '__main__':
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )