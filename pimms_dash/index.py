import uuid

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

from app import app, app_title
from panel_control import control_panel_layout
from tab_about import about_tab_layout
from tab_datatable import datatable_tab_layout
from tab_histogram import histogram_tab_layout
from tab_venn import venn_tab_layout
from tab_genome_scatter import genome_scatter_tab_layout
from tab_circos import circos_tab_layout
from tab_geneviewer import geneviewer_tab_layout
from tab_NIM_comparison import NIM_comparison_tab_layout
from utils import manage_session_data


# Header
def create_header(title):
    return html.Div(
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src="/assets/UoN_Primary_Logo_Rev_RGB_REV.png",
                        top=True, style={"width": "18rem"},
                        className="mb-3"
                    ),
                    width=6
                ),
                dbc.Col(
                    html.H1(
                        title,
                        style={"color": "white"},
                        className="text-right mr-3"
                    ),
                    width=6,
                )
            ],
            no_gutters=True,
            align="center",
        ),
    style={"backgroundColor": "#1b2b6b"},
    className="mt-3"
    )

def serve_layout():
    session_id = str(uuid.uuid4())
    return dbc.Container(
        [
            dcc.Store(data=session_id, id='session-id', storage_type='session'),
            create_header(app_title),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        control_panel_layout,
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Tabs(
                            [
                                dbc.Tab(about_tab_layout, label="About", labelClassName="text-dark"),
                                dbc.Tab(datatable_tab_layout, label="DataTable", labelClassName="text-dark"),
                                dbc.Tab(NIM_comparison_tab_layout, label="NIM Comparison", labelClassName="text-dark"),
                                #dbc.Tab(histogram_tab_layout, label="Histogram", labelClassName="text-dark"),
                                dbc.Tab(venn_tab_layout, label="Venn", labelClassName="text-dark"),
                                dbc.Tab(genome_scatter_tab_layout, label="Genome Scatter", labelClassName="text-dark"),
                                #dbc.Tab(circos_tab_layout, label="Circos", labelClassName="text-dark"),
                                dbc.Tab(geneviewer_tab_layout, label="GeneViewer", labelClassName="text-dark"),
                            ],
                        ),
                        width=9
                    )
                ]
            )
        ],
        fluid=True
    )

app.layout = serve_layout

def run_app():
    manage_session_data()
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )

if __name__ == '__main__':
    run_app()
