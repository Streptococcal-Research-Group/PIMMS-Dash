import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_table.Format import Format, Scheme

from utils import PIMMSDataFrame, load_data
from figures import main_datatable

from app import app


datatable_tab_layout = dbc.Card(
    dbc.CardBody(
        [
            html.Div("No Input Data Loaded", id="tab1-datatable-div")
        ]
    ),
    className="mt-1",
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
        return main_datatable(pimms_df.get_data(), id="main-datatable", row_selectable='single', export_format="xlsx")
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
    if not run_status or not run_status['pimms']:
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