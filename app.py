import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
import dash_daq as daq
import pandas as pd
from datetime import datetime
from app_utils import LoadDataFrames, PlotDataFrame, PlotPredictions, get_last_days_datetime
from layout.tab_one import tab_one_layout
from layout.tab_two import tab_two_layout
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from flask_caching import Cache
import plotly.express as px

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': "cache/"
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

image_path = "assets/slrpEVlogo.png"

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
    return get_last_days_datetime(7), get_last_days_datetime(-1)  # placeholder, no new data yet


# daily time series
# TODO: Put this somewhere else. 
@app.callback(
    Output("daily_time_series", "figure"),
    Input("quantity_picker", "value"),
    Input("signal", "data"),
)
def display_daily_time_series(quantity, signal):
    data = update_data()[0]
    data = data["session"]
    if data.empty:
        return # TODO: Return a placeholder, rather than null; yesterday's data?
    data["userId"] = data["userId"].astype(str)
    fig = px.bar(data, x=data["Time"], y=data["Power (W)"], color=data["userId"], hover_data=["vehicle_model"])
    fig.update_yaxes(showgrid=False)
    return fig 

# vehicle pie chart
# TODO: Put this somewhere else. 
@app.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("signal", "data"),
)
def display_vehicle_pie_chart(signal):
    data = update_data()[0]
    data = data["session"]
    if data.empty:
        return # TODO: Return a placeholder, rather than null; yesterday's data?
    car_pie = data[["dcosId", "vehicle_model"]].groupby("dcosId").first()
    car_pie["vehicle_model"].value_counts()
    fig = px.pie(values = car_pie["vehicle_model"].value_counts(), names=car_pie["vehicle_model"].value_counts().index)
    return fig 

# calendar and granularity dropdown callback function  
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

    # load dataframes, get specific dataframe
    result = update_data()
    dataframes = result[0]
    df = dataframes.get(granularity)
 
    # plot dataframe
    fig = PlotDataFrame(df, granularity, quantity, start_date, end_date).plot()

    if predictions:
        PlotPredictions(fig, granularity, quantity, start_date, end_date).add_predictions()

    jsonified_df = df.to_json(orient='split')

    return fig, jsonified_df, f"Data last updated at {result[1]}."


@app.callback(
    Output("signal", "data"),
    Input("interval_component", "n_intervals"),
    prevent_initial_callback = True
)
def interval_thing(n):
    update_data() # expensive process 
    return n

@cache.memoize(timeout=1200)
def update_data():

    print("Fetching data...")
    raw_data = FetchData.scan_save_all_records()

    print("Cleaning data...")
    cleaned_df = CleanData.clean_save_raw_data(raw_data)

    print("Done!")
    return cleaned_df, datetime.now().strftime('%H:%M:%S')

# running the app
if __name__ == '__main__':
    app.run(debug=True)
