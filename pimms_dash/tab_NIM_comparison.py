import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from utils import PIMMSDataFrame, load_data
from figures import NIM_comparison_linked


NIM_comparison_tab_layout = dbc.Card(
    dbc.CardBody(
        [
            html.Div("", id="NIM-comparison-div"),
        ]
    ),
    className="mt-3",
)


@app.callback(
    Output('NIM-comparison-div', 'children'),
    [Input('run-status', 'data'),
     State('session-id', 'data')],
    prevent_initial_call=True
)
def create_comparison_subplot(run_status, session_id):
    """
    Callback to create bar chart and linked heatmap.
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """
    if not run_status or not run_status["pimms"]:
        raise PreventUpdate

    data = load_data('pimms_df', session_id)

    # Load data from store
    pimms_df = PIMMSDataFrame.from_json(data)
    NIM_test_col, NIM_control_col = pimms_df.get_NIM_score_columns()

    df = pimms_df.get_data()
    fig = NIM_comparison_linked(df[NIM_control_col], df[NIM_test_col], df["start"], df["end"], df["locus_tag"])

    return dcc.Graph(id='NIM-comparison-fig', figure=fig)
