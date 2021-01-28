import uuid

import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
from panel_control import control_tabs
from panel_analysis import analysis_tabs
from utils import manage_session_data

app_title = 'Pimms Dashboard'


# Header
def create_header(title):
    return dbc.Row(
        [
            dbc.Col(
                html.Div(html.H1(title), id='title'),
                width=8,
                className="mt-3"
            ),
            dbc.Col(
                html.A(
                    html.H2('DRS|UoN'),
                    href="https://digitalresearch.nottingham.ac.uk/",
                    id='drs_link', className="text-right"),
                width=4,
            )
        ],
        no_gutters=True,
        align="center",
        id="header"
    )


app.layout = dbc.Container(
    [
        html.Div(str(uuid.uuid4()), id='session-id', style={'display': 'none'}),
        create_header(app_title),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    control_tabs,
                    width=3,
                ),
                dbc.Col(
                    analysis_tabs,
                    width=9
                )
            ]
        )
    ],
    fluid=True
)


def run_app():
    manage_session_data()
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )

if __name__ == '__main__':
    run_app()
