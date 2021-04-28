import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import numpy as np

from app import app
from utils import PIMMSDataFrame, load_data
from figures import main_datatable, venn_diagram


venn_tab_layout = dbc.Card(
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
                ],
                justify="center"
            ),
            dbc.Collapse(
                [
                    dbc.Row(
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
                        className="mt-3"
                    ),
                    dbc.Row(
                        dbc.Checklist(
                            options=[
                                {"label": "Highlight Truncated <10th", "value": "<10"},
                                {"label": "Highlight Truncated >90th", "value": ">90"},
                            ],
                            value=[],
                            id="venn-table-checklist",
                            switch=True,
                            inline=True,
                        ),
                        className="mt-3"
                    ),
                    dbc.Row(
                        html.Div("No Input Data Loaded", id="tab3-venn-datatable-div", className="mt-3"),
                        className="mt-3"
                    ),
                ],
                id="venn-datatable-collapse",
                className="ml-3"
            ),
        ],
    ),
    className="mt-3",
)


@app.callback(
    [Output("tab3-venn-div", "children"),
     Output("tab3-venn-label", "children"),
     Output("tab3-venn-datatable-div", "children")],
    [Input("run-status", "data"),
     Input('venn-slider', 'value'),
     Input('venn-inserts-slider', 'value'),
     Input("venn-table-radioitems", "value"),
     Input("venn-table-checklist", "value"),
     State('session-id', 'data')],
    prevent_initial_call=True
)
def create_venn(run_status, thresh_c, slider_c, radioitems, checklist, session_id):
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

    if not run_status or not run_status["pimms"]:
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

    style_data_conditional = []
    # If displaying all sets style by set

    style_data_conditional = [
                                 {'if': {"filter_query": f"{{_set_}} = AB", "column_id": "_set_"},
                                  "backgroundColor": "rgba(181, 153, 199, 0.5)"},
                                 {'if': {"filter_query": f"{{_set_}} = Ab", "column_id": "_set_"},
                                  "backgroundColor": "rgba(143, 189, 219, 0.5)"},
                                 {'if': {"filter_query": f"{{_set_}} = aB", "column_id": "_set_"},
                                  "backgroundColor": "rgba(255, 190, 133, 0.5)"},
                             ]
    if checklist and "<10" in checklist:
        style_data_conditional.append(
            {'if': {"filter_query": f"{{{perc_test_cols[1]}}} < 10 && {{{perc_test_cols[1]}}} > 0",
                    "column_id": [f'{perc_test_cols[0]}', f'{perc_test_cols[1]}']},
             "backgroundColor": "rgba(151, 2, 2, 0.4)"}
        )
        style_data_conditional.append(
            {'if': {"filter_query": f"{{{perc_control_cols[1]}}} < 10 && {{{perc_control_cols[1]}}} > 0",
                    "column_id": [f'{perc_control_cols[0]}', f'{perc_control_cols[1]}']},
             "backgroundColor": "rgba(151, 2, 2, 0.4)"}
        )
    if checklist and ">90" in checklist:
        style_data_conditional.append(
            {'if': {"filter_query": f"{{{perc_test_cols[0]}}} > 90",
                    "column_id": [f'{perc_test_cols[0]}', f'{perc_test_cols[1]}']},
             "backgroundColor": "rgba(1, 152, 16, 0.4)"}
        )
        style_data_conditional.append(
            {'if': {"filter_query": f"{{{perc_control_cols[0]}}} > 90",
                    "column_id": [f'{perc_control_cols[0]}', f'{perc_control_cols[1]}']},
             "backgroundColor": "rgba(1, 152, 16, 0.4)"}
        )


    table = main_datatable(df[df_cols], id="venn-datatable",
                           style_data_conditional=style_data_conditional,
                           style_table={'height': '100em', 'overflowY': 'auto'},
                           fixed_rows={"headers":True},
                           page_size=50,
                           export_format="xlsx")

    return html.Img(src=venn_img, id='venn-image'), label, table


@app.callback(
    Output("venn-datatable-collapse", "is_open"),
    [Input("venn-collapse-button", "n_clicks")],
    [State("venn-datatable-collapse", "is_open")],
)
def toggle_collapse_venn(n, is_open):
    if n:
        return not is_open
    return is_open
