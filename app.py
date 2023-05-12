import dash
import dash_bootstrap_components as dbc
import pandas as pd 
import pickle
from plotting import PlotMainTimeSeries, PlotDailySessionTimeSeries, PlotDailySessionEnergyBreakdown, PlotCumulativeEnergyDelivered, GetUserHoverData, PlotForecasts, PlotHoverHistogram
from tasks.schedule import redis_client 
from dash import html, dcc
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta


# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True, use_pages=True)
app.title = "slrpEV Dashboard"

# app layout
app.layout = html.Div([
	html.H1("slrpEV Analytics Dashboard"),

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

	dash.page_container
])


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
    fig = PlotDailySessionTimeSeries.plot_daily_time_series(data)
    # plot yesterday's time series
    if yesterday:
        fivemindemand = pickle.loads(redis_client.get("fivemindemand"))
        fig = PlotDailySessionTimeSeries.plot_yesterday(fig, fivemindemand)
    return fig


@app.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("data_refresh_signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = PlotDailySessionEnergyBreakdown.plot_daily_energy_breakdown(data)
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
    fig = PlotCumulativeEnergyDelivered.plot_cumulative_energy_delivered(
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
    fig = PlotMainTimeSeries.plot_main_time_series(
        data, granularity, quantity, start_date, end_date)
    
    # plot predictions (if supported)
    if forecasts and granularity != "fivemindemand" and granularity != "monthlydemand":
        forecast_df = prediction_to_run(granularity)
        fig = PlotForecasts.plot_forecasts(fig, forecast_df, quantity, granularity)

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
        day_hist = PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        return day_hist, PlotHoverHistogram.empty_histogram_figure()
    
    elif granularity == "monthlydemand":
        return PlotHoverHistogram.empty_histogram_figure(), PlotHoverHistogram.empty_histogram_figure()
    
    else:
        day_hist = PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        hour_hist = PlotHoverHistogram.plot_hour_hover_histogram(hourlydemand, quantity, hour)
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
    num_sessions, avg_duration, freq_connect, total_nrg = GetUserHoverData.get_user_hover_data(
        data, userId)
    
    text = (
        f"User has been here {num_sessions} times!", 
        f"User charges on average {avg_duration} hours!", 
        f"User usually charges: {freq_connect}", 
        f"User has consumed {total_nrg} kWh to date!"
    )

    return text

@app.callback(
    Output("homepage_kwh", "children"),
    Output("homepage_users", "children"),
    Output("homepage_peak_power", "children"),
    Input("data_refresh_signal", "data"),
)
def update_homepage_cards(n):
    # load data
    today = pickle.loads(redis_client.get("todays_sessions"))
    monthlydemand = pickle.loads(redis_client.get("monthlydemand"))
    monthlydemand = monthlydemand.loc[monthlydemand.index >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)]

    if len(today) == 0:
        return 0, 0, str(monthlydemand["peak_power_W"][0]) + " W"
    else:
        today = today[["dcosId", "cumEnergy_Wh", "vehicle_model"]].groupby("dcosId").first().copy()
        kwh_today = today["cumEnergy_Wh"].sum(axis=0) / 1000
        num_users = len(today)
        return str(kwh_today) + " kWh", num_users, str(monthlydemand["peak_power_W"][0]) + " W"  


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


## Helper Functions
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


# running the app
if __name__ == '__main__':
    app.run_server(debug=True)
