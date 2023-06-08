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
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show Scatter Options",
                            id="scatter-collapse-button",
                            color="info",
                            className="mt-3"
                        ),
                    ),
                ],
                justify="center"
            ),
            dbc.Collapse(
                [
                    dbc.Row(
                        [
                            dbc.Col(
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
                                ],
                            ),
                        ],
                        className="mt-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Marker Size:", html_for="scatter-marker-size-input", width="auto"),
                                    dbc.Input(
                                        id="scatter-marker-size-input", type="number", min=0, max=10, step=0.1, value=4,
                                    ),
                                ],
                                width=6
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Marker line width:", html_for="scatter-marker-line-width-input", width="auto"),
                                    dbc.Input(
                                        id="scatter-marker-line-width-input", type="number", min=0, max=10, step=0.1, value=1,
                                    ),
                                ],
                                width=6
                            ),
                        ],
                        className="mt-3"
                    )
                ],
                id="scatter-options-collapse",
                className="ml-3"
            ),
        ]
    ),
    className="mt-3",
)


@app.callback(
    Output('tab4-scatter-div', 'children'),
    [Input("run-status", "data"),
     Input("scatter-checklist", 'value'),
     Input('plot-color-store', 'data'),
     Input("scatter-marker-size-input", 'value'),
     Input("scatter-marker-line-width-input", 'value'),
     Input('plotlabel_control', 'value'),
     Input('plotlabel_test', 'value'),
     State("session-id", "data")],
    prevent_initial_call=True
)
def create_genome_scatter(run_status, checkbox, colors, marker_size, marker_line_width,
                          label_control, label_test, session_id):
    """
    Callback to create/update genome scatter plot.
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :param checkbox: scatter options checkbox
    :return:
    """
    if not run_status or not (run_status["gff_control"] and run_status["gff_test"]):
        raise PreventUpdate

    if run_status["control-run"]:
        return "Control Run: Genome Scatter Not Available"

    data_control = load_data("gff_df_control", session_id)
    data_test = load_data("gff_df_test", session_id)
    gff_df_control = GffDataFrame.from_json(data_control)
    gff_df_test = GffDataFrame.from_json(data_test)
    # Create figure
    control_title = f"Insertions Across {label_control} Phenotype"
    test_title = f"Insertions Across {label_test} Phenotype"
    fig = genome_comparison_scatter(
        gff_df_control, gff_df_test, control_title, test_title)
    # Change to log axis if checked
    if 'log' in checkbox:
        fig.update_yaxes(type="log")
    fig.update_traces(marker_color=colors['control'], marker_line_width=marker_line_width, marker_size=marker_size, row=1)
    fig.update_traces(marker_color=colors['test'], marker_line_width=marker_line_width, marker_size=marker_size, row=2)
    fig.update_layout(height=700)
    return dcc.Graph(id='gff-scatter-fig', figure=fig)

@app.callback(
    Output("scatter-options-collapse", "is_open"),
    [Input("scatter-collapse-button", "n_clicks")],
    [State("scatter-options-collapse", "is_open")],
)
def toggle_collapse_scatter(n, is_open):
    if n:
        return not is_open
    return is_open
