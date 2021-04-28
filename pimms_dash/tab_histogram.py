import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from utils import PIMMSDataFrame, load_data
from figures import histogram, histogram_type2


histogram_tab_layout = dbc.Card(
    dbc.CardBody(
        [
            html.Div("No Input Data Loaded", id="tab2-hist-div")
        ]
    ),
    className="mt-3",
)


@app.callback(
    Output('tab2-hist-div', 'children'),
    [Input('run-status', 'data'),
     Input('hist-dropdown-type', 'value'),
     Input('hist-bin-size', 'value'),
     State('session-id', 'data')],
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
    if not run_status or not run_status["pimms"]:
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
     State('session-id', 'data')],
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
