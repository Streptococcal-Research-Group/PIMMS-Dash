import uuid

import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
from panel_control import control_tabs
from panel_analysis import analysis_tabs
from utils import manage_session_data

app_title = 'PIMMS | Dashboard'


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
