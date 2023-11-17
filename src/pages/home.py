import dash
import dash_bootstrap_components as dbc
import pandas as pd
import pytz
import dash_mantine_components as dmc
from dash.dependencies import Output, Input, State
from plotting import plottingfunctions as pltf
from dash import html, dcc
from datetime import datetime, timedelta
from db.utils import db

r = db.get_redis_connection()

### --> Helper Functions <-- ###

def calculate_pct_change(after, before):
    '''
    Calculate the percent change between two numbers.
    If 'before' is zero, this function returns 100, and returns 0 if both
    'after' and 'before' are zero. 
    '''
    # both are zero case
    if not after and not before:
        return 0
    # before is zero case
    elif not before:
        return 100
    # now is zero & now and before are non-zero case
    return (after - before) * 100 / before


def calcuate_stats_change(kwh_today, num_users, peak_power, dailydemand, raw_data, monthlydemand):

    def get_icon_and_color(change):
        """
        Returns an arrow icon and color corresponding to a change. Green up for increase, grey sideways for equal, red down for decrease. 
        """
        if change > 0:
            return "bi bi-arrow-up me-1", "#58c21e"
        elif change < 0:
            return "bi bi-arrow-down me-1", "#c21e58"
        else:
            return "bi bi-arrow-right me-1", "#55595c"

    # calculate daily kWh change
    yesterday = pd.to_datetime(datetime.now(pytz.timezone('US/Pacific')) - timedelta(days=1)).strftime("%Y-%m-%d")
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
                className=get_icon_and_color(kwh_change)[0],
                style={"color": get_icon_and_color(kwh_change)[1]}
            ),
            f"{kwh_change:+.0f}% since yesterday!" if kwh_change else "No change since yesterday!"
        ],
        [
            html.I(
                className=get_icon_and_color(num_users_change)[0],
                style={"color": get_icon_and_color(num_users_change)[1]}
            ),
            f"{num_users_change:+} users since yesterday!" if num_users_change else "No change since yesterday!"
        ],
        [
            html.I(
                className=get_icon_and_color(peak_power_change)[0],
                style={"color": get_icon_and_color(peak_power_change)[1]} 
            ),
            f"{peak_power_change:+.1f}% since last month!" if peak_power_change else "No change since last month!"
        ],
    )

# --> <-- #


dash.register_page(__name__, path="/")

layout = \
    html.Div([
        html.H1(id="date-title", className="d-flex justify-content-center text-center my-5 mx-2 text-bolder"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cumulative Energy Delivered", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.H2(id="homepage-cum-kwh"),
                                html.Div([
                                    html.I(className="bi bi-lightning-charge-fill me-1", style={"color": "#FCC01E"}),
                                    html.Span(id="homepage-cum-kwh-stats")
                                ], className="my-3")
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Energy Delivered Today", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.H2(id="homepage-kwh"),
                                html.Div(className="my-3", id="homepage-kwh-change")
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cumulative E-Miles Delivered", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.H2(id="homepage-cum-emiles"),
                                html.Div([
                                    html.I(className="bi bi-geo-alt-fill me-1", style={"color": "#3CDFFF"}),
                                    html.Span(id="homepage-cum-emiles-stats")
                                ], className="my-3")
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Users Today", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.H2(id="homepage-users"),
                                html.Div(className="my-3", id="homepage-users-change")
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cumulative Number of Sessions", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.Div([
                                    html.H2(id="homepage-cum-sessions", className="m-0"),
                                    html.Div(id="homepage-sessions-split", className="d-flex flex-column align-items-center")
                                ], className="d-flex flex-row align-items-center justify-content-center"),
                                html.Div([
                                    html.I(className="bi bi-calendar-week me-1", style={"color": "#000000"}),
                                    html.Span(id="homepage-cum-sessions-stats")
                                ], className="my-3") 
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Peak Power This Month", className="card-title"),
                        ]),
                        dcc.Loading(
                            dbc.CardBody([
                                html.H2(id="homepage-peak-power"),
                                html.Div(className="my-3", id="homepage-peak-power-change")
                            ]),
                        type="circle")
                    ], className="h-100 rounded shadow text-center"),
                ], className="col-md-6 col-sm-12 col-12"),
            ], className="row-cols-1 rows-cols-sm-2 gx-4 gy-4"),
        ], className="my-5 animate__animated animate__fadeIn")
    ])


# update daily and monthly stats homepage cards
@dash.callback(
    Output("homepage-kwh", "children"),
    Output("homepage-users", "children"),
    Output("homepage-peak-power", "children"),
    Output("homepage-kwh-change", "children"),
    Output("homepage-users-change", "children"),
    Output("homepage-peak-power-change", "children"),
    Input("data-refresh-signal", "data"),
)
def update_today_homepage_cards(n):
    # load data
    today, monthlydemand, dailydemand, raw_data = db.get_multiple_df(r, ["todays_sessions", "monthlydemand", "dailydemand", "raw_data"])

    # filter data to just this month
    thismonthdemand = monthlydemand.iloc[[-1]]

    # extract peak power, convert to kW
    peak_power_float = thismonthdemand["peak_power_W"][0] / 1000
    peak_power = f'{peak_power_float:,} kW'

    # workaround for length of NoneType error (no sessions today)
    if len(today) == 0:
        kwh_change, users_change, peak_power_change = calcuate_stats_change(0, 0, peak_power_float, dailydemand, raw_data, monthlydemand)

        return 0, 0, peak_power, kwh_change, users_change, peak_power_change

    today = today[["dcosId", "cumEnergy_Wh", "vehicle_model"]].groupby("dcosId").first().copy()
    kwh_today_float = today["cumEnergy_Wh"].sum(axis=0) / 1000

    kwh_today = f'{kwh_today_float:,} kWh'
    num_users = len(today)

    kwh_change, users_change, peak_power_change = calcuate_stats_change(kwh_today_float, num_users, peak_power_float, dailydemand, raw_data, monthlydemand)

    return kwh_today, num_users, peak_power, kwh_change, users_change, peak_power_change


# update cumulative stats homepage cards
@dash.callback(
    Output("homepage-cum-kwh", "children"),
    Output("homepage-cum-sessions", "children"),
    Output("homepage-sessions-split", "children"),
    Output("homepage-cum-emiles", "children"),
    Output("homepage-cum-kwh-stats", "children"),
    Output("homepage-cum-emiles-stats", "children"),
    Output("homepage-cum-sessions-stats", "children"),
    Input("data-refresh-signal", "data")
)
def update_cum_homepage_cards(n):
    # load data
    raw_data = db.get_df(r, "raw_data_subset")

    # calculate cumulative sessions
    cum_sessions_float = raw_data.shape[0]
    cum_sessions = f'{cum_sessions_float:,}'
    # calculate regular vs. schedule split by %
    cum_sessions_percent_reg = f'{(raw_data[raw_data["choice"] == "REGULAR"].shape[0] / cum_sessions_float):.1%}'
    cum_sessions_percent_sched = f'{(raw_data[raw_data["choice"] == "SCHEDULED"].shape[0] /cum_sessions_float):.1%}'
    sessions_split = [
        dmc.RingProgress(
            sections=[
                {
                    "tooltip": f'Regular - {cum_sessions_percent_reg} ({raw_data[raw_data["choice"] == "REGULAR"].shape[0]})', 
                    "value": 100 * raw_data[raw_data["choice"] == "REGULAR"].shape[0] / cum_sessions_float, 
                    "color": "#003262"},
                {
                    "tooltip": f'Scheduled - {cum_sessions_percent_sched} ({raw_data[raw_data["choice"] == "SCHEDULED"].shape[0]})', 
                    "value": 100 * raw_data[raw_data["choice"] == "SCHEDULED"].shape[0] / cum_sessions_float, 
                    "color": "#FDB515"}
            ],
            size=45,
            thickness=8
        ),
        ]

    num_weeks = (datetime.today() - datetime(2020, 11, 5)).days // 7
    cum_sessions_stats = f"An average of {cum_sessions_float/num_weeks:.1f} sessions per week!"

    # calculate cumulative energy
    cum_kwh_float = raw_data["cumEnergy_Wh"].sum() / 1000
    cum_kwh_delivered = f'{cum_kwh_float:,.1f} kWh'
    cum_kwh_stats = f"Enough energy to power a US home for {cum_kwh_float/ 10649:.1f} years!" # 10649 kWh per home per year conversion

    # calculate cumulative e-miles
    cum_emiles_float = raw_data["cumEnergy_Wh"].sum() / 290
    cum_emiles_delivered = f'{cum_emiles_float:,.0f} Mi' # 290 Wh/mile conversion rate
    cum_emiles_stats = f"Equivalent to {(cum_emiles_float / 5810):.1f} round trips from San Francisco to New York City!" # 5810 miles round trip

    return cum_kwh_delivered, cum_sessions, sessions_split, cum_emiles_delivered, cum_kwh_stats, cum_emiles_stats, cum_sessions_stats


# update date title
@dash.callback(
    Output("date-title", "children"),
    Input("data-refresh-signal", "data")
)
def update_date_title(n):
    return datetime.now(pytz.timezone('US/Pacific')).strftime("%A, %B %d, %Y")   
