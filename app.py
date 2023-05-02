import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
import pandas as pd 
from plotting import PlotMainTimeSeries, PlotDailySessionTimeSeries, PlotDailySessionEnergyBreakdown, PlotCumulativeEnergyDelivered, GetUserHoverData, PlotForecasts, PlotHoverHistogram
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator
from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from flask_caching import Cache
from celery import Celery

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True, use_pages=True)
app.title = "slrpEV Dashboard"
server = app.server

# Celery process 

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': "redis://localhost:6360"
}
cache = Cache(app.server, config=CACHE_CONFIG)

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
    data = update_data().get("dataframes")
    data = data.get("todays_sessions")
    # plot figure
    fig = PlotDailySessionTimeSeries.plot_daily_time_series(data)
    # plot yesterday's time series
    if yesterday:
        fivemindemand = update_data().get("dataframes").get("fivemindemand")
        fig = PlotDailySessionTimeSeries.plot_yesterday(fig, fivemindemand)
    return fig


@app.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("data_refresh_signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = update_data().get("dataframes")
    data = data.get("todays_sessions")
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
    data = update_data().get("dataframes").get("raw_data")
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
    Input("hourly_forecast_signal", "data"),
    Input("daily_forecast_signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, data_signal, hourly_forecast_signal, daily_forecast_signal):
    # load data
    data = update_data().get("dataframes")
    data = data.get(granularity)
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
    # load data
    data = update_data().get("dataframes")
    hourlydemand = data.get("hourlydemand")
    dailydemand = data.get("dailydemand")
    day = hoverData["points"][0]["customdata"][0] 
    hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))

    # place holder for no hover
    if hoverData is None:
        return dash.no_update, dash.no_update
    
    elif granularity == "dailydemand":
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
    data = update_data().get("dataframes").get("raw_data")
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
    Output("data_refresh_signal", "data"),
    Output("last_updated_timer", "children"),
    Input("data_refresh_interval_component", "n_intervals"),
)
def data_refresh_interval(n):
    update_data() # expensive process
    # update refresh timestamp
    last_updated = update_data().get('last_updated_time')
    return n, f"Data last updated at {last_updated}."


@app.callback(
    Output("CV_signal", "data"),
    Output("last_validated_timer", "children"),
    Input("CV_interval_component", "n_intervals"),
)
def CV_interval(n):
    params = update_ml_parameters() # expensive process
    # calculate new models with ML parameters
    return n, f"Parameters last validated {params['last_validated_time']}." 


@app.callback(
    Output("hourly_forecast_signal", "data"),
    Input("hourly_forecast_interval_component", "n_intervals"),
    Input("data_refresh_signal", "data"),
)
def hourly_forecast_interval(n, signal):
    forecast_hourly()
    return n


@app.callback(
    Output("daily_forecast_signal", "data"),
    Input("daily_forecast_interval_component", "n_intervals"),
    Input("data_refresh_signal", "data"),
)
def daily_forecast_interval(n, signal):
    forecast_daily()
    return n


## Cached functions 
@cache.memoize(timeout=3600)  # refresh every hour
def update_data() -> dict:

    print("Fetching data...")
    raw_data = FetchData.scan_save_all_records()

    print("Cleaning data...")
    cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

    print("Done!")
    return {"dataframes": cleaned_dataframes, "last_updated_time": datetime.now().strftime('%H:%M:%S')}


@cache.memoize(timeout=1209600) # retrain every two weeks
def update_ml_parameters() -> dict:
    # get parameters
    hard_coded_params_hourly = {'energy_demand_kWh': 
                                    {'best_depth': 57, 'best_n_neighbors': 25},
                                'peak_power_W': 
                                    {'best_depth': 57, 'best_n_neighbors': 23},
                                'avg_power_demand_W': 
                                    {'best_depth': 57, 'best_n_neighbors': 25}
                                }
    hard_coded_params_daily = {'energy_demand_kWh': 
                                    {'order': (2, 0, 1), 'seasonal_order': (0, 1, 2, 7)},
                                'peak_power_W': 
                                    {'order': (1, 0, 0), 'seasonal_order': (0, 1, 2, 7)},
                                'avg_power_demand_W': 
                                    {'order': (2, 0, 1), 'seasonal_order': (0, 1, 2, 7)}
                                }
    best_params = {}
    best_params["hourlydemand"] = hard_coded_params_hourly
    best_params["dailydemand"] = hard_coded_params_daily

    # clear predictions
    CreateHourlyForecasts.save_empty_prediction_df()
    CreateDailyForecasts.save_empty_prediction_df()
    
    return {"best_params": best_params, "last_validated_time": datetime.now().strftime('%m/%d/%y %H:%M:%S')}


### --> NOT USED RIGHT NOW BECAUSE IDK HOW TO SCHEDULE IT IN THE BACKGROUND <-- ###
@cache.memoize(timeout=1209600)
def update_hourly_parameters(data):
    return HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data) 


@cache.memoize(timeout=1209600)
def update_daily_parameters(data):
    return DailyCrossValidator.cross_validate(data)
### --> NOT USED RIGHT NOW BECAUSE IDK HOW TO SCHEDULE IT IN THE BACKGROUND <-- ###


@cache.memoize(timeout=3600) #refresh every hour
def forecast_hourly():
    data = update_data().get("dataframes").get("hourlydemand")
    params = update_ml_parameters().get("best_params")
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, params)
    return forecasts   


@cache.memoize(timeout=86400) #refresh every day 
def forecast_daily():
    data = update_data().get("dataframes").get("dailydemand")
    params = update_ml_parameters().get("best_params")
    forecasts = CreateDailyForecasts.run_daily_forecast(data, params)
    return forecasts


## Helper Functions
def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


def prediction_to_run(granularity):
    if granularity == "fivemindemand":
        return # not yet supported 
    elif granularity == "hourlydemand":
        return forecast_hourly()
    elif granularity == "dailydemand":
        return forecast_daily()
    elif granularity == "monthlydemand":
        return # not yet supported 


# running the app
if __name__ == '__main__':
    app.run_server(debug=True)
