import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

import numpy as np
import pandas as pd

from app import app
from utils import PIMMSDataFrame, GffDataFrame, load_data
from figures import main_datatable, mpl_needleplot


geneviewer_tab_layout = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("Select a gene in the DataTable tab", id="tab6-geneviewer-div"))
                ],
                justify="center"
            ),
            html.Br(),
            dbc.Button(id="geneviewer-reload-button", children="reload", color="dark", outline=True,
                       style={"width": 75, "padding": 0}),
            html.Hr(),
            dbc.Row(
                [
                    dcc.Markdown(id="geneviewer-markdown")
                ],
                className="ml-1"
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show Geneviewer Options",
                            id="geneviewer-collapse-options-button",
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
                                    dbc.Label("Marker Size:", html_for="geneviewer-marker-size-input", width="auto"),
                                    dbc.Input(
                                        id="geneviewer-marker-size-input", type="number", min=0, max=20, step=0.1,
                                        value=6,
                                    ),
                                ],
                                width=4
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Stem width:", html_for="geneviewer-stem-line-width-input",
                                              width="auto"),
                                    dbc.Input(
                                        id="geneviewer-stem-line-width-input", type="number", min=0, max=10, step=0.1,
                                        value=1,
                                    ),
                                ],
                                width=4
                            ),
                        ],
                        className="mt-3"
                    )
                ],
                id="geneviewer-options-collapse",
                className="ml-3"
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Show Insert Data Table",
                            id="geneviewer-collapse-button",
                            color="info",
                        ),
                    ),
                ],
                className="mt-3",
                justify="center"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Collapse(
                            [
                                html.Div("No Input Data Loaded", id="tab6-geneviewer-datatable-div",className="mt-3")
                            ],
                            id="geneviewer-datatable-collapse"
                        )
                    )
                ],
                className="mt-3"
            )
        ]
    ),
    className="mt-3",
)


@app.callback(
    [Output("tab6-geneviewer-div", "children"),
     Output("geneviewer-markdown", "children"),
     Output("tab6-geneviewer-datatable-div", "children")],
    [Input("main-datatable", "selected_rows"),
     Input("plot-color-store", "data"),
     Input("geneviewer-reload-button", "n_clicks"),
     Input("geneviewer-marker-size-input", 'value'),
     Input("geneviewer-stem-line-width-input", 'value')],
    [State("run-status", "data"),
     State("dashboard-tabs", "active_tab"),
     State("session-id", "data")],
)
def create_needleplot(selected_rows, colors, reload_clicks, marker_size, stem_width, run_status, active_tab, session_id):
    """
    Callback to display intergenic mutations when row is selected.
    Also returns markdown of information on needleplot.
    Also returns Datatable object of mutations from coord gff.
    """
    trigger = callback_context.triggered[0]['prop_id'].split('.')[0]

    if (
        not (
            run_status["gff_control"] and run_status["gff_test"]
        ) and not run_status['control-run']
    ) or (
        run_status['control-run'] and not run_status["gff_control"]
    ):
        return "Load control and test coordinate gffs.\n" \
               "Select a gene in the DataTable tab", "", ""
    elif trigger == "plot-color-store" and active_tab != "geneviewer":
        raise PreventUpdate
    elif selected_rows:
        # Selected row can only be single value - extract from list
        row_index = selected_rows[0]

        # Load pimms gff
        data = load_data('pimms_df', session_id)
        pimms_df = PIMMSDataFrame.from_json(data)

        # Get gene start and end
        gene_start = pimms_df.get_data().at[row_index, "start"]
        gene_end = pimms_df.get_data().at[row_index, "end"]

        # Get gene label
        gene_id = pimms_df.get_data().at[row_index, "locus_tag"]
        gene_name = pimms_df.get_data().at[row_index, "gene"]
        if gene_name and gene_name is not np.nan:
            gene_label = f"{gene_id} - {gene_name}"
        else:
            gene_label = gene_id

        buffer_prc = 0 #Todo control intergenic buffer with slider.
        buffer = buffer_prc * (gene_end - gene_start)

        if not run_status['control-run']:
            # Load test coordinate gff
            data_test = load_data("gff_df_test", session_id)
            gff_df_test = GffDataFrame.from_json(data_test)

            # get mutations in test from gff df
            if gff_df_test.empty_score():
                inserts_data_t = gff_df_test.value_counts('start').reset_index().rename(
                    columns={"index": "position", "start": "count"})
            else:
                inserts_data_t = gff_df_test[['start', 'score']].rename(columns={"start": "position", "score": "count"})

            # tRestrict mutations in test to gene plus a percentage buffer
            inserts_data_t = inserts_data_t[
                (inserts_data_t["position"] > (gene_start - buffer)) & (inserts_data_t["position"] < (gene_end + buffer))]
        else:
            inserts_data_t = pd.DataFrame(columns=['position', 'count'])

        # Load control coordinate gff
        data_control = load_data("gff_df_control", session_id)
        gff_df_control = GffDataFrame.from_json(data_control)

        # get mutations in control from gff df
        if gff_df_control.empty_score():
            inserts_data_c = gff_df_control.value_counts('start').reset_index().rename(
                columns={"index": "position", "start": "count"})
        else:
            inserts_data_c = gff_df_control[['start', 'score']].rename(columns={"start": "position", "score": "count"})

        # Restrict mutations in control to gene plus a percentage buffer
        inserts_data_c = inserts_data_c[
            (inserts_data_c["position"] > (gene_start - buffer)) & (inserts_data_c["position"] < (gene_end + buffer))]

        # Create wide data view for table
        wide_table = inserts_data_c.merge(inserts_data_t, how="outer", on="position")
        wide_table = (wide_table
                      .fillna(0.0)
                      .sort_values(by="position")
                      .rename(columns={"count_x": "control count", "count_y": "test count"})
                      .reset_index(drop=True))

        # Create intergenic column to highlight mutations that occur within gene and not buffer.
        inserts_data_c["within CDS"] = ((inserts_data_c["position"] >= gene_start) & (inserts_data_c["position"] <= gene_end))
        inserts_data_t["within CDS"] = ((inserts_data_t["position"] >= gene_start) & (inserts_data_t["position"] <= gene_end))
        wide_table["within CDS"] = ((wide_table["position"] >= gene_start) & (wide_table["position"] <= gene_end))

        # Create mutation_data df - Assign group column and append control and test
        inserts_data_c["group"] = "Control"
        inserts_data_t["group"] = "Test"
        mutation_data = inserts_data_t.append(inserts_data_c).sort_values(by="position")

        # Format markdown with mutation counts
        md_text = f"""
        Start Position: **{gene_start}**    End Position: **{gene_end}**

        * Control Phenotype Total Inserts: **{inserts_data_c[inserts_data_c["within CDS"]==True]["count"].sum()}**

        * Control Phenotype Unique Insert Sites: **{len(inserts_data_c[inserts_data_c["within CDS"]==True])}**

        * Test Phenotype Total Inserts: **{inserts_data_t[inserts_data_t["within CDS"]==True]["count"].sum()}**

        * Test Phenotype Unique Insert Sites: **{len(inserts_data_t[inserts_data_t["within CDS"]==True])}**
        """

        # Return objects to div children
        if mutation_data.empty:
            return f"No Mutations to plot within {gene_label}", "", ""
        else:
            needleplot_img = mpl_needleplot(mutation_data, gene_label, gene_start, gene_end, color_dict=colors,
                                            stem_width=stem_width, marker_size=marker_size)
            mutation_table = main_datatable(wide_table, id="venn-datatable",
                           style_table={'height': '100em', 'overflowY': 'auto'},
                           fixed_rows={"headers":True},
                           page_size=50,
                           export_format="xlsx")
            return html.Img(src=needleplot_img, id='geneviewer-image'), md_text, mutation_table
    else:
        raise PreventUpdate


@app.callback(
    Output("geneviewer-datatable-collapse", "is_open"),
    [Input("geneviewer-collapse-button", "n_clicks")],
    [State("geneviewer-datatable-collapse", "is_open")],
)
def toggle_collapse_geneviewer(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("geneviewer-options-collapse", "is_open"),
    [Input("geneviewer-collapse-options-button", "n_clicks")],
    [State("geneviewer-options-collapse", "is_open")],
)
def toggle_collapse_venn(n, is_open):
    if n:
        return not is_open
    return is_open