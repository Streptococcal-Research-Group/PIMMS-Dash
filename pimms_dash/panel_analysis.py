import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
from dash.dash import no_update
from dash.exceptions import PreventUpdate
from dash_table.Format import Format, Scheme
import dash_bio as dashbio

import numpy as np
from math import log

from app import app
from utils import PIMMSDataFrame, GffDataFrame, load_data
from figures import main_datatable, histogram, histogram_type2, venn_diagram, genome_comparison_scatter
from circos import pimms_circos

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div("No Input Data Loaded", id="tab1-datatable-div")
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div("No Input Data Loaded", id="tab2-hist-div")
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div("No Input Data Loaded", id="tab3-venn-div"),
                        width=6,
                    ),
                    dbc.Col(
                        html.Div(id="tab3-venn-label"),
                        width={"size": 4, "offset": 2},
                    ),
                ],
                justify="between", align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show Venn Table",
                            id="venn-collapse-button",
                            color="info",
                        ),
                    ),
                    dbc.Col(

                    ),
                ],
                justify="center"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Collapse(
                            [
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Set Ab Only", "value": "Ab"},
                                        {"label": "Set aB Only", "value": "aB"},
                                        {"label": "Intersection Only", "value": "AB"},
                                        {"label": "All", "value": "all"},
                                    ],
                                    value="all",
                                    id="venn-table-radioitems",
                                    switch=True,
                                    inline=True,
                                ),
                                html.Div("No Input Data Loaded", id="tab3-venn-datatable-div"),
                            ],
                            id="venn-datatable-collapse"
                        )
                    )
                ],
                className="mt-3"
            ),
        ],
    ),
    className="mt-3",
)

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("No Coordinate-Gffs Loaded", id="tab4-scatter-div"))
                ]
            ),
        ]
    ),
    className="mt-3",
)

tab5_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div("No Input Data Loaded", id="tab5-circos-div"),
                        width=6,
                    ),
                    dbc.Col(
                        html.Div(id='event-data-select'),
                        width={"size":4,"offset":2},
                    )
                ]
            ),
            dbc.Collapse(
                dcc.RangeSlider(
                    id='circos-gen-slider',
                    min=0,
                    max=1,
                    step=0.001,
                    value=[0, 1],
                ),

                id="collapse-circos-slider",
                is_open=False
            ),
        ],
    ),
    className="mt-3",
)

tab6_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("Select a gene in the DataTable tab", id="tab6-geneviewer-div"))
                ],
                justify="center"
            ),
        ]
    ),
    className="mt-3",
)

analysis_tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="DataTable"),
        dbc.Tab(tab2_content, label="Histogram"),
        dbc.Tab(tab3_content, label="Venn Diagram"),
        dbc.Tab(tab4_content, label="Genome Scatter"),
        dbc.Tab(tab5_content, label="Circos"),
        dbc.Tab(tab6_content, label="GeneViewer"),
    ]
)


@app.callback(
    Output("tab1-datatable-div", "children"),
    [Input("run-status", "data"),
     State("session-id", "children")],
    prevent_initial_call=True
)
def create_table(run_status, session_id):
    """
    Callback to create datatable when new data placed in dcc.Store. Creates simple table if option is checked.
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """
    if run_status['pimms']:
        data = load_data("pimms_df", session_id)
        pimms_df = PIMMSDataFrame.from_json(data)
        return main_datatable(pimms_df.get_data(), id="main-datatable", row_selectable='single')
    else:
        return "No Input Data Found"

@app.callback(
    [Output("main-datatable", "style_data_conditional"),
     Output("main-datatable", "filter_action"),
     Output("main-datatable", "page_size"),
     Output("main-datatable", "columns")],
    [Input("main-datatable", "selected_rows"),
     Input("comparison-metric-dropdown", "value"),
     Input("datatable-checklist", "value"),
     Input("datatable-numrows", 'value'),
     State("run-status", "data"),
     State("session-id", "children")]
)
def style_table(selected_rows, c_metric, checked_options, num_rows, run_status, session_id):
    """
    This Callback adds highlighting to datatable.
    1. Highlights the rows where one NIM score is 0 and other is >0.
    2. Highlights any selected columns
    :param selected_columns: list of columns selected in dataframe
    :param c_metric: selected comparison metric
    :param checked_options: list of check values from datatable checkbox
    :param num_rows: number of rows in table
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """
    # Prevent Update if no data
    if not run_status['pimms']:
        raise PreventUpdate

    # read data from data store
    data = load_data("pimms_df", session_id)
    pimms_df = PIMMSDataFrame.from_json(data)
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

    # Add filter row
    if "filter" in checked_options:
        filter_action = "native"
    else:
        filter_action = "none"

    # Adjust rows per page
    if num_rows > 0:
        page_size = num_rows
    else:
        page_size = 1

    # Adjust columns if simple table
    if 'simple' in checked_options:
        cols = pimms_df.get_columns(simple=True, c_metric=c_metric)
        columns = [{"name": i.replace("_", " "), "id": i, "selectable": True,
                    "format": Format(precision=2, scheme=Scheme.fixed)} for i in cols]
    else:
        cols = pimms_df.get_columns(simple=False, c_metric=c_metric)
        columns = [{"name": i.replace("_", " "),
                      "id": i,
                      "selectable": True,
                      "format": Format(precision=2, scheme=Scheme.fixed)} for i in cols]

    # Add styling dicts to style_data_conditional. See datatable docs
    style_data_conditional = []
    if "hl" in checked_options:
        # Load data from dcc.Store.
        style_data_conditional.append({
                    "if": {"filter_query": f"({{{NIM_control_col}}} = 0 and {{{NIM_test_col}}} > 0) or \
                                             ({{{NIM_control_col}}} > 0 and {{{NIM_test_col}}} = 0)"},
                    "backgroundColor": "#EDFFEC"})
    if selected_rows != None:
        for row_i in selected_rows:
            locus_tag = pimms_df.get_data().at[row_i, "locus_tag"]
            style_data_conditional.append({
                    'if': {'filter_query': f'{{locus_tag}} eq "{locus_tag}"'},
                    "background_color": "#D2F3FF",
                    'fontWeight': 'bold',
                })
    return style_data_conditional, filter_action, page_size, columns


@app.callback(
    Output('tab2-hist-div', 'children'),
    [Input('run-status', 'data'),
     Input('hist-dropdown-type', 'value'),
     Input('hist-bin-size', 'value'),
     State('session-id', 'children')],
    prevent_initial_call=True
)
def create_hist(run_status, hist_type, bin_size, session_id):
    """
    Callback to create histogram.
    :param hist_type: str from dropdown, either type1 or type2
    :param bin_size: size of histogram bins
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """
    if not run_status["pimms"]:
        raise PreventUpdate

    data = load_data('pimms_df', session_id)

    # Load data from store
    pimms_df = PIMMSDataFrame.from_json(data)
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

    # Create relevant histogram and return in graph component
    if hist_type == 'type1':
        hist_fig = histogram(pimms_df.get_data()[NIM_control_col], pimms_df.get_data()[NIM_test_col],
                                    bin_size=bin_size)
        return dcc.Graph(id='hist-fig-t1', figure=hist_fig)
    elif hist_type == 'type2':
        hist_fig = histogram_type2(pimms_df.get_data()[NIM_control_col], pimms_df.get_data()[NIM_test_col],
                                          bin_size=bin_size)
        return dcc.Graph(id='hist-fig-t2', figure=hist_fig)


@app.callback(
    Output('hist-fig-t1', 'figure'),
    [Input('hist-fig-t1', 'relayoutData'),
     Input('hist-bin-size', 'value'),
     State('session-id', 'children')],
    prevent_initial_call=True
)
def display_hist_type1(relayoutData, bin_size, session_id):
    """
    Callback to update type1 hist according to updated ranges. Used to keep interactivity in the type1 hist where
    multiple subplots are used with the lower hist flipped vertically.
    :param relayoutData: dict containing relayout data from histogram. see plotly docs.
    :param bin_size: histogram bin size
    :param session_id: uuid of session
    :return:
    """
    if relayoutData:
        data = load_data("pimms_df", session_id)
        if 'autosize' in relayoutData:
            raise PreventUpdate
        # Load data from store
        pimms_df = PIMMSDataFrame.from_json(data)
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
        return histogram(pimms_df.get_data()[NIM_control_col], pimms_df.get_data()[NIM_test_col],
                                range_x=r_x, range_y=r_y, bin_size=bin_size)
    raise PreventUpdate


@app.callback(
    [Output("tab3-venn-div", "children"),
     Output("tab3-venn-label", "children"),
     Output("tab3-venn-datatable-div", "children")],
    [Input("run-status", "data"),
     Input('venn-slider', 'value'),
     Input('venn-inserts-slider', 'value'),
     Input("venn-table-radioitems", "value"),
     State('session-id', 'children')],
    prevent_initial_call=True
)
def create_venn(run_status, thresh_c, slider_c, radioitems, session_id):
    """
    Callback to create/update venn diagram when new data in dcc.store or venn options are changed.
    Also creates the venn datatable below the diagram.
    :param thresh_c: NIM score threshold from slider
    :param slider_c: Inserts range from slider
    :param radioitems: Checklist of venn table options
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """

    def assign_set(a, b):
        if a and b:
            return "AB"
        elif a and not b:
            return "Ab"
        elif b and not a:
            return "aB"
        else:
            return np.nan

    if not run_status["pimms"]:
        raise PreventUpdate

    data = load_data('pimms_df', session_id)

    # Load data from store
    pimms_df = PIMMSDataFrame.from_json(data)
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()
    perc_test_cols, perc_control_cols = pimms_df.test_control_cols_containing('insert_posn_as_percentile')
    # Create an unique identifier column
    pimms_df.insert_column('unique', np.arange(len(pimms_df)).astype(str))

    # Apply filters to get sets
    df = pimms_df.get_data().copy(deep=True)
    df["_control_set_"] = np.where(
        ((df[NIM_control_col] <= thresh_c) &
         (df[perc_control_cols[0]] >= slider_c[0]) &
         (df[perc_control_cols[1]] <= slider_c[1])),
        True,
        False
    )
    df["_test_set_"] = np.where(
        ((df[NIM_test_col] <= thresh_c) &
         (df[perc_test_cols[0]] >= slider_c[0]) &
         (df[perc_test_cols[1]] <= slider_c[1])),
        True,
        False
    )
    df["_set_"] = df.apply(lambda row: assign_set(row["_control_set_"],row["_test_set_"]), axis=1)

    # Create Venn
    control_set = df[df["_control_set_"] == True]['unique']
    test_set = df[df["_test_set_"] == True]['unique']
    venn_img = venn_diagram(control_set, test_set) #'#4e5e6c'

    # Create Venn Label
    label = dcc.Markdown(f"""
    * **Set A**: 
    {NIM_control_col.replace("_"," ")}

    * **Set B**:
    {NIM_test_col.replace("_"," ")}

    """)

    # Filter rows. Move prior to creating venn_img to change diagram using radioitems.
    if radioitems != "all":
        df = df[df["_set_"] == radioitems]

    # Create Venn datatable
    df_cols = pimms_df.info_columns + perc_test_cols + perc_control_cols + [NIM_test_col, NIM_control_col, "_set_"]
    df_cols.pop(0)
    style_data_conditional = [
                                 {'if': {"filter_query": f"{{_set_}} = AB"},
                                  "backgroundColor": "#b599c7"},
                                 {'if': {"filter_query": f"{{_set_}} = Ab"},
                                  "backgroundColor": "#8ebbda"},
                                 {'if': {"filter_query": f"{{_set_}} = aB"},
                                  "backgroundColor": "#ffbf87"},
                             ]
    table = main_datatable(df[df_cols], id="venn-datatable",
                           style_data_conditional=style_data_conditional,
                           style_table={'height': '100em', 'overflowY': 'auto'},
                           fixed_rows={"headers":True},
                           page_size=50)

    return html.Img(src=venn_img, id='venn-image'), label, table


@app.callback(
    Output("venn-datatable-collapse", "is_open"),
    [Input("venn-collapse-button", "n_clicks")],
    [State("venn-datatable-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('tab4-scatter-div', 'children'),
    [Input("run-status", "data"),
     Input("scatter-checklist", 'value'),
     State("session-id", "children")],
    prevent_initial_call=True
)
def create_genome_scatter(run_status, checkbox, session_id):
    """
    Callback to create/update genome scatter plot.
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :param checkbox: scatter options checkbox
    :return:
    """
    if not run_status["gff_control"]:
        raise PreventUpdate

    data_control = load_data("gff_df_control", session_id)
    data_test = load_data("gff_df_test", session_id)
    gff_df_control = GffDataFrame.from_json(data_control)
    gff_df_test = GffDataFrame.from_json(data_test)
    # Create figure
    fig = genome_comparison_scatter(gff_df_control, gff_df_test)
    # Change to log axis if checked
    if 'log' in checkbox:
        fig.update_yaxes(type="log")

    fig.update_layout(height=700)
    return dcc.Graph(id='gff-scatter-fig', figure=fig)


@app.callback(Output('tab5-circos-div', 'children'),
              [Input("run-status", "data"),
               Input('circos-gen-slider', 'value'),
               Input("circos-checklist", 'value'),
               Input("comparison-metric-dropdown", "value"),
               State('session-id', 'children')],
              prevent_initial_call=True
)
def create_circos(run_status, g_len, checkbox, c_metric, session_id):
    """
    Callback to create/update circos plot
    :param g_len: int, length of genome to display from slider. 0 to 1
    :param checkbox: list of circos checked options
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :param c_metric: selected comparision metric
    :return:
    """
    if not run_status["pimms"]:
        raise PreventUpdate

    data = load_data('pimms_df', session_id)

    hide_zeros = 'hide_zero' in checkbox
    # Load data from dcc.Store
    pimms_df = PIMMSDataFrame.from_json(data)
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

    # Calc genome range and limit using slider values
    genome_range = pimms_df.get_data()['end'].max() - pimms_df.get_data()['start'].min()
    start = int(g_len[0] * genome_range)
    end = int(g_len[1] * genome_range)

    # Default c_metric to first if 'all' or None selected
    if c_metric in ["all", None]:
        c_metric = pimms_df.comparison_cols[0]

    # Create dataframe for each circos ring, rename cols to relevant names for circos to pick up
    inner_ring = pimms_df.get_data()[pimms_df.info_columns + [NIM_control_col]]
    inner_ring = inner_ring.rename(columns={"seq_id": "block_id", NIM_control_col: "value"})
    outer_ring = pimms_df.get_data()[pimms_df.info_columns + [NIM_test_col]]
    outer_ring = outer_ring.rename(columns={"seq_id": "block_id", NIM_test_col: "value"})
    hist_ring = pimms_df.get_data()[pimms_df.info_columns + [c_metric]]
    hist_ring = hist_ring.rename(columns={"seq_id": "block_id", c_metric: "value"})

    # Create the circos plot
    circos = pimms_circos(inner_ring, outer_ring, hist_ring, start, end, hide_zeros=hide_zeros)
    # Return Tab children
    return circos

@app.callback(
    Output("collapse-circos-slider", "is_open"),
    [Input("run-status", "data")],
    prevent_initial_call=True
)
def reveal_circos_slider(run_status):
    if run_status['pimms']:
        return True
    else:
        return False


@app.callback(
    Output('event-data-select', 'children'),
    [Input('main-circos', 'eventDatum')])
def circos_hover_description(event_datum):
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


@app.callback(
    Output("tab6-geneviewer-div", "children"),
    [Input("main-datatable", "selected_rows")],
    [State("run-status", "data"),
     State("session-id", "children")],
)
def create_needleplot(selected_rows, run_status, session_id):
    """
    Callback to display intragenic mutations when row is selected
    """
    if not (run_status["gff_control"] and run_status["gff_test"]):
        return "Load control and test coordinate gffs.\n" \
               "Select a gene in the DataTable tab"
    elif selected_rows:
        # Selected row can only be single value - extract from list
        row_index = selected_rows[0]

        # Load pimms gff
        data = load_data('pimms_df', session_id)
        pimms_df = PIMMSDataFrame.from_json(data)

        # Load test coordinate gff
        data_test = load_data("gff_df_test", session_id)
        gff_df_test = GffDataFrame.from_json(data_test)

        # Load control coordinate gff
        data_control = load_data("gff_df_control", session_id)
        gff_df_control = GffDataFrame.from_json(data_control)

        # Get gene label
        gene_start = pimms_df.get_data().at[row_index, "start"]
        gene_end = pimms_df.get_data().at[row_index, "end"]

        gene_id = pimms_df.get_data().at[row_index, "locus_tag"]
        gene_name = pimms_df.get_data().at[row_index, "gene"]
        if gene_name and gene_name is not np.nan:
            gene_label = f"{gene_id} - {gene_name}"
        else:
            gene_label = gene_id

        gene_interval = f"{gene_start}-{gene_end}"

        if gff_df_test.empty_score():
            inserts_data_t = gff_df_test.value_counts('start').reset_index().rename(
                columns={"index": "position", "start": "count"})
        else:
            inserts_data_t = gff_df_test[['start', 'score']].rename(columns={"start": "position", "score": "count"})

        if gff_df_control.empty_score():
            inserts_data_c = gff_df_control.value_counts('start').reset_index().rename(
                columns={"index": "position", "start": "count"})
        else:
            inserts_data_c = gff_df_control[['start', 'score']].rename(columns={"start": "position", "score": "count"})

        buffer = 0.1
        inserts_data_c = inserts_data_c[
            (inserts_data_c["position"] > (gene_start - buffer)) & (inserts_data_c["position"] < (gene_end + buffer))]
        inserts_data_t = inserts_data_t[
            (inserts_data_t["position"] > (gene_start - buffer)) & (inserts_data_t["position"] < (gene_end + buffer))]

        mutations = [str(x) for x in inserts_data_t["position"].values]
        counts = [str(x) for x in inserts_data_t["count"].values]
        groups = ["Test Mutation"]*len(inserts_data_t)

        mutations = mutations + [str(x) for x in inserts_data_c["position"].values]
        counts = counts + [str(x) for x in inserts_data_c["count"].values]
        groups = groups + ["Control Mutation"]*len(inserts_data_c)


        needledata = dict(
            x=mutations,
            y=counts,
            mutationGroups=groups,
            domains=[dict(name=gene_label, coord=gene_interval)]
        )
        if len(mutations) == 0:
            return f"No Mutations to plot within {gene_label}"
        else:
            return dashbio.NeedlePlot(
                id="needleplot",
                mutationData=needledata,
                domainStyle={
                    'displayMinorDomains': True,
                    'domainColor': ['#FFDD00']
                },
                xlabel="Position",
                ylabel="Mutation Count"
            )
    else:
        raise PreventUpdate