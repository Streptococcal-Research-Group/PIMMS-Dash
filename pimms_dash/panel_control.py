import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from utils import GffDataFrame, PIMMSDataFrame, parse_upload, store_data
from app import app, DATA_PATH, TESTDATA_PATH

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("PIMMS"),
            html.P("""The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been
                    developed for simple conditionally essential genome discovery experiments in bacteria.
                    Capable of using raw sequence data files alongside a FASTA sequence of the
                    reference genome and GFF file, PIMMS will generate a tabulated output of each coding
                    sequence with corresponding mapped insertions accompanied with normalized results
                    enabling streamlined analysis. This allows for a quick assay of the genome to identify
                    conditionally essential genes on a standard desktop computer prioritizing results for
                    further investigation.""", className="card-text"),
            dbc.Button("PIMMS Paper", color="info", external_link=True, target='_blank', className="text-center",
                       href='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4391243/pdf/fgene-06-00139.pdf'),
        ]
    ),
    className="mt-3",
    color="light"
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            dcc.Store(id='run-status'),
            html.P('Comparison Metric:'),
            dcc.Dropdown(
                id='comparison-metric-dropdown',
                options=[
                    {'label': 'Log2 Fold Change', 'value': 'fold_change'},
                    {'label': 'Percentile Rank', 'value': 'pctl_rank'},
                    {'label': 'All', 'value': 'all'}
                ],
                value='fold_change',
                className='text-secondary'
            ),
            html.Hr(),
            html.H4("Select Data", className="text-center"),
            html.Div(children='Select Control'),
            dbc.Select(
                id="control-dropdown",
                options=[{'label': i.name, 'value': i.name} for i in list(TESTDATA_PATH.glob('*.csv'))],
                value=0,
                bs_size="sm"
            ),
            html.Div(children='Select Test'),
            dbc.Select(
                id="test-dropdown",
                options=[{'label': i.name, 'value': i.name} for i in list(TESTDATA_PATH.glob('*.csv'))],
                value=0,
                bs_size="sm",
            ),
            html.Hr(),
            html.Br(),
            html.Div("Select Control Coordinate-Gff"),
            dbc.Select(
                id="gff-dropdown-control",
                options=[{'label': i.name, 'value': i.name} for i in list(TESTDATA_PATH.glob('*.gff'))],
                value=0,
                bs_size="sm",
            ),
            html.Br(),
            html.Div("Select Test Coordinate-Gff"),
            dbc.Select(
                id="gff-dropdown-test",
                options=[{'label': i.name, 'value': i.name} for i in list(TESTDATA_PATH.glob('*.gff'))],
                value=0,
                bs_size="sm",
            ),
            html.Hr(),
            dbc.Button("Run Selection", id="run-button", color="info", className='mx-auto', block=True),
            html.Hr(),
            html.H4("Upload Data", className="text-center"),
            dcc.Upload(id='upload-data', multiple=True, children=[
                dbc.Card(
                    dbc.CardBody("Drag and Drop Files Here"),
                    color="primary", outline=True, inverse=True, className='text-center')
            ]
                       ),
            html.Div(id='output-data-upload')
        ]
    ),
    className="mt-3",
    color="light"
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Datatable Options"),
            dbc.FormGroup(
                [
                    dbc.Label("Toggle display:", html_for="datatable-checklist"),
                    dbc.Checklist(
                        options=[
                            {'label': 'Highlight', 'value': 'hl'},
                            {'label': 'Show Filter', 'value': 'filter'},
                            {'label': 'Simple Table (NRM NIM)', 'value': 'simple'},
                        ],
                        value=['hl', 'filter', 'simple'],
                        id="datatable-checklist",
                        switch=True,
                    ),
                    dbc.Label("Number of rows per page:", html_for="datatable-numrows"),
                    dbc.Input(
                        id="datatable-numrows",
                        type="number",
                        placeholder="Rows per page",
                        value=20,
                        bs_size="sm"
                    ),
                ],
                row=False,
            ),
            html.Hr(),
            html.H5("Histogram Options"),
            dbc.FormGroup(
                [
                    dbc.Label("Figure type:", html_for="hist-dropdown-type"),
                    dcc.Dropdown(
                        id="hist-dropdown-type",
                        options=[
                            {'label': 'Type 1', 'value': 'type1'},
                            {'label': 'Type 2', 'value': 'type2'},
                        ],
                        value='type1',
                        className='text-secondary',
                    ),
                    dbc.Label("Bin Size:", html_for='hist-bin-size'),
                    dbc.Input(
                        id='hist-bin-size',
                        type='number',
                        placeholder="Number of bins",
                        value=1,
                        bs_size="sm"
                    ),
                ],
                row=False
            ),
            html.Hr(),
            html.H5("Venn Options"),
            dbc.FormGroup(
                [
                    dbc.Label(html.Div("NIM score threshold", id='venn-slider-label'),
                              html_for='venn-slider'),
                    dcc.Slider(id='venn-slider', value=0, min=0, max=50, step=1),
                    dbc.Label(html.Div("Inserts percentile range", id='venn-inserts-slider-label'),
                              html_for='venn-inserts-slider'),
                    dcc.RangeSlider(id='venn-inserts-slider', min=0, max=100, step=1, value=[0, 100]),
                ]
            ),
            html.Hr(),
            html.H5("Genome Scatter Options"),
            dbc.FormGroup(
                [
                    dbc.Label("Scatter Scale:", html_for="scatter-checklist"),
                    dbc.Checklist(
                        options=[
                            {'label': 'Log scale', 'value': 'log'},
                        ],
                        value=['log'],
                        id="scatter-checklist",
                        switch=True,
                    ),
                ]
            ),
            html.Hr(),
            html.H5("Circos Options"),
            dbc.FormGroup(
                [
                    dbc.Label("Toggle display:", html_for="circos-checklist"),
                    dbc.Checklist(
                        options=[
                            {'label': 'Hide values where both scores = 0', 'value': 'hide_zero'},
                        ],
                        value=['hide_zero'],
                        id="circos-checklist",
                        switch=True,
                    ),
                ]
            ),
        ]
    ),
    className="mt-3",
    color="light"
)

control_tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="About"),
        dbc.Tab(tab2_content, label="Data"),
        dbc.Tab(tab3_content, label="Options"),
    ],
    active_tab="tab-1"
)


@app.callback(
    Output("run-status", "data"),
    [Input("run-button", "n_clicks"),
     State("test-dropdown", "value"),
     State("control-dropdown", "value"),
     State("gff-dropdown-control", "value"),
     State("gff-dropdown-test", "value"),
     State("session-id", "children")],
    prevent_initial_call=True
)
def run_selection(run_clicks, test_filename, control_filename, control_gff_filename, test_gff_filename, session_id):

    # Create empty run status
    run_status = {'pimms': None, 'gff_control': None, 'gff_test': None}

    # Prevent update if all dropdowns unselected.
    if ((test_filename in [0, None]) or (control_filename in [0, None])) and \
            (control_gff_filename in [0, None]) and \
            (test_gff_filename in [0, None]):
        raise PreventUpdate

    # List all available .csv and .gff files
    session_upload_dir = DATA_PATH.joinpath('session_data', session_id, "uploaded")
    all_csvs = list(TESTDATA_PATH.glob('*.csv')) + list(session_upload_dir.glob('*.csv'))
    all_gffs = list(TESTDATA_PATH.glob('*.gff')) + list(session_upload_dir.glob('*.gff'))

    # Read control coordinate gff file and store
    if control_gff_filename not in [0, None]:
        control_gff_path = [i for i in all_gffs if i.name == control_gff_filename][0]
        try:
            gff_df_control = GffDataFrame(control_gff_path)
            store_data(gff_df_control.to_json(), 'gff_df_control', session_id)
            run_status['gff_control'] = True
        except Exception as e:
            # Todo log exception
            run_status['gff_control'] = False

    # Read test coordinate gff file and store
    if test_gff_filename not in [0, None]:
        test_gff_path = [i for i in all_gffs if i.name == test_gff_filename][0]
        try:
            gff_df_test = GffDataFrame(test_gff_path)
            store_data(gff_df_test.to_json(), 'gff_df_test', session_id)
            run_status['gff_test'] = True
        except Exception as e:
            # Todo log exception
            run_status['gff_test'] = False

    # Read pimms csv files and store
    if (test_filename not in [0, None]) and (control_filename not in [0, None]):
        # Get full filepaths from dropdown selection
        try:
            test_path = [i for i in all_csvs if i.name == test_filename][0]
            control_path = [i for i in all_csvs if i.name == control_filename][0]
            pimms_df = PIMMSDataFrame(control_path, test_path)
            store_data(pimms_df.to_json(), 'pimms_df', session_id)
            run_status['pimms'] = True
        except Exception as e:
            # Todo Log exception
            run_status['pimms'] = False

    return run_status


@app.callback(
    [Output("run-button", "color"),
     Output("run-button", "children")],
    [Input("test-dropdown", "value"),
     Input("control-dropdown", "value"),
     Input("gff-dropdown-control", "value"),
     Input("gff-dropdown-test", "value"),
     Input("run-status", "data")],
    prevent_initial_call=True
)
def run_button_color(dropdown1, dropdown2, dropdown3, dropdown4, run_status):
    ctx = callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] != "run-status":
        return "info", "Run Selection"
    elif run_status['pimms']:
        return "success", "Successful"
    elif not run_status['pimms']:
        return "danger", "Failed"
    else:
        raise ValueError


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('upload-data', 'last_modified'),
     State("session-id", "children")],
    prevent_initial_call=True
)
def upload_new_file(list_of_contents, list_of_names, list_of_dates, session_id):
    """ Callback to parse and save uploaded data"""
    session_upload_dir = DATA_PATH.joinpath('session_data', session_id, "uploaded")
    if not session_upload_dir.exists():
        session_upload_dir.mkdir(parents=True, exist_ok=True)
    if list_of_contents is not None:
        children = [parse_upload(c, n, session_upload_dir) for c, n in zip(list_of_contents, list_of_names)]
        return children


@app.callback(
    [Output('test-dropdown', 'options'),
     Output('control-dropdown', 'options'),
     Output('gff-dropdown-test', 'options'),
     Output('gff-dropdown-control', 'options')],
    [Input('test-dropdown', "value"),
     Input('control-dropdown', "value"),
     Input('gff-dropdown-test', "value"),
     Input('gff-dropdown-control', "value"),
     Input('output-data-upload', 'children'),
     State("session-id", "children")],
    prevent_initial_call=True
)
def update_dropdowns(dropdown1, dropdown2, dropdown3, dropdown4, upload_message, session_id):
    """Callback to update the select data dropdowns"""
    callback_trigger = callback_context.triggered[0]['prop_id'].split('.')[0]
    # Prevent update if a failed upload triggered callback
    if callback_trigger == 'output-data-upload':
        if not upload_message or not upload_message[0]:
            raise PreventUpdate
        elif not upload_message[0].startswith('Uploaded'):
            raise PreventUpdate

    session_upload_dir = DATA_PATH.joinpath('session_data', session_id, "uploaded")
    all_csvs = list(TESTDATA_PATH.glob('*.csv')) + list(session_upload_dir.glob('*.csv'))
    all_gffs = list(TESTDATA_PATH.glob('*.gff')) + list(session_upload_dir.glob('*.gff'))

    test_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown2}
                             for i in all_csvs]
    control_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown1}
                                for i in all_csvs]
    test_gff_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown4}
                                 for i in all_gffs]
    control_gff_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown3}
                                    for i in all_gffs]
    return test_dropdown_options, control_dropdown_options, test_gff_dropdown_options, control_gff_dropdown_options

@app.callback(
    [Output('test-dropdown', "valid"),
     Output('test-dropdown', "invalid"),
     Output('control-dropdown', "valid"),
     Output('control-dropdown', "invalid"),
     Output('gff-dropdown-control', "valid"),
     Output('gff-dropdown-control', "invalid"),
     Output('gff-dropdown-test', "valid"),
     Output('gff-dropdown-test', "invalid")],
    [Input("run-status", "data"),
     Input('test-dropdown', "value"),
     Input('control-dropdown', "value"),
     Input('gff-dropdown-test', "value"),
     Input('gff-dropdown-control', "value"),],
    prevent_initial_call=True
)
def run_status_feedback(run_status, dropdown1, dropdown2, dropdown3, dropdown4):
    if run_status is None:
        raise PreventUpdate
    callback_trigger = callback_context.triggered[0]['prop_id'].split('.')[0]

    output = [
        run_status['pimms'],
        not run_status['pimms'],
        run_status['pimms'],
        not run_status['pimms'],
        run_status['gff_control'],
        not run_status['gff_control'],
        run_status['gff_test'],
        not run_status['gff_test']
    ]
    # If this callback was triggered by change in dropdown not a run. Remove dropdown ticks.
    if callback_trigger != 'run-status':
        output = [None]*8
    return tuple(output)