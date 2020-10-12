import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from utils import GffDataFrame, PIMMSDataFrame, parse_upload
from app import app, DATA_PATH

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
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            dcc.Store(id='pimms-store'),
            dcc.Store(id='gff-store'),
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
                options=[{'label': i.name, 'value': i.name} for i in list(DATA_PATH.glob('*.csv'))],
                value=0,
                bs_size="sm"
            ),
            html.Div(children='Select Test'),
            dbc.Select(
                id="test-dropdown",
                options=[{'label': i.name, 'value': i.name} for i in list(DATA_PATH.glob('*.csv'))],
                value=0,
                bs_size="sm",
            ),
            html.Br(),
            html.Div("Select Gff file (Optional)"),
            dbc.Select(
                id="gff-dropdown",
                options=[{'label': i.name, 'value': i.name} for i in list(DATA_PATH.glob('*.gff'))],
                value=0,
                bs_size="sm"
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
    [Output("pimms-store", "data"),
     Output("gff-store", "data"),
     Output("run-status", "data")],
    [Input("run-button", "n_clicks"),
     State("test-dropdown", "value"),
     State("control-dropdown", "value"),
     State("gff-dropdown", "value")],
    prevent_initial_call=True
)
def run_selection(run_clicks, test_filename, control_filename, gff_filename):
    run_status = {'pimms': None, 'gff': None}
    gff_df_json = None
    pimms_df_json = None
    if ((test_filename in [0, None]) or (control_filename in [0, None])) and (gff_filename in [0, None]):
        raise PreventUpdate

    if gff_filename not in [0, None]:
        gff_path = [i for i in list(DATA_PATH.glob('*.gff')) if i.name == gff_filename][0]
        try:
            gff_df = GffDataFrame(gff_path)
            gff_df_json = gff_df.to_json()
            run_status['gff'] = True
        except Exception as e:
            # Todo log exception
            run_status['gff'] = False

    if (test_filename not in [0, None]) and (control_filename not in [0, None]):
        # Get full filepaths from dropdown selection
        try:
            test_path = [i for i in list(DATA_PATH.glob('*.csv')) if i.name == test_filename][0]
            control_path = [i for i in list(DATA_PATH.glob('*.csv')) if i.name == control_filename][0]
            pimms_df = PIMMSDataFrame(control_path, test_path)
            pimms_df_json = pimms_df.to_json()
            run_status['pimms'] = True
        except Exception as e:
            # Todo Log exception
            run_status['pimms'] = False

    return pimms_df_json, gff_df_json, run_status


@app.callback(
    [Output("run-button", "color"),
     Output("run-button", "children")],
    [Input("test-dropdown", "value"),
     Input("control-dropdown", "value"),
     Input("run-status", "data")],
    prevent_initial_call=True
)
def run_button_color(dropdown1, dropdown2, run_status):
    ctx = callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] != "run-status":
        return "info", "Run Selection"
    elif (run_status['pimms'] and run_status['gff']) or (run_status['pimms'] and run_status['gff'] is None):
        return "success", "Successful"
    elif not run_status['pimms']:
        return "danger", "Failed"
    else:
        raise ValueError


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('upload-data', 'last_modified')],
    prevent_initial_call=True
)
def upload_new_file(list_of_contents, list_of_names, list_of_dates):
    """ Callback to parse and save uploaded data"""
    if list_of_contents is not None:
        children = [parse_upload(c, n) for c, n in zip(list_of_contents, list_of_names)]
        return children


@app.callback(
    [Output('test-dropdown', 'options'),
     Output('control-dropdown', 'options')],
    [Input('test-dropdown', "value"),
     Input('control-dropdown', "value"),
     Input('output-data-upload', 'children')],
    prevent_initial_call=True
)
def update_dropdowns(dropdown1, dropdown2, upload_message):
    """Callback to update the select data dropdowns"""
    callback_trigger = callback_context.triggered[0]['prop_id'].split('.')[0]
    if callback_trigger == 'output-data-upload':
        if not upload_message or not upload_message[0]:
            raise PreventUpdate
        elif not upload_message[0].startswith('Uploaded'):
            raise PreventUpdate

    test_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown2}
                             for i in list(DATA_PATH.glob('*.csv'))]
    control_dropdown_options = [{'label': i.name, 'value': i.name, 'disabled': i.name == dropdown1}
                                for i in list(DATA_PATH.glob('*.csv'))]
    return test_dropdown_options, control_dropdown_options

@app.callback(
    [Output('test-dropdown', "valid"),
     Output('test-dropdown', "invalid"),
     Output('control-dropdown', "valid"),
     Output('control-dropdown', "invalid"),
     Output('gff-dropdown', "valid"),
     Output('gff-dropdown', "invalid")],
    [Input("run-status", "data")],
    prevent_initial_call=True
)
def run_status_feedback(run_status):
    return run_status['pimms'], not run_status['pimms'], run_status['pimms'], not run_status['pimms'],\
           run_status['gff'], not run_status['gff']