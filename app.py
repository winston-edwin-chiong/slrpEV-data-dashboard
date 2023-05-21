import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd 
import pickle
from plotting import plottingfunctions as pltf
from tasks.schedule import redis_client 
from dash import html, dcc
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta


# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True, use_pages=True)
app.title = "slrpEV Dashboard"


# app layout
app.layout = \
    html.Div([
        dbc.NavbarSimple([
            dbc.Nav([
                dbc.NavItem([dbc.NavLink(f"{page['name']}", href=page["relative_path"])]) for page in dash.page_registry.values()
            ])
        ],
        brand="slrpEV Dashboard",
        brand_href="/",
        brand_external_link=True,
        fluid=True,
        sticky="top",
        expand="lg"
        ),
        dash.page_container,
    ])

# app layout
app.layout = \
    html.Div([
        # --> Navbar <-- #
        dbc.Navbar([
            dbc.Container([
                html.A([
                    dbc.Row([
                        dbc.Col([
                            html.Img(src="/assets/images/ChartLogo.png", height="40px", className="me-2")
                        ]),
                    ])
                ], href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse([
                    dbc.Nav([
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-house px-1"),
                            dbc.NavLink("Home", href="/", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-graph-up px-1"),
                            dbc.NavLink("Alltime", href="/alltime", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-table px-1"),
                            dbc.NavLink("Datatable", href="/data", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-calendar-event px-1"),
                            dbc.NavLink("Today", href="/today", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-info-circle px-1"),
                            dbc.NavLink("About", href="/about", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                    ], horizontal="center")
                ], id="navbar-collapse", is_open=False, navbar=True)
            ], className="navbar-container ms-2 me-2", fluid=True)
        ], className="py-2 nav-fill w-100 border-start-0 border-end-0", sticky="top", expand="lg"),
        # --> <---#

        # --> Page Content <-- #
        dash.page_container,
        # --> <-- #
    ])

# callback for toggling the collpase on small screens 
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open")
)
def toggle_navbar_collapse(n, is_open):
    if n: 
        return not is_open 
    return is_open 

# jump to present button
@app.callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks"),
)
def jump_to_present(button_press):
    return get_last_days_datetime(7), get_last_days_datetime(-1)


@app.callback(
    Output("daily_time_series", "figure"),
    Input("data_refresh_signal", "data"),
    Input("toggle_yesterday", "value")
)
def display_daily_time_series(signal, yesterday):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessionTimeSeries.plot_daily_time_series(data)
    # plot yesterday's time series
    if yesterday:
        fivemindemand = pickle.loads(redis_client.get("fivemindemand"))
        fig = pltf.PlotDailySessionTimeSeries.plot_yesterday(fig, fivemindemand)
    return fig


@app.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("data_refresh_signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessionEnergyBreakdown.plot_daily_energy_breakdown(data)
    return fig


@app.callback(
    Output("cumulative_energy_delivered", "figure"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("data_refresh_signal", "data")
)
def display_cumulative_energy_figure(start_date, end_date, signal):
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # plot figure
    fig = pltf.PlotCumulativeEnergyDelivered.plot_cumulative_energy_delivered(
        data, start_date, end_date)
    return fig


@app.callback(
    Output("time_series_plot", "figure"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("toggle_forecasts", "value"),
    Input("data_refresh_signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, data_signal,):
    # load data
    data = pickle.loads(redis_client.get(granularity))
    # plot main time series
    fig = pltf.PlotMainTimeSeries.plot_main_time_series(
        data, granularity, quantity, start_date, end_date)
    
    # plot predictions (if supported)
    if forecasts and granularity != "fivemindemand" and granularity != "monthlydemand":
        forecast_df = prediction_to_run(granularity)
        fig = pltf.PlotForecasts.plot_forecasts(fig, forecast_df, quantity, granularity)

    return fig


@app.callback(
    Output("day_histogram", "figure"),
    Output("hour_histogram", "figure"),
    Input("time_series_plot", "hoverData"),
    State("quantity_picker", "value"),
    State("dataframe_picker", "value"),
    prevent_initial_call=True
)
def display_histogram_hover(hoverData, quantity, granularity):

    # place holder for no hover
    if hoverData is None:
        return dash.no_update, dash.no_update

    # load data
    hourlydemand = pickle.loads(redis_client.get("hourlydemand"))
    dailydemand = pickle.loads(redis_client.get("dailydemand"))

    # extract hour and day 
    if hoverData["points"][0]["curveNumber"] == 0:
        day = hoverData["points"][0]["customdata"][0] 
        hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))
    elif hoverData["points"][0]["curveNumber"] == 1:
        day = pd.to_datetime(hoverData["points"][0]["x"]).day_name()
        hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))
    
    # create hover histograms
    if granularity == "dailydemand":
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        return day_hist, pltf.PlotHoverHistogram.empty_histogram_figure()
    
    elif granularity == "monthlydemand":
        return pltf.PlotHoverHistogram.empty_histogram_figure(), pltf.PlotHoverHistogram.empty_histogram_figure()
    
    else:
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        hour_hist = pltf.PlotHoverHistogram.plot_hour_hover_histogram(hourlydemand, quantity, hour)
        return day_hist, hour_hist


@app.callback(
    Output("num_sessions_user", "children"),
    Output("avg_duration_user", "children"),
    Output("freq_connect_time_user", "children"),
    Output("total_nrg_consumed_user", "children"),
    Input("daily_time_series", "hoverData"),
    prevent_initial_call=True
)
def display_user_hover(hoverData):
    # place holder for no hover
    if hoverData is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # get user ID
    userId = int(hoverData["points"][0]["customdata"][2])
    # get user hover data
    num_sessions, avg_duration, freq_connect, total_nrg = pltf.GetUserHoverData.get_user_hover_data(
        data, userId)
    
    text = (
        f"User has been here {num_sessions} times!", 
        f"User charges on average {avg_duration} hours!", 
        f"User usually charges: {freq_connect}", 
        f"User has consumed {total_nrg} kWh to date!"
    )

    return text

@app.callback(
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


@app.callback(
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


# --> Interval Components <-- #

@app.callback(
    Output("data_refresh_signal", "data"),
    Output("last_updated_timer", "children"),
    Input("data_refresh_interval_component", "n_intervals"),
)
def data_refresh_interval(n):
    '''
    This callback polls the Redis database at regular intervals. 
    '''
    # update data refresh timestamp
    last_updated = redis_client.get('last_updated_time').decode("utf-8")
    return n, f"Data last updated at {last_updated}."


@app.callback(
    Output("CV_signal", "data"),
    Output("last_validated_timer", "children"),
    Input("CV_interval_component", "n_intervals"),
)
def CV_interval(n):
    '''
    This callback polls the Redis database at regular intervals. 
    '''
    # update CV timestamp 
    last_validated = redis_client.get("last_validated_time").decode("utf-8")
    return n, f"Parameters last validated {last_validated}." 

# --> <-- #


# --> Helper Functions <-- #

def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


def prediction_to_run(granularity):
    if granularity == "fivemindemand":
        return # not yet supported 
    elif granularity == "hourlydemand":
        return pickle.loads(redis_client.get("hourly_forecasts"))
    elif granularity == "dailydemand":
        return pickle.loads(redis_client.get("daily_forecasts"))
    elif granularity == "monthlydemand":
        return # not yet supported 

# --> <-- #


# running the app
if __name__ == '__main__':
    app.run_server(debug=True)
