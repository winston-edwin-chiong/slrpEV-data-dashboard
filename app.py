import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
import dash_daq as daq
import pandas as pd
from datetime import datetime
from app_utils import get_last_days_datetime, LoadDataFrames, PlotDataFrame, PlotPredictions
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from flask_caching import Cache
import os


# last week's date
seven_days_ago = get_last_days_datetime(7)


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
        dcc.Tab(
            label="Tab One",
            children=[
                html.Div([
                    dcc.DatePickerRange(
                        id="date_picker",
                        clearable=True,
                        start_date=seven_days_ago,
                        start_date_placeholder_text="mm/dd/yyyy",
                        end_date_placeholder_text="mm/dd/yyyy",
                        with_portal=False
                    ),
                    dcc.Dropdown(
                        id="dataframe_picker",
                        options=[
                            {'label': '5-Min', 'value': 'fivemindemand'},
                            {'label': 'Hourly', 'value': 'hourlydemand'},
                            {'label': 'Daily', 'value': "dailydemand"},
                            {'label': 'Monthly', 'value': 'monthlydemand'}
                        ],
                        value='hourlydemand',  # default value
                        clearable=False,
                        searchable=False
                    ),
                    dcc.Dropdown(
                        id="quantity_picker",
                        options=[
                            {'label': 'Energy Demand', 'value': 'energy_demand_kWh'},
                            {'label': 'Average Power Demand', 'value': 'avg_power_demand_W'},
                            {'label': 'Peak Power Demand', 'value': 'peak_power_W'}
                        ],
                        value='energy_demand_kWh',  # default value
                        clearable=False,
                        searchable=False
                    ),
                    html.Button("Today", id="jump_to_present_btn"),
                    daq.ToggleSwitch(
                        label="Toggle Predictions", 
                        value=False, 
                        id="toggle_predictions", 
                        disabled=True,
                        )
                ]),
                html.Div([
                    dcc.Graph(
                        id="time_series_plot",
                        config={
                            "displaylogo": False,
                            "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                        }
                    )
                ]),
                dcc.Store(id='current_df'),  # stores current dataframe
                html.Div([
                    dcc.Interval(
                        id="interval_component",
                        interval=20 * 60 * 1000,  # update every 20 minutes
                        n_intervals=0
                    ),
                    html.Div(
                        id="last_updated_timer"
                    ),
                ])
            ]
        ),
        dcc.Tab(
            label="Tab Two",
            children=[
                html.Div([
                    dcc.Graph(
                        id="daily_time_series",
                        config={
                            "displaylogo": False,
                            "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                        }
                    )
                ]),
            ]
        )
    ])
])


# jump to present button 
@app.callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks")
)
def jump_to_present(button_press):
    return seven_days_ago, None  # placeholder, no new data yet


# daily time series
@app.callback(
    Output("daily_time_series", "figure"),
    Input("quantity_picker", "value"),
    Input("last_updated_timer", "children")
)
def display_daily_time_series(quantity, last_updated):
    return 

# calendar and granularity dropdown callback function  
@app.callback(
    Output("time_series_plot", "figure"),
    Output("current_df", "data"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("toggle_predictions", "value"),
    Input("last_updated_timer", "children")
)
def display_main_figure(granularity, quantity, start_date, end_date, predictions, last_updated):

    # load dataframes, get specific dataframe
    dataframes = LoadDataFrames.load_csv()
    df = dataframes.get(granularity)

    # plot dataframe
    fig = PlotDataFrame(df, granularity, quantity, start_date, end_date).plot()

    if predictions:
        PlotPredictions(fig, granularity, quantity, start_date, end_date).add_predictions()

    jsonified_df = df.to_json(orient='split')

    return fig, jsonified_df


@app.callback(
    Output("last_updated_timer", "children"),
    Input("interval_component", "n_intervals"),
    prevent_initial_call=False
)
def update_data(n):

    print("Fetching data...")
    FetchData.scan_save_all_records()

    print("Cleaning data...")
    CleanData.clean_save_raw_data()

    print("Done!")
    return f"Data last updated {datetime.now().strftime('%H:%M:%S')}."


# running the app
if __name__ == '__main__':
    app.run(debug=True)
