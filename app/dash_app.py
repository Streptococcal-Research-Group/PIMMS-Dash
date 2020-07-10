# Dash and plotly
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Other
import numpy as np

# local imports
from settings import DATA_PATH
from utils import GffDataFrame, PIMMSDataFrame, fold_change_comparision,percentile_rank_comparision, parse_upload
from circos import create_pimms_circos
from figures import *

# Globals
app_title = 'Pimms Dashboard'
tab_height = '80vh'

# Available data
testing_csvs = list(DATA_PATH.glob('*.csv'))
test_gff = list(DATA_PATH.glob('*.gff'))

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
        style={'width': '100%', 'display': 'inline-block', 'color': 'white'}
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
                    style={'font-weight': '200', 'font-size': '10pt', 'line-height': '1.6'}),
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
                    html.Div('Comparision Metric',
                             style={'margin-right': '2em', 'verticalAlign': "middle"}),
                    dcc.Dropdown(
                        id='comparision-metric-dropdown',
                        options=[
                            {'label': 'Log2 Fold Change', 'value': 'fold'},
                            {'label': 'Percentile Rank', 'value': 'perc'}
                        ],
                        value='fold',
                        style={'width': '140px', 'verticalAlign': "middle",
                               'border': 'solid 1px #545454', 'color': 'black'}
                    )
                ], style={'display': 'flex', 'marginTop': '5px', 'justify-content': 'center',
                          'align-items': 'center'}),
                html.Hr(),
                html.H3(children='Select Data', style={'text-align': 'center'}),
                html.Div(id='uploaded-data', children=[
                    html.Div(id='up-control-block', children=[
                        html.Div(children='Select Control'),
                        dcc.Dropdown(
                            id="control-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in testing_csvs],
                            value=0,
                            style={'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        )],
                        style={'marginRight': '10px', 'margin-top': '10px', 'width': '80%', 'margin-left': '20px'}),
                    html.Div(id='up-test-block', children=[
                        html.Div(children='Select Test'),
                        dcc.Dropdown(
                            id="test-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in testing_csvs],
                            value=0,
                            style={'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        )],
                        style={'marginRight': '10px', 'margin-top': '10px', 'width': '80%', 'margin-left': '20px'}),
                    ]),
                html.Br(),
                html.Br(),
                html.Button(
                    "Run Selection",
                    id="run-button",
                    style={'display': 'block', 'text-align': 'center', 'padding': '10px', 'margin': 'auto'}
                ),
                html.Br(),
                html.Div(id='gff-up-control-block', children=[
                    html.Div(children='Select Gff file'),
                    dcc.Dropdown(
                        id="gff-dropdown",
                        options=[{'label': i.name, 'value': i.name} for i in test_gff],
                        value=0,
                        style={'verticalAlign': "middle",
                               'border': 'solid 1px #545454', 'color': 'black'}
                    ),
                ], style={'marginRight': '10px', 'margin-top': '10px', 'width': '80%', 'margin-left': '20px'}),
                html.Hr(),
                html.H3(children='Upload Data', style={'text-align': 'center'}),
                html.Div(
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop Files',
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '1px',
                        },
                        # Allow multiple files to be uploaded
                        multiple=True,
                    ),
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
                ),
                html.Br(),
                html.Div(id='output-data-upload',
                         style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
                ]),


# Third tab on control panel
def control_options_tab():
    return html.Div(children=[
                html.H3("Datatable options"),
                dcc.Checklist(id='datatable_check',
                    options=[
                        {'label': 'Highlight', 'value': 'hl'},
                        {'label': 'Show Filter', 'value': 'filter'},
                        {'label': 'Simple Table (NRM NIM only)', 'value': 'simple'},
                    ],
                    value=['hl', 'filter', 'simple'],
                    labelStyle={'display': 'flex', 'marginTop': '5px', 'marginLeft': '10px'},
                ),
                html.Div(children=[
                    html.Div('Rows per page:'),
                    dcc.Input(
                        id='page_num_in',
                        type='number',
                        value=20,
                        style={'margin-left': '10px', 'width': '40px'}
                    )],
                    style={'display': 'flex', 'margin': '10px'}),
                html.Hr(),
                html.H3("Histogram options"),
                html.Div(children=[
                    html.Div('Style', style={'margin': '2px', 'margin-left': '5px', 'margin-right': '20px',
                                             'verticalAlign': "middle"}),
                    dcc.Dropdown(
                        id='hist-type-dropdown',
                        options=[
                            {'label': 'Type 1', 'value': 'type1'},
                            {'label': 'Type 2', 'value': 'type2'},
                        ],
                        value='type1',
                        style={'width': '140px', 'verticalAlign': "middle",
                               'border': 'solid 1px #545454', 'color': 'black'}
                    )
                ], style={'display': 'flex', 'margin': '10px', 'align-items': 'center'}),
                html.Div(children=[
                    html.Div('Bin Size :', style={'margin': '2px', 'margin-left': '5px', 'margin-right': '20px',
                                                  'verticalAlign': "middle"}),
                    dcc.Input(
                        id='hist-bin-size',
                        type='number',
                        value=1,
                        style={'width': '45px', 'verticalAlign': "middle",
                               'border': 'solid 1px #545454', 'color': 'black'}
                    ),
                ], style={'display': 'flex', 'margin': '10px'}),
                html.Hr(),
                html.H3("Venn options"),
                html.Div(children=[
                    html.Div(id='venn-thresh-desc-c', style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.Slider(id='venn-slider-c', value=0, min=0, max=50, step=1),
                    html.Div(id='venn-inserts-desc-c', style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.RangeSlider(
                        id='venn-inserts-slider-c',
                        min=0,
                        max=100,
                        step=1,
                        value=[0, 100]
                    ),
                ]),
                html.Hr(),
                html.H3("Genome Scatter Options"),
                dcc.Checklist(
                    id='scatter-checkbox',
                    options=[
                        {'label': 'Log scale', 'value': 'log'},
                    ],
                    value=['log'],
                    labelStyle={'display': 'flex', 'marginTop': '5px', 'marginLeft': '10px'}
                    ),
                html.Hr(),
                html.H3("Circos Options"),
                dcc.Checklist(id='circos-checkbox',
                              options=[
                                  {'label': 'Hide values where both scores = 0', 'value': 'hide_zero'},
                              ],
                              value=['hide_zero'],
                              labelStyle={'display': 'flex', 'marginTop': '5px', 'marginLeft': '10px'},
                              ),


    ], style={'marginLeft': '5px'})


# empty analysis tab
def empty_tab():
    return html.Div('Select data for import ...', style={'height': '100%', 'backgroundColor': 'white'})


# First tab in analysis panel, display datatable
def analysis_datatable_tab():
    return html.Div(children=[
        html.Div(id='table_preview')
        ], style={'backgroundColor': 'white'})


# Second analysis tab, display histogram
def analysis_hist_tab():
    return html.Div(children=[
        html.Div(id='histogram'),
        ], style={'backgroundColor': 'white'})


# Third analysis tab, display venn diagram
def analysis_venn_tab():
    return html.Div(children=[
        html.Div(id='venn-diagram'),
        dcc.Markdown("""
        
        """)
        ], style={'backgroundColor': 'white'})


# Fourth analysis tab, display genome scatter
def analysis_gff_scatter_tab():
    return html.Div(children=[
        html.Div(id='genome-scatter'),
    ], style={'backgroundColor': 'white'})


# Fifth analysis tab, display circos plot
def analysis_circos_tab():
    return html.Div(children=[
        html.Div(id='circos-plot-container'),
        html.Div(id='circos-slider-container', children=[
            dcc.RangeSlider(
                id='circos-gen-slider',
                min=0,
                max=1,
                step=0.001,
                value=[0, 1],
            )], style={'display': 'none'}),
    ], style={'backgroundColor': '#333652'})


# Main App
app.layout = html.Div(id='main-app', children=[
                dcc.Store(id='memory'),
                create_header(app_title),
                html.Div(id='main-section', children=[
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
                                label='Data',
                                value='tab2',
                                children=control_data_tab(),
                                style={'color': '#000000'}
                            ),
                            dcc.Tab(
                                label='Options',
                                value='tab3',
                                children=control_options_tab(),
                                style={'color': '#000000'}
                            ),
                        ]),
                    ], style={'color': 'white',
                              'width': '25%',
                              'height': tab_height,
                              'margin-right': '35px',
                              'background-color': '#333652',
                              'font-size': '10pt',
                              'overflow-y': 'auto'}
                    ),
                    # Visualisation Tabs
                    html.Div(id='analysis-tabs', children=[
                        dcc.Tabs(id='a_tabs', value='tab1', children=[
                            dcc.Tab(
                                label='DataTable',
                                value='tab1',
                                children=analysis_datatable_tab()
                            ),
                            dcc.Tab(
                                label='Histogram',
                                value='tab2',
                                children=analysis_hist_tab()
                            ),
                            dcc.Tab(
                                label='Venn Diagram',
                                value='tab3',
                                children=analysis_venn_tab()
                            ),
                            dcc.Tab(
                                label='Genome Scatter',
                                value='tab4',
                                children=analysis_gff_scatter_tab()
                            ),
                            dcc.Tab(
                                label='Circos',
                                value='tab5',
                                children=analysis_circos_tab(),
                            ),
                            dcc.Tab(
                                label='Analysis tab6',
                                value='tab6',
                                children=empty_tab()
                            ),
                        ]),
                    ], style={'height': tab_height,
                              'width': '75%',
                              'backgroundColor': 'white'}
                    ),
                ], style={'display': 'flex', 'margin': '35px'})
            ])


# Callbacks - All callbacks must be declared after app.layout

@app.callback(Output('memory', 'data'),
              [Input('run-button', 'n_clicks'),
               Input('test-dropdown', 'value'),
               Input('control-dropdown', 'value'),
               Input('comparision-metric-dropdown', 'value')],
              [State('memory', 'data')])
def on_click(n_clicks, test_path, control_path, c_metric, data):
    """
    This Callback stores the input data in a dcc.Store component when the run-button is clicked.
    :param n_clicks: int number of times run button clicked
    :param test_path: path from test-dropdown
    :param control_path: path from control-dropdown
    :param c_metric: comparision choice from dropdown
    :param data: the dcc.Store current data
    :return:
    """
    # Prevent update if run-button unclicked or dropdowns not populated
    if (n_clicks is None) or (test_path in [0, None]) or (control_path in [0, None]):
        raise dash.exceptions.PreventUpdate

    # Give a default data dict with 0 clicks if there's no data currently in dcc.store.
    data = data or {'clicks': 0, 'pimms_df': None}
    # If number of clicks has changed, update.
    if n_clicks > data['clicks']:
        # get index position of test_path within the list of available data.
        test_csv_idx = [i.name for i in testing_csvs].index(test_path)
        control_csv_idx = [i.name for i in testing_csvs].index(control_path)
        # extract full path from available data list
        test_path = testing_csvs[test_csv_idx]
        control_path = testing_csvs[control_csv_idx]
        # Create pimms dataframe, loading and merging the input data
        pimms_df = PIMMSDataFrame(control_path, test_path)
        # Create extra comparision column using chosen metric
        if c_metric == 'fold':
            pimms_df.calc_NIM_comparision_metric(fold_change_comparision, 'c_metric')
        elif c_metric == 'perc':
            pimms_df.calc_NIM_comparision_metric(percentile_rank_comparision, 'c_metric')
        # store in data dict. Serialising pimms_df object before storing.
        data['pimms_df'] = pimms_df.to_json()
        data['clicks'] = n_clicks

    return data


@app.callback(
    Output('main_table', 'style_data_conditional'),
    [Input('main_table', 'selected_columns'),
     Input('datatable_check', 'value')],
    [State('memory', 'data')])
def update_styles(selected_columns, checked_options, data):
    """
    This Callback adds highlighting to datatable.
    1. Highlights the rows where one NIM score is 0 and other is >0.
    2. Highlights any selected columns
    :param selected_columns: list of columns selected in dataframe
    :param checked_options: list of check values from datatable checkbox
    :param data: current data stored in dcc.Store component
    :return:
    """
    # Load data from dcc.Store.
    pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()
    # Add styling dicts to style_data_conditional. See datatable docs
    style_data_conditional = []
    if 'hl' in checked_options:
        style_data_conditional.append({
                    'if': {'filter_query': f'({{{NIM_control_col}}} = 0 and {{{NIM_test_col}}} > 0) or \
                                             ({{{NIM_control_col}}} > 0 and {{{NIM_test_col}}} = 0)'},
                    'backgroundColor': '#EDFFEC'})
    if selected_columns != None:
        for col in selected_columns:
            style_data_conditional.append({
                    'if': {'column_id': col},
                    'background_color': '#D2F3FF'
                })
    return style_data_conditional


@app.callback(
    Output('main_table', 'filter_action'),
    [Input('datatable_check', 'value')])
def toggle_filter(checked_options):
    """Callback to show/hide the filter row in datatable when checkbox is clicked."""
    if 'filter' in checked_options:
        return 'native'
    else:
        return 'none'


@app.callback(
    Output('main_table', 'page_size'),
    [Input('page_num_in', 'value')])
def table_page_size(number_pages):
    """ Callback to adjust page size of datatable"""
    if number_pages > 0:
        return number_pages
    else:
        return 1


@app.callback(
    Output('table_preview', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('datatable_check', 'value')],
    [State('memory', 'data')])
def create_table(ts, checked_options, data):
    """
    Callback to create datatable when new data placed in dcc.Store. Creates simple table if option is checked.
    :param ts: timestamp from dcc.store, Used to trigger callback when dcc.store updated.
    :param checked_options: list of options checked in datatable checkbox
    :param data: current data stored in dcc.Store component
    :return:
    """
    if ts is not None:
        pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
        if 'simple' in checked_options:
            df = pimms_df.get_df_simple()
        else:
            df = pimms_df.data
        df = df.round(3)
        return create_datatable(df)
    return empty_tab()


@app.callback(
    Output('venn-thresh-desc-c', 'children'),
    [Input('venn-slider-c', 'value')])
def update_venn_thresh_desc_control(slider_val):
    """ Callback to update text description of venn NIM score slider"""
    return f'NIM scores <= {slider_val}'


@app.callback(
    Output('venn-inserts-desc-c', 'children'),
    [Input('venn-inserts-slider-c', 'value')])
def update_venn_thresh_desc_control(slider_val):
    """ Callback to update text description of venn inserts slider"""
    return f'Inserts are within percentiles {slider_val[0]} to {slider_val[1]} '


@app.callback(
    Output('venn-diagram', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('venn-slider-c', 'value'),
     Input('venn-inserts-slider-c', 'value')],
    [State('memory', 'data')])
def update_venn(ts, thresh_c, slider_c, data):
    """
    Callback to create/update venn diagram when new data in dcc.store or venn options are changed.
    :param ts: timestamp from dcc.store, Used to trigger callback when dcc.store updated.
    :param thresh_c: NIM score threshold from slider
    :param slider_c: Inserts range from slider
    :param data: current data stored in dcc.Store component
    :return:
    """
    if ts is not None:
        # Load data from store
        pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
        NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()
        perc_test_cols, perc_control_cols = pimms_df.test_control_cols_containing('insert_posn_as_percentile')
        # Create an unique identifier column
        pimms_df['unique'] = np.arange(len(pimms_df)).astype(str)

        # Apply filters to get sets
        control_set = pimms_df[((pimms_df[NIM_control_col] <= thresh_c) &
                                (pimms_df[perc_control_cols[0]] >= slider_c[0]) &
                                (pimms_df[perc_control_cols[1]] <= slider_c[1]))]['unique']
        test_set = pimms_df[((pimms_df[NIM_test_col] <= thresh_c) &
                             (pimms_df[perc_test_cols[0]] >= slider_c[0]) &
                             (pimms_df[perc_test_cols[1]] <= slider_c[1]))]['unique']
        # Create Venn
        venn_img = create_venn(control_set, test_set)
        # Create Venn Label
        label = dcc.Markdown(f"""
        * **Set A**: 
        {NIM_control_col}
        
        * **Set B**:
        {NIM_test_col}

        """)
        return html.Div(children=[
            html.Div(html.Img(src=venn_img,
                              style={'display': 'flex', 'justify-content': 'center',
                                     'align-items': 'center', 'height': '100%'}
                              )
                     ),
            label,
            ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})
    return empty_tab()


@app.callback(
    Output('histogram', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('hist-type-dropdown', 'value'),
     Input('hist-bin-size', 'value')],
    [State('memory', 'data')])
def create_hist(ts, hist_type, bin_size, data):
    """
    Callback to create histogram.
    :param ts: timestamp from dcc.store, Used to trigger callback when dcc.store updated.
    :param hist_type: str from dropdown, either type1 or type2
    :param bin_size: size of histogram bins
    :param data: current data stored in dcc.Store component
    :return:
    """
    if ts is not None:
        # Load data from store
        pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
        NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

        # Create relevant histogram and return in graph component
        if hist_type == 'type1':
            hist_fig = create_histogram(pimms_df[NIM_control_col], pimms_df[NIM_test_col], bin_size=bin_size)
            return dcc.Graph(id='hist-fig', figure=hist_fig)
        elif hist_type == 'type2':
            hist_fig = create_histogram_type2(pimms_df[NIM_control_col], pimms_df[NIM_test_col], bin_size=bin_size)
            return dcc.Graph(id='hist-fig-t2', figure=hist_fig)
    return empty_tab()


@app.callback(
    Output('hist-fig', 'figure'),
    [Input('hist-fig', 'relayoutData'),
     Input('hist-bin-size', 'value')],
    [State('memory', 'data')])
def display_hist_type1(relayoutData, bin_size, data):
    """
    Callback to update type1 hist according to updated ranges. Used to keep interactivity in the type1 hist where
    multiple subplots are used with the lower hist flipped vertically.
    :param relayoutData: dict containing relayout data from histogram. see plotly docs.
    :param bin_size: histogram bin size
    :param data: current data stored in dcc.Store component
    :return:
    """
    if relayoutData:
        if 'autosize' in relayoutData:
            raise dash.exceptions.PreventUpdate
        # Load data from store
        pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
        NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

        # Create new y range
        if 'yaxis.range[1]' in relayoutData:
            r_y = [0, relayoutData['yaxis.range[1]']]
        elif 'yaxis2.range[1]' in relayoutData:
            r_y = [0, relayoutData['yaxis2.range[0]']]
        else:
            r_y = None

        # Create new x range
        if 'xaxis.range[0]' in relayoutData:
            r_x = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        else:
            r_x = None
        # Return new type1 histogram with updated ranges
        return create_histogram(pimms_df[NIM_control_col], pimms_df[NIM_test_col], range_x=r_x, range_y=r_y, bin_size=bin_size)
    raise dash.exceptions.PreventUpdate


@app.callback(
    Output('genome-scatter', 'children'),
    [Input('run-button', 'n_clicks'),
     Input('gff-dropdown', 'value'),
     Input('scatter-checkbox', 'value')])
def update_genome_scatter(n_clicks, gff_filename, checkbox):
    """
    Callback to create/update genome scatter plot.
    TODO load gff file into dcc.Store, currently reads gff data within this callback
    :param n_clicks: number of clicks of run button
    :param gff_filename:
    :param checkbox: scatter options checkbox
    :return:
    """
    if (n_clicks is not None) and (gff_filename not in [0, None]):
        # Get full file path
        gff_idx = [i.name for i in test_gff].index(gff_filename)
        # Load into gffdataframe object
        gff_df = GffDataFrame(test_gff[gff_idx])
        # Create figure
        fig = create_genome_scatter(gff_df)
        # Change to log axis if checked
        if 'log' in checkbox:
            fig.update_layout(yaxis_type="log")
        return dcc.Graph(id='gff-scatter-fig', figure=fig)
    else:
        return empty_tab()


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def upload_new_file(list_of_contents, list_of_names, list_of_dates):
    """ Callback to parse and save uploaded data"""
    if list_of_contents is not None:
        children = [parse_upload(c, n) for c, n in zip(list_of_contents, list_of_names)]
        return children


@app.callback([Output('test-dropdown', 'options'),
               Output('control-dropdown', 'options')],
              [Input('output-data-upload', 'children')])
def update_upload_dropdowns(upload_message):
    """Callback to update the select data dropdowns when new data uploaded"""
    if not upload_message or not upload_message[0]:
        raise dash.exceptions.PreventUpdate
    if upload_message[0].startswith('Uploaded'):
        output_list = [{'label': i.name, 'value': i.name} for i in list(DATA_PATH.glob('*.csv'))]
        return output_list, output_list
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(Output('circos-plot-container', 'children'),
              [Input('memory', 'modified_timestamp'),
               Input('circos-gen-slider', 'value'),
               Input('circos-checkbox', 'value')],
              [State('memory', 'data')])
def create_circos(ts, g_len, checkbox, data):
    """
    Callback to create/update circos plot
    :param ts: timestamp from dcc.store, Used to trigger callback when dcc.store updated.
    :param g_len: int, length of genome to display from slider. 0 to 1
    :param checkbox: list of circos checked options
    :param data: current data stored in dcc.Store component
    :return:
    """
    hide_zeros = 'hide_zero' in checkbox
    if ts is not None:
        # Load data from dcc.Store
        pimms_df = PIMMSDataFrame.from_json(data['pimms_df'])
        NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

        # Calc genome range and limit using slider values
        genome_range = pimms_df['end'].max() - pimms_df['start'].min()
        start = int(g_len[0] * genome_range)
        end = int(g_len[1] * genome_range)

        # Create dataframe for each circos ring, rename cols to relevant names for circos to pick up
        inner_ring = pimms_df[pimms_df.info_columns + [NIM_control_col]]
        inner_ring = inner_ring.rename(columns={"seq_id": "block_id", NIM_control_col: "value"})
        outer_ring = pimms_df[pimms_df.info_columns + [NIM_test_col]]
        outer_ring = outer_ring.rename(columns={"seq_id": "block_id", NIM_test_col: "value"})
        hist_ring = pimms_df[pimms_df.info_columns + ['c_metric']]
        hist_ring = hist_ring.rename(columns={"seq_id": "block_id", 'c_metric': "value"})

        # Create the circos plot
        circos = create_pimms_circos(inner_ring, outer_ring, hist_ring, start, end, hide_zeros=hide_zeros)
        # Return Tab children
        return html.Div(children=[
                    html.Div(children=[
                        circos,
                        html.Div(id='event-data-select', style={'color': 'white'})],
                        style={'display': 'flex', 'justify-content': 'left', 'align-items': 'center'}),
                    html.Div(f'Displaying Genome from positions {start} to {end}',
                             style={'color': 'white', 'margin-left': '20px'})
                    ])
    else:
        return empty_tab()


@app.callback(Output('circos-slider-container', 'style'),
              [Input('memory', 'modified_timestamp')])
def display_circos_slider(ts):
    """ Callback to hide circos slider when no data in dcc.Store"""
    if ts is not None:
        return {'display': 'block'}
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output('event-data-select', 'children'),
    [Input('main-circos', 'eventDatum')])
def event_data_select(event_datum):
    """ Callback to update text next to circos plot with circos hover data."""
    if event_datum is not None:
        contents = []
        for key in event_datum.keys():
            contents.append(html.Span(key.title(), style={'font-weight': 'bold'}))
            contents.append(' - {}'.format(event_datum[key]))
            contents.append(html.Br())
    else:
        contents = ['Hover over circos plot to', html.Br(), 'display locus information.']
    return contents


if __name__ == '__main__':
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )
