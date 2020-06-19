import pathlib
import io
import base64

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

import pandas as pd
import numpy as np


app_title = 'Pimms Dashboard'
tab_height = '600px'

# Define local paths
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Available data
test_csvs = list(DATA_PATH.glob('*.csv'))

#Expected columns
info_columns = ['seq_id', 'locus_tag', 'type', 'gene', 'start', 'end', 'feat_length', 'product']
simple_columns = info_columns + ['UK15_Blood_Output_NRM_score',
                                 'UK15_Blood_Output_NIM_score',
                                 'UK15_Media_Input_NRM_score',
                                 'UK15_Media_Input_NIM_score']
c_suffix = '_control'
t_suffix = '_test'

# Initialise App
app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True
server = app.server

def load_and_merge(control_data_path, test_data_path):
    test_csv_idx = [i.name for i in test_csvs].index(test_data_path)
    control_csv_idx = [i.name for i in test_csvs].index(control_data_path)
    df_c = pd.read_csv(test_csvs[test_csv_idx])
    df_t = pd.read_csv(test_csvs[control_csv_idx])
    df_m = merge_control_test(df_c, df_t, info_columns, c_suffix, t_suffix)
    return df_m.to_json(date_format='iso', orient='split')


def merge_control_test(control_df, test_df, on, control_suffix, test_suffix):
    assert (set(on).issubset(control_df.columns)), 'On columns are not present in control_df'
    assert (set(on).issubset(test_df.columns)), 'On columns are not present in test_df'
    ctrl_data_cols = set(control_df.columns) - set(on)
    test_data_cols = set(test_df.columns) - set(on)
    new_control_names = [(i, i + control_suffix) for i in list(ctrl_data_cols)]
    new_test_names = [(i, i + test_suffix) for i in list(test_data_cols)]
    control_df.rename(columns=dict(new_control_names), inplace=True)
    test_df.rename(columns=dict(new_test_names), inplace=True)
    df_m = pd.merge(test_df, control_df, how='inner', on=on)
    return df_m


def simplify_df_m(df_m):
    new_cols = []
    for col in set(df_m.columns)-set(info_columns):
        for simple_col in set(simple_columns)-set(info_columns):
            if col.startswith(simple_col):
                new_cols.append(col)
    return df_m[info_columns+new_cols]


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
                html.H3(children='Select Data', style={'text-align': 'center'}),
                html.Div(id='uploaded-data', children=[
                    html.Div(id='up-control-block', children=[
                        html.Div(children='Select Control'),
                        dcc.Dropdown(
                            id="control-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in test_csvs],
                            value=0,
                            style={'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        ),
                    ], style={'marginRight': '10px', 'margin-top':'10px', 'width':'80%'}),
                    html.Div(id='up-test-block', children=[
                        html.Div(children='Select Test'),
                        dcc.Dropdown(
                            id="test-dropdown",
                            options=[{'label': i.name, 'value': i.name} for i in test_csvs],
                            value=0,
                            style={'verticalAlign': "middle",
                                   'border': 'solid 1px #545454', 'color': 'black'}
                        ),
                    ], style={'marginRight': '10px', 'margin-top':'10px','width':'80%'}),
                    ], style={'margin-left':'20px'}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Button(
                    "Run Selection",
                    id="run-button",
                    style={'display': 'block', 'text-align': 'center', 'padding': '10px',
                           'margin':'auto'}
                ),
                html.Br(),
                html.Hr(),
                html.H3(children='Upload Data', style={'text-align': 'center'}),
                html.Div(
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop Files'
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '1px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center',}
                ),
                html.Div(id='output-data-upload'),
                ]),


#third tab on control panel
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
                        value=12,
                        style={'margin-left':'10px', 'width':'40px'}
                    )
                ],style={'display':'flex', 'margin': '10px'}),
                html.Hr(),
                html.H3("Histogram options"),
                html.Div(children=[
                    html.Div('Style', style={'margin-right': '2em', 'verticalAlign': "middle"}),
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
                ], style={'display': 'flex', 'marginTop': '5px', 'justify-content': 'center',
                          'align-items': 'center'}),
                html.Hr(),
                html.H3("Venn options"),
                html.Div(children=[
                    html.Div(id='venn-thresh-desc-c', style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.Slider(id='venn-slider-c', value=0, min=0, max=50, step=1),
                    html.Div(id='venn-thresh-desc-t', style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.Slider(id='venn-slider-t', value=0, min=0, max=50, step=1),
                    html.Div(id='venn-inserts-desc-c', style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.RangeSlider(
                        id='venn-inserts-slider-c',
                        min=0,
                        max=100,
                        step=1,
                        value=[0, 100]
                    ),
                    html.Div(id='venn-inserts-desc-t',style={'margin-left': '10px', 'margin-right': '10px'}),
                    dcc.RangeSlider(
                        id='venn-inserts-slider-t',
                        min=0,
                        max=100,
                        step=1,
                        value=[0, 100]
                    ),
                ]),

    ],style={'marginLeft': '5px'})


# empty analysis tab
def empty_tab():
    return html.Div('Select data for import ...', style={'height': '100%', 'backgroundColor': 'white'})


# First tab in analysis panel, display datatable
def analysis_datatable_tab():
    return html.Div(children=[
        html.Div(id='table_preview')
        ], style={'backgroundColor': 'white'})


#Second analysis tab, display histogram
def analysis_hist_tab():
    return html.Div(children=[
        html.Div(id='histogram'),
        ], style={'backgroundColor': 'white'})


#Third analysis tab, display venn diagram
def analysis_venn_tab():
    return html.Div(children=[
        html.Div(id='venn-diagram'),
        dcc.Markdown("""
        
        """)
        ], style={'backgroundColor': 'white'})


def create_histogram(series_control, series_test, range_x=None, range_y=None):
    # Build histogram using numpy
    np_hist_t = np.histogram(series_test.values, bins='auto')
    np_hist_c = np.histogram(series_control.values, bins=np_hist_t[1])
    np_hist_info = {
        'test': {
            'nbins': len(np_hist_t[1]) - 1,
            'start': np_hist_t[1][0],
            'end': np_hist_t[1][-1],
            'max': np_hist_t[0].max(),
            'min': np_hist_t[0].min(),
            'size': np_hist_t[1][1]
        },
        'control': {
            'nbins': len(np_hist_c[1]) - 1,
            'start': np_hist_c[1][0],
            'end': np_hist_c[1][-1],
            'max': np_hist_c[0].max(),
            'min': np_hist_c[0].min(),
            'size': np_hist_c[1][1]
        },
    }
    range_max = np.max([np_hist_info['test']['max'], np_hist_info['control']['max']])
    range_min = np.min([np_hist_info['test']['min'], np_hist_info['control']['min']])

    #create plotly graph objects
    hist_t = go.Histogram(x=series_test,
                          ybins={'end': np_hist_info['test']['end'],
                                 'size': np_hist_info['test']['size'],
                                 'start': np_hist_info['test']['start']},
                          name='Test',
                          opacity=0.5,
                          marker={'line':{'width':1}}
                          )
    hist_c = go.Histogram(x=series_control,
                          ybins={'end': np_hist_info['control']['end'],
                                 'size': np_hist_info['control']['size'],
                                 'start': np_hist_info['control']['start']},
                          name='Control',
                          opacity=0.5,
                          marker={'line': {'width': 1}}
                          )
    #create figure
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0,
                        column_titles=['Sampled Results'],  # title of plot
                        x_title='NIM',  # xaxis label
                        y_title='Count',
                        )

    fig.add_trace(hist_c, row=1, col=1)
    fig.add_trace(hist_t, row=2, col=1)

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)

    #Manage range
    if range_y:
        fig.update_layout(go.Layout(yaxis=dict(range=range_y)))
        fig.update_layout(go.Layout(yaxis2=dict(range=range_y[::-1])))
    else:
        fig.update_layout(go.Layout(yaxis=dict(range=[range_min, range_max])))
        fig.update_layout(go.Layout(yaxis2=dict(range=[range_max, range_min])))

    if range_x:
        fig.update_layout(go.Layout(xaxis=dict(range=range_x)))
        fig.update_layout(go.Layout(xaxis2=dict(range=range_x)))

    return fig


def create_histogram_t2(series_control, series_test,):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=series_control,
                               name='Control',
                               opacity=0.5,
                               marker={'line': {'width': 1}}
                               ))
    fig.add_trace(go.Histogram(x=series_test,
                               name='Test',
                               opacity=0.5,
                               marker={'line': {'width': 1}}
                               ))

    fig.update_layout(
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0,  # gap between bars of the same location coordinates
        xaxis_title="NIM",
        yaxis_title="Count",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)

    return fig


def create_venn(set_A, set_B):
    # get venn sets
    aB = len(set(set_B) - set(set_A))
    Ab = len(set(set_A) - set(set_B))
    AB = len(set(set_A) & set(set_B))

    # Create venn using matplotlib, encode to b64, pass to html.img
    plt.figure(linewidth=10, edgecolor="black", facecolor="black")
    mpl_fig = venn2(subsets=(Ab, aB, AB))
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png')
    pic_IObytes.seek(0)
    encoded_image = base64.b64encode(pic_IObytes.read())
    img = 'data:image/png;base64,{}'.format(encoded_image.decode())
    # plotly_fig = mpl_to_plotly(mpl_fig) # Not working for venn
    plt.close()
    return html.Img(src=img, style={'display':'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '100%'})


def create_datatable(df_m):
    return dash_table.DataTable(id='main_table',
                columns=[{"name": ["Information", i.replace("_", " ")], "id": i, "deletable": True} for i in df_m.columns if i in info_columns] + \
                        [{"name": ['Control', i.replace("_", " ")], "id": i, "selectable": True} for i in df_m.columns if i.endswith(c_suffix)] + \
                        [{"name": ['Test', i.replace("_", " ")], "id": i, "selectable": True} for i in df_m.columns if i.endswith(t_suffix)],
                data=df_m.to_dict('records'),
                merge_duplicate_headers=True,
                sort_mode="multi",
                column_selectable="multi",
                tooltip_data=[{'product':{'type': 'text','value': f'{r}'} } for r in df_m['product'].values],
                style_table={'overflowX': 'scroll', 'overflowY': 'auto', 'color':'black'},
                style_as_list_view=True,
                style_header={'backgroundColor': 'white', 'fontWeight': 'bold'},

                style_cell={
                    'minWidth': '50px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal','padding': '5px','textAlign': 'left'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'product'},
                        'overflow': 'hidden',
                        'text-overflow': 'ellipsis',
                        'white-space': 'nowrap'}],
                style_data={
                    'lineHeight': '15px'
                },
                page_size=12,
                sort_action="native",
            )


# Main App
app.layout = html.Div(id='main-app', children=[
                dcc.Store(id='memory'),
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
                ], style={'display': 'inline-block',
                          'color': 'white',
                          'width': '350px',
                          'height': tab_height,
                          'margin': '35px',
                          'margin-right': '0px',
                          'background-color': '#333652',
                          'font-size': '10pt',
                          'float': 'left'}
                ),
                # Visualisation Tabs
                html.Div(id='analysis-tabs', children=[
                    dcc.Tabs(id='a_tabs', value='tab1',children=[
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
                            label='Analysis tab4',
                            value='tab4',
                            children=empty_tab()
                        ),
                        dcc.Tab(
                            label='Analysis tab5',
                            value='tab5',
                            children=empty_tab()
                        ),
                        dcc.Tab(
                            label='Analysis tab6',
                            value='tab6',
                            children=empty_tab()
                        ),
                    ]),
                ], style={'display': 'inline-block',
                          'margin': '35px',
                          'height': tab_height,
                          'width': '65%',
                          'backgroundColor':'white'}
                ),
            ])


#Callbacks

@app.callback(Output('memory', 'data'),
              [Input('run-button', 'n_clicks'),
               Input('test-dropdown', 'value'),
               Input('control-dropdown', 'value')],
              [State('memory', 'data')])
def on_click(n_clicks, test_path, control_path, data):
    if (n_clicks is None) or (test_path in [0, None]) or (control_path in [0, None]):
        raise dash.exceptions.PreventUpdate

    # Give a default data dict with 0 clicks if there's no data.
    data = data or {'clicks': 0, 'dataframe': None}
    if n_clicks > data['clicks']:
        data['dataframe'] = load_and_merge(control_path, test_path)
        data['clicks'] = n_clicks

    return data

@app.callback(
    Output('main_table', 'style_data_conditional'),
    [Input('main_table', 'selected_columns'),
     Input('datatable_check', 'value')]
)
def update_styles(selected_columns, checked_options):
    style_data_conditional = []
    if 'hl' in checked_options:
        style_data_conditional.append({
                    'if': {'filter_query': f'({{UK15_Media_Input_NIM_score{c_suffix}}} = 0 and {{UK15_Blood_Output_NIM_score{t_suffix}}} > 0) or \
                     ({{UK15_Media_Input_NIM_score{c_suffix}}} > 0 and {{UK15_Blood_Output_NIM_score{t_suffix}}} = 0)'},
                    'backgroundColor': '#EDFFEC'})
    if selected_columns != None:
        for col in selected_columns:
            style_data_conditional.append({
                    'if': { 'column_id': col },
                    'background_color': '#D2F3FF'
                })
    return style_data_conditional


@app.callback(
    Output('main_table', 'filter_action'),
    [Input('datatable_check', 'value')],
)
def toggle_filter(checked_options):
    if 'filter' in checked_options:
        return 'native'
    else:
        return 'none'

@app.callback(
    Output('main_table', 'page_size'),
    [Input('page_num_in', 'value')],
)
def table_page_size(number_pages):
    if number_pages > 0:
        return number_pages
    else:
        return 1

@app.callback(
    Output('table_preview', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('datatable_check', 'value')],
    [State('memory', 'data')]
)
def create_table(ts, checked_options, data):
    if ts is not None:
        df_m = pd.read_json(data['dataframe'], orient='split')
        if 'simple' in checked_options:
            df_m = simplify_df_m(df_m)
        return create_datatable(df_m)
    return empty_tab()

@app.callback(
    Output('venn-thresh-desc-c', 'children'),
    [Input('venn-slider-c', 'value')]
)
def update_venn_thresh_desc_control(slider_val):
    return f'SET A: Control NIM scores <= {slider_val}'

@app.callback(
    Output('venn-thresh-desc-t', 'children'),
    [Input('venn-slider-t', 'value')]
)
def update_venn_thresh_desc_control(slider_val):
    return f'SET B: Test NIM scores <= {slider_val}'

@app.callback(
    Output('venn-inserts-desc-c', 'children'),
    [Input('venn-inserts-slider-c', 'value')]
)
def update_venn_thresh_desc_control(slider_val):
    return f'SET A: Control inserts are within percentiles {slider_val[0]} to {slider_val[1]} '

@app.callback(
    Output('venn-inserts-desc-t', 'children'),
    [Input('venn-inserts-slider-t', 'value')]
)
def update_venn_thresh_desc_control(slider_val):
    return f'SET B: Test inserts are within percentiles {slider_val[0]} to {slider_val[1]}'

@app.callback(
    Output('venn-diagram', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('venn-slider-c', 'value'),
     Input('venn-slider-t', 'value'),
     Input('venn-inserts-slider-c', 'value'),
     Input('venn-inserts-slider-t', 'value')],
    [State('memory', 'data')]
)
def update_venn(ts, thresh_c, thresh_t, slider_c, slider_t, data):
    if ts is not None:
        df_m = pd.read_json(data['dataframe'], orient='split')
        control_col = [col for col in df_m.columns if f'NIM_score{c_suffix}' in col][0]
        test_col = [col for col in df_m.columns if f'NIM_score{t_suffix}' in col][0]
        control_perc_cols = [col for col in df_m.columns if f'insert_posn_as_percentile{t_suffix}' in col]
        test_perc_cols = [col for col in df_m.columns if f'insert_posn_as_percentile{t_suffix}' in col]

        df_m['unique'] = np.arange(len(df_m)).astype(str)

        #apply filters to get sets
        control_set = df_m[((df_m[control_col] <= thresh_c) &
                            (df_m[control_perc_cols[0]] >= slider_c[0]) &
                            (df_m[control_perc_cols[1]] <= slider_c[1]))]['unique']
        test_set = df_m[((df_m[test_col] <= thresh_t) &
                            (df_m[test_perc_cols[0]] >= slider_t[0]) &
                            (df_m[test_perc_cols[1]] <= slider_t[1]))]['unique']

        venn_img = create_venn(control_set, test_set)
        label = dcc.Markdown(f"""
        * **Set A**: 
        {control_col}
        
        * **Set B**:
        {test_col}

        """)
        return html.Div(children=[
            html.Div(venn_img),
            label,
        ],style={'display': 'flex','justify-content': 'center',
                      'align-items': 'center'})
    return empty_tab()

@app.callback(
    Output('histogram', 'children'),
    [Input('memory', 'modified_timestamp'),
     Input('hist-type-dropdown', 'value')],
    [State('memory', 'data')]
)
def create_hist(ts, hist_type, data):
    if ts is not None:
        df_m = pd.read_json(data['dataframe'], orient='split')
        control_col = [col for col in df_m.columns if f'NIM_score{c_suffix}' in col][0]
        test_col = [col for col in df_m.columns if f'NIM_score{t_suffix}' in col][0]
        if hist_type == 'type1':
            hist_fig = create_histogram(df_m[control_col], df_m[test_col])
            return dcc.Graph(id='hist-fig', figure=hist_fig)
        elif hist_type == 'type2':
            hist_fig = create_histogram_t2(df_m[control_col], df_m[test_col])
            return dcc.Graph(id='hist-fig-t2', figure=hist_fig)
    return empty_tab()

@app.callback(
    Output('hist-fig', 'figure'),
    [Input('hist-fig', 'relayoutData')],
    [State('memory', 'data')]
)
def display_hist_type1(relayoutData, data):
    if relayoutData:
        if 'autosize' in relayoutData:
            raise dash.exceptions.PreventUpdate
        df_m = pd.read_json(data['dataframe'], orient='split')
        control_col = [col for col in df_m.columns if f'NIM_score{c_suffix}' in col][0]
        test_col = [col for col in df_m.columns if f'NIM_score{t_suffix}' in col][0]

        if 'yaxis.range[1]' in relayoutData:
            r_y = [0, relayoutData['yaxis.range[1]']]
        elif 'yaxis2.range[1]' in relayoutData:
            r_y = [0, relayoutData['yaxis2.range[0]']]
        else:
            r_y = None

        if 'xaxis.range[0]' in relayoutData:
            r_x = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        else:
            r_x = None
        return create_histogram(df_m[control_col], df_m[test_col], range_x=r_x, range_y=r_y)
    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )