import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import pandas as pd

from app import app
from utils import PIMMSDataFrame, load_data
from figures import pca_plot


pca_tab_layout = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("No Data Loaded", id="tab-pca-div"))
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show PCA Options",
                            id="pca-collapse-options-button",
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
                                    dbc.Label("Marker Size:", html_for="pca-marker-size-input", width="auto"),
                                    dbc.Input(
                                        id="pca-marker-size-input", type="number", min=0, max=20, step=0.1, value=12,
                                    ),
                                ],
                                width=6
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Marker line width:", html_for="pca-marker-line-width-input",
                                              width="auto"),
                                    dbc.Input(
                                        id="pca-marker-line-width-input", type="number", min=0, max=10, step=0.1,
                                        value=1,
                                    ),
                                ],
                                width=6
                            ),
                        ],
                        className="mt-3"
                    )
                ],
                id="pca-options-collapse",
                className="ml-3"
            ),
        ]
    ),
    className="mt-3",
)

@app.callback(
    Output('tab-pca-div', 'children'),
    [Input("run-status", "data"),
     Input('plot-color-store', 'data'),
     Input("pca-marker-size-input", 'value'),
     Input("pca-marker-line-width-input", 'value'),
     State("session-id", "data")],
    prevent_initial_call=True
)
def create_pca_pca(run_status, colors, marker_size, marker_line_width, session_id):
    """
    Callback to create/update pca plot.
    :param run_status: dictionary containing run success information
    :param session_id: uuid of session
    :return:
    """
    if (not run_status or not run_status["pimms"]):
        return "No Data Loaded"
    elif run_status["deseq"]["mutantpools"] == 0:
        return "No replicates found"
    elif run_status["deseq"]["run"] is False:
        return "DESeq not run"
    elif run_status["deseq"]["success"] is False:
        return "DESeq run failed"

    data = load_data('pimms_df', session_id)

    # Load data from store
    pimms_df = PIMMSDataFrame.from_json(data)

    pca_df = pd.DataFrame.from_dict(pimms_df.pca_dict, orient="index")
    pca_df["group"] = pd.Series(pca_df.index).apply(lambda x: x.split("_")[-1]).to_list()
    labels = pimms_df.pca_labels

    fig = pca_plot(pca_df, colors["control"], colors["test"])
    fig.update_xaxes(title=labels["x_label"])
    fig.update_yaxes(title=labels["y_label"])

    fig.update_traces(marker_line_width=marker_line_width, marker_size=marker_size)

    return dcc.Graph(id='pca-scatter-fig', figure=fig)

@app.callback(
    Output("pca-options-collapse", "is_open"),
    [Input("pca-collapse-options-button", "n_clicks")],
    [State("pca-options-collapse", "is_open")],
)
def toggle_collapse_venn(n, is_open):
    if n:
        return not is_open
    return is_open