import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import dash_daq as daq


def tab_three_layout():
    layout = \
        dcc.Tab([
            html.Div([
                "DATA GOES HERE!"
            ]),
        ], label="Data",)
    return layout