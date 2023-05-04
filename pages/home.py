import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = \
    html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("Energy Delivered Today", className="card-title"),
            ]),
            dbc.CardBody([
                html.H2("420 kWh")
            ])
        ]),
        dbc.Card([
            dbc.CardHeader([
                html.H5("Users Today", className="card-title"),
            ]),
            dbc.CardBody([
                html.H2("420"),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader([
                html.H5("Peak Power This Month", className="card-title"),
            ]),
            dbc.CardBody([
                html.H2("420 W"),
            ])
        ])
    ])
