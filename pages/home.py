import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__, path="/")

layout = \
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Energy Delivered Today", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-kwh")
                    ])
                ]),                
            ], md=6, sm=12),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Cumulative Energy Delivered", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-cum-kwh")
                    ])
                ]),
            ], md=6, sm=12),
        ], className="my-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Cumulative E-Miles Delivered", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-cum-emiles")
                    ])
                ]),
            ], md=6, sm=12),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Users Today", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-users"),
                    ])
                ]),
            ], md=6, sm=12),
        ], className="my-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Cumulative Number of Sessions", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-cum-sessions"),
                    ])
                ]),
            ], md=6, sm=12),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Peak Power This Month", className="card-title"),
                    ]),
                    dbc.CardBody([
                        html.H2(id="homepage-peak-power"),
                    ])
                ]),
            ], md=6, sm=12),
        ], className="my-4"),
        # Interval components 
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
    ],
    fluid=True
    )
