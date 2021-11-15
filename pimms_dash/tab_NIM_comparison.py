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
            dcc.Loading(
                html.Div("No Input Data Loaded", id="NIM-comparison-div"),
                type="dot",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show NIM Options",
                            id="nim-collapse-button",
                            color="info",
                            className="mt-3"
                        ),
                    ),
                ],
                justify="center"
            ),
            dbc.Collapse(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Choose Mode:"),
                            dbc.RadioItems(
                                options=[
                                    {"label": "NIM", "value": "nim"},
                                    {"label": "NRM", "value": "nrm"},
                                ],
                                value="nim",
                                id="nim-comp-radio",
                                inline=True,
                            ),
                        ],
                        className="mt-3"
                    ),
                ],
                id="nim-options-collapse",
                className="ml-3"
            ),
        ]
    ),
    className="mt-3",
)


@app.callback(
    Output('NIM-comparison-div', 'children'),
    [Input('run-status', 'data'),
     Input('nim-comp-radio', 'value'),
     Input('plot-color-store', 'data'),
     Input('plotlabel_control', 'value'),
     Input('plotlabel_test', 'value'),
     State('session-id', 'data')],
    prevent_initial_call=True
)
def create_comparison_subplot(run_status, mode, colors, test_label, control_label, session_id):
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

    if mode == 'nim':
        test_col, control_col = pimms_df.get_NIM_score_columns()
        title = "NIM Score Across Genome"
        y_title = "NIM Score"
    elif mode == 'nrm':
        test_col, control_col = pimms_df.get_NRM_score_columns()
        title = "NRM Score Across Genome"
        y_title = "NRM Score"
    else:
        raise PreventUpdate

    df = pimms_df.get_data()
    series_control = df[control_col]
    series_test = df[test_col]
    fig = NIM_comparison_linked(
        series_control, series_test, df["start"], df["end"], df["locus_tag"], title=title,
        color_control=colors['control'], color_test=colors['test'],
        test_label=test_label, control_label=control_label,
    )

    fig['layout']['yaxis1'].update(title=y_title)

    return dcc.Graph(id='NIM-comparison-fig', figure=fig)

@app.callback(
    Output("nim-options-collapse", "is_open"),
    [Input("nim-collapse-button", "n_clicks")],
    [State("nim-options-collapse", "is_open")],
)
def toggle_collapse_nim(n, is_open):
    if n:
        return not is_open
    return is_open