import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from utils import GffDataFrame, load_data
from figures import genome_comparison_scatter


genome_scatter_tab_layout = dbc.Card(
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
    if not run_status or not run_status["gff_control"]:
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
