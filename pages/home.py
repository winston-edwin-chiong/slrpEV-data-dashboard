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
                html.H2(id="homepage_kwh")
            ])
        ]),
        dbc.Card([
            dbc.CardHeader([
                html.H5("Users Today", className="card-title"),
            ]),
            dbc.CardBody([
                html.H2(id="homepage_users"),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader([
                html.H5("Peak Power This Month", className="card-title"),
            ]),
            dbc.CardBody([
                html.H2(id="homepage_peak_power"),
            ])
        ]),
        html.Div([
            dcc.Interval(
                id="data_refresh_interval_component",
                interval=30 * 60 * 1000,  # update every 30 minutes
                n_intervals=0
            ),
            dcc.Store(id="data_refresh_signal"),
        ]),
        html.Div(
            id="last_updated_timer"
        )
    ])
