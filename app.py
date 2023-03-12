import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
from app_utils import PlotMainTimeSeries
from app_utils import get_last_days_datetime, PlotMainTimeSeries, PlotDailySessionTimeSeries, PlotDailySessionEnergyBreakdown
from layout.tab_one import tab_one_layout
from layout.tab_two import tab_two_layout
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from flask_caching import Cache

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': "cache/",
    'CACHE_THRESHOLD': 6
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
    Input("signal", "data"),
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
    Input("signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = update_data().get("dataframes")
    data = data.get("todays_sessions")
    # plot figure
    fig = PlotDailySessionEnergyBreakdown.plot_daily_energy_breakdown(data)
    return fig





@app.callback(
    Output("time_series_plot", "figure"),
    Output("current_df", "data"),
    Output("last_updated_timer", "children"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("toggle_predictions", "value"),
    Input("signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, predictions, signal):
    # load data
    data = update_data().get("dataframes")
    df = data.get(granularity)

    last_updated = update_data().get('last_updated_time')

    # plot main time series
    fig = PlotMainTimeSeries.plot_main_time_series(df, granularity, quantity, start_date, end_date)

    jsonified_df = df.to_json(orient='split')

    return fig, jsonified_df, f"Data last updated at {last_updated}."


@app.callback(
    Output("signal", "data"),
    Input("interval_component", "n_intervals"),
    prevent_initial_callback=True
)
def interval_thing(n):
    update_data()  # expensive process
    return n


@cache.memoize(timeout=3600)  # refresh every hour
def update_data() -> dict:

    print("Fetching data...")
    raw_data = FetchData.scan_save_all_records()

    print("Cleaning data...")
    cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

    print("Done!")
    return {"dataframes":cleaned_dataframes, "last_updated_time":datetime.now().strftime('%H:%M:%S')}


# running the app
if __name__ == '__main__':
    app.run(debug=True)
