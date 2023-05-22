import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc 
import pickle
import pandas as pd 
from dash.dependencies import Output, Input, State
from plotting import plottingfunctions as pltf
from dash import html, dcc
from tasks.schedule import redis_client
from datetime import datetime


# --> Helper Functions <-- #

def calculate_pct_change(now, before):
    '''
    Calculate the percent change between two numbers.
    '''
    if before and now:
        return (now - before) * 100 / before
    elif not before and now: 
        return 100 
    return 0

def calcuate_stats_change(kwh_today, num_users, peak_power, dailydemand, raw_data, monthlydemand):

    # calculate daily kWh change 
    yesterday = pd.to_datetime(pd.Timestamp.now().normalize() - pd.DateOffset(days=1))
    yesterday_kwh = dailydemand.loc[dailydemand.index == yesterday]["energy_demand_kWh"].iloc[0]
    kwh_change = calculate_pct_change(kwh_today, yesterday_kwh)

    # calculate number of users change 
    yesterday_users = raw_data.loc[pd.to_datetime(raw_data["connectTime"]).dt.normalize() == yesterday]["userId"].nunique()
    num_users_change = num_users - yesterday_users

    # calculate monthly peak power change 
    last_month_peak_power = monthlydemand.iloc[[-2]]["peak_power_W"].iloc[0] / 1000
    peak_power_change = calculate_pct_change(peak_power, last_month_peak_power)

    return (
        [
            html.I(
                className="bi bi-arrow-up me-1" if kwh_change > 0 else ("bi bi-arrow-down me-1" if kwh_change else "bi bi-arrow-right me-1"), 
                style={"color": "#58c21e" if kwh_change > 0 else ("#c21e58" if kwh_change else "#55595c")}
                ), 
            f"{kwh_change:+} since yesterday!" if kwh_change else "No change since yesterday!"
        ],
        [
            html.I(
                className="bi bi-arrow-up me-1" if num_users_change > 0 else ("bi bi-arrow-down me-1" if num_users_change else "bi bi-arrow-right me-1"), 
                style={"color": "#58c21e" if num_users_change > 0 else ("#c21e58" if num_users_change else "#55595c")}
                ), 
            f"{num_users_change:+} users since yesterday!" if num_users_change else "No change since yesterday!"
        ],
        [
            html.I(
                className="bi bi-arrow-up me-1" if peak_power_change > 0 else ("bi bi-arrow-down me-1" if peak_power_change else "bi bi-arrow-right me-1"), 
                style={"color": "#58c21e" if peak_power_change > 0 else ("#c21e58" if peak_power_change else "#55595c")}
                ), 
            f"{round(peak_power_change, 2):+} % since last month!" if peak_power_change else "No change since last month!"
        ],
    )

# --> <-- #


dash.register_page(__name__, path="/")

layout = \
    html.Div([
        html.H1(datetime.now().strftime("%A, %B %d, %Y"), className="d-flex justify-content-center my-3"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cumulative Energy Delivered", className="card-title"),
                        ]),
                        dbc.CardBody([
                            html.H2(id="homepage-cum-kwh"),
                            html.Div(className="my-3", id="homepage-cum-kwh-stats")
                        ])
                    ], className="h-100 rounded shadow"),
                ], md=6, sm=12),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Energy Delivered Today", className="card-title"),
                        ]),
                        dbc.CardBody([
                            html.H2(id="homepage-kwh"),
                            html.Div(className="my-3", id="homepage-kwh-change")
                        ])
                    ], className="h-100 rounded shadow"),                
                ], md=6, sm=12),
            ], className="my-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cumulative E-Miles Delivered", className="card-title"),
                        ]),
                        dbc.CardBody([
                            html.H2(id="homepage-cum-emiles"),
                            html.Div(className="my-3", id="homepage-cum-emiles-stats")
                        ])
                    ], className="h-100 rounded shadow"),
                ], md=6, sm=12),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Users Today", className="card-title"),
                        ]),
                        dbc.CardBody([
                            html.H2(id="homepage-users"),
                            html.Div(className="my-3", id="homepage-users-change")
                        ])
                    ], className="h-100 rounded shadow"),
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
                            html.Div(className="my-3", id="homepage-cum-sessions-stats")
                        ])
                    ], className="h-100 rounded shadow"),
                ], md=6, sm=12),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Peak Power This Month", className="card-title"),
                        ]),
                        dbc.CardBody([
                            html.H2(id="homepage-peak-power"),
                            html.Div(className="my-3", id="homepage-peak-power-change")
                        ])
                    ], className="h-100 rounded shadow"),
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
    ])


# update daily and monthly stats homepage cards 
@dash.callback(
    Output("homepage-kwh", "children"),
    Output("homepage-users", "children"),
    Output("homepage-peak-power", "children"),
    Output("homepage-kwh-change", "children"),
    Output("homepage-users-change", "children"),
    Output("homepage-peak-power-change", "children"),
    Input("data_refresh_signal", "data"),
)
def update_today_homepage_cards(n):
    # load data
    today = pickle.loads(redis_client.get("todays_sessions"))
    monthlydemand = pickle.loads(redis_client.get("monthlydemand"))
    dailydemand = pickle.loads(redis_client.get("dailydemand"))
    raw_data = pickle.loads(redis_client.get("raw_data"))

    # filter data to just this month
    thismonthdemand = monthlydemand.loc[monthlydemand.index >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)]

    # extract peak power 
    peak_power_float = thismonthdemand["peak_power_W"][0] / 1000
    peak_power = f'{peak_power_float:,}' + " kW"


    # workaround for length of NoneType error
    if len(today) == 0:
        kwh_change, users_change, peak_power_change = calcuate_stats_change(0, 0, peak_power_float, dailydemand, raw_data, monthlydemand)
        return 0, 0, peak_power, kwh_change, users_change, peak_power_change
    
    else:
        today = today[["dcosId", "cumEnergy_Wh", "vehicle_model"]].groupby("dcosId").first().copy()
        kwh_today_float = today["cumEnergy_Wh"].sum(axis=0) / 1000
        kwh_today = f'{kwh_today_float:,}' + " kWh"
        num_users = len(today)
        kwh_change, users_change, peak_power_change = calcuate_stats_change(kwh_today_float, num_users, peak_power_float, dailydemand, raw_data, monthlydemand)
        return kwh_today, num_users, peak_power, kwh_change, users_change, peak_power_change


# update cumulative stats homepage cards
@dash.callback(
    Output("homepage-cum-kwh", "children"),
    Output("homepage-cum-sessions", "children"),
    Output("homepage-cum-emiles", "children"),
    Output("homepage-cum-kwh-stats", "children"),
    Output("homepage-cum-emiles-stats", "children"),
    Output("homepage-cum-sessions-stats", "children"),
    Input("data_refresh_signal", "data")
)
def update_cum_homepage_cards(n):
    # load data
    raw_data = pickle.loads(redis_client.get("raw_data"))

    # calculate cumulative sessions
    cum_sessions_float = len(raw_data)
    cum_sessions = f'{cum_sessions_float:,}'
    num_weeks = (datetime.today() - datetime(2020, 11, 5)).days // 7
    cum_sessions_stats = [html.I(className="bi bi-ev-station me-1"), f"An average of {round(cum_sessions_float/num_weeks, 1)} sessions per week!"]

    # calculate cumulative energy
    cum_kwh_float = round(raw_data["cumEnergy_Wh"].sum() / 1000, 1)
    cum_kwh_delivered = f'{cum_kwh_float:,}' + " kWh"
    cum_kwh_stats = [html.I(className="bi bi-lightning-charge-fill me-1"), f"Enough energy to power a US home for {round(cum_kwh_float/ 10649, 1)} years!"] # 10649 kWh per home per year conversion

    # calculate cumulative e-miles
    cum_emiles_float = round(raw_data["cumEnergy_Wh"].sum() / 290, 0)
    cum_emiles_delivered = f'{cum_emiles_float:,}' + " Mi" # 290 Wh/mile conversion rate
    cum_emiles_stats = [html.I(className="bi bi-geo-alt-fill me-1"), f"Equivalent to {round(cum_emiles_float / 5810, 1)} round trips from San Francisco to New York City!"] # 5810 miles round trip 
    
    return cum_kwh_delivered, cum_sessions, cum_emiles_delivered, cum_kwh_stats, cum_emiles_stats, cum_sessions_stats

