import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
import pandas as pd 
from app_utils import PlotMainTimeSeries, PlotDailySessionTimeSeries, PlotDailySessionEnergyBreakdown, PlotCumulativeEnergyDelivered, GetUserHoverData
from layout.tab_one import tab_one_layout
from layout.tab_two import tab_two_layout
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
from flask_caching import Cache


# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': "cache/",
    'CACHE_THRESHOLD': 20
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

# app layout
app.layout = html.Div([
    dcc.Tabs([
        tab_one_layout(),
        tab_two_layout()
    ])
])


# jump to present button
@app.callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks")
)
def jump_to_present(button_press):
    return get_last_days_datetime(7), get_last_days_datetime(-1)


@app.callback(
    Output("daily_time_series", "figure"),
    Input("quantity_picker", "value"),
    Input("data_refresh_signal", "data"),
)
def display_daily_time_series(quantity, signal):
    # load data
    data = update_data().get("dataframes")
    data = data.get("todays_sessions")
    # plot figure
    fig = PlotDailySessionTimeSeries.plot_daily_time_series(data)
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
    Output("last_updated_timer", "children"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("toggle_forecasts", "value"),
    Input("data_refresh_signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, signal):
    # load data
    data = update_data().get("dataframes")
    data = data.get(granularity)
    # update refresh timestamp
    last_updated = update_data().get('last_updated_time')
    # plot main time series
    fig = PlotMainTimeSeries.plot_main_time_series(
        data, granularity, quantity, start_date, end_date)
    
    # plot predictions
    if forecasts:
        forecasts = get_forecast(granularity)


    return fig, f"Data last updated at {last_updated}."


@app.callback(
    Output("num_sessions_user", "children", allow_duplicate=True),
    Output("avg_duration_user", "children"),
    Output("freq_connect_time_user", "children"),
    Output("total_nrg_consumed_user", "children"),
    Input("daily_time_series", "hoverData"),
    prevent_initial_callback=True
)
def display_user_hover(hoverData):
    # place holder for no hover
    if hoverData is None:
        return "# of Sessions by User", "Avg. Stay Duration", "Frequent Connect Time", "Total Energy Consumed by User"
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
    Input("data_refresh_interval_component", "n_intervals"),
)
def data_refresh_interval(n):
    update_data()  # expensive process
    return n


@app.callback(
    Output("CV_signal", "data"),
    Output("last_validated_timer", "children"),
    Input("CV_interval_component", "n_intervals"),
)
def CV_interval(n):
    params = update_ml_parameters()
    # calculate new models with ML parameters
    return n, f"Parameters last validated {params['last_validated_time']}." #, new_models dict


@app.callback(
        Output(),
        Input("CV_signal", "data")
)
def recreate_models():
    pass


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
    # load data 
    data = update_data().get("dataframes").get("hourlydemand")
    # get kNN parameters
    best_params = HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data) 
    print(best_params)
    return {"best_params": best_params, "last_validated_time": datetime.now().strftime('%m/%d/%y %H:%M:%S')}


@cache.memoize()
def update_hourly_forecasts():
    # load data 
    data = update_data().get("dataframes").get("hourlydemand")
    # get optimal parameters
    params = update_ml_parameters().get("best_params")
    # get hourly forecast 
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, params)
    return forecasts



## Helper Functions
def get_forecast(granularity):
    if granularity == "hourlydemand":
        forecasts = update_hourly_forecasts()
    elif granularity == "dailydemand":
        pass
    elif granularity == "monthlydemand":
        pass

def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


# running the app
if __name__ == '__main__':
    app.run(debug=True)
