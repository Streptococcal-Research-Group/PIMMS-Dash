import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from utils import PIMMSDataFrame, load_data
from circos import pimms_circos


circos_tab_layout = dbc.Card(
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


@app.callback(Output('tab5-circos-div', 'children'),
              [Input("run-status", "data"),
               Input('circos-gen-slider', 'value'),
               Input("circos-checklist", 'value'),
               Input("comparison-metric-dropdown", "value"),
               State('session-id', 'data')],
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
    if not run_status or not run_status["pimms"]:
        raise PreventUpdate

    if run_status["control-run"]:
        return "Control Run: Circos Not Available"

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