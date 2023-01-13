import dash 
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input
import dash_daq as daq
import pandas as pd
from datetime import datetime
from app_utils import get_last_days_datetime, LoadDataFrames, PlotDataFrame, PlotPredictions
from janitorial.FetchData import FetchData
from janitorial.CleanData import CleanData
from sklearn.pipeline import Pipeline


# load dataframes 
dataframes = LoadDataFrames.load_csv()

# last week's date
seven_days_ago = get_last_days_datetime(7)

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

image_path = "assets/slrpEVlogo.png"

# app layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(
            label="Tab One",
            children=[
                html.Div([
                    dcc.DatePickerRange(
                        id="date_time_picker",
                        clearable=True,
                        start_date=seven_days_ago, # placeholder, no new data yet
                        start_date_placeholder_text="mm/dd/yyyy",
                        end_date_placeholder_text="mm/dd/yyyy",
                        with_portal=False
                    ),
                    dcc.Dropdown(
                        id = "dataframe_picker",
                        options=[
                            {'label':'5-Min', 'value':'fivemindemand'},
                            {'label':'Hourly', 'value':'hourlydemand'},
                            {'label':'Daily', 'value':"dailydemand"},
                            {'label':'Monthly', 'value':'monthlydemand'}
                        ],
                        value='hourlydemand', # default value
                        clearable=False,
                        searchable=False
                    ),
                    dcc.Dropdown(
                        id="quantity_picker",
                        options=[
                            {'label':'Energy Demand', 'value':'energy_demand_kWh'},
                            {'label':'Average Power Demand', 'value':'avg_power_demand_W'},
                            {'label':'Peak Power Demand', 'value':'peak_power_W'}
                        ],
                        value = 'energy_demand_kWh', # default value
                        clearable=False,
                        searchable=False
                    ),
                    html.Button("Jump to Past 7 Days", id="jump_to_present_btn"),
                    daq.ToggleSwitch(label="Toggle Predictions", value=False, id="toggle_predictions")
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
                dcc.Store(id='current_df'), # stores current dataframe
                html.Div([
                    "Rolling 7-Day RMSE:"
                ]),
                html.Div([
                    dcc.Interval(
                        id="interval_component",
                        interval = 20*60*1000,
                        n_intervals=0
                    ),
                    html.Div(
                        id="last_updated_timer"
                    )
                ])
            ]
        ),
        dcc.Tab(
            label="Tab Two",
            children=[

            ]
        )
    ])
])


# jump to present button 
@app.callback(
    Output("date_time_picker", "start_date"),
    Output("date_time_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks")
)
def jump_to_present(button_press):
    return seven_days_ago, None # placeholder, no new data yet


# calendar and granularity dropdown callback function  
@app.callback(
    Output("time_series_plot", "figure"),
    Output("current_df", "data"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_time_picker", "start_date"),
    Input("date_time_picker", "end_date"),
    Input("toggle_predictions", "value")
    )
def display_main_figure(granularity, quantity, start_date, end_date, predictions):
    df = dataframes.get(granularity)
    fig = PlotDataFrame(df, granularity, quantity, start_date, end_date).plot()

    if predictions == True:
        PlotPredictions(fig, granularity, quantity, start_date, end_date).add_predictions()

    jsonified_df = df.to_json(orient='split')

    return fig, jsonified_df

@app.callback(
    Output("last_updated_timer", "children"),
    Input("interval_component", "n_intervals"),
    prevent_initial_call=True
    )
def update_data(n):
    print("Fetching data...")
    FetchData("Sessions2").scan_save_all_records()
    print("Cleaning data...")
    CleanData().clean_raw_data()
    print("Done!")
    return f"Data last updated {datetime.now().strftime('%H:%M:%S')}."


# running the app
if __name__ == '__main__':
    app.run(debug=True)
