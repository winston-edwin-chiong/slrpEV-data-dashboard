import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import dash_daq as daq

dash.register_page(__name__)

layout = \
    html.Div([
        html.Div([
            "DATA GOES HERE!"
        ]),
    ])