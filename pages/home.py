import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc 
import pickle
from dash.dependencies import Output, Input, State
from plotting import plottingfunctions as pltf
from dash import html, dcc
from tasks.schedule import redis_client
from datetime import datetime


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


@dash.callback(
    Output("homepage-kwh", "children"),
    Output("homepage-users", "children"),
    Output("homepage-peak-power", "children"),
    Input("data_refresh_signal", "data"),
)
def update_today_homepage_cards(n):
    # load data
    today = pickle.loads(redis_client.get("todays_sessions"))
    monthlydemand = pickle.loads(redis_client.get("monthlydemand"))
    # filter data to just this month
    monthlydemand = monthlydemand.loc[monthlydemand.index >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)]
    # extract peak power 
    peak_power = str(monthlydemand["peak_power_W"][0]) + " W"

    if len(today) == 0:
        return 0, 0, peak_power
    else:
        today = today[["dcosId", "cumEnergy_Wh", "vehicle_model"]].groupby("dcosId").first().copy()
        kwh_today = str(today["cumEnergy_Wh"].sum(axis=0) / 1000) + " kWh"
        num_users = len(today)
        return kwh_today, num_users, peak_power
    

@dash.callback(
    Output("homepage-cum-kwh", "children"),
    Output("homepage-cum-sessions", "children"),
    Output("homepage-cum-emiles", "children"),
    Input("data_refresh_signal", "data")
)
def update_cum_homepage_cards(n):
    # load data
    raw_data = pickle.loads(redis_client.get("raw_data"))
    num_sessions = len(raw_data)
    cum_energy_delivered = str(round(raw_data["cumEnergy_Wh"].sum() / 1000, 1)) + " kWh"
    cum_emiles_delivered = str(round(raw_data["cumEnergy_Wh"].sum() / 290, 0)) + " Mi"
    return cum_energy_delivered, num_sessions, cum_emiles_delivered
