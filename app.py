import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import pandas as pd
import time
import plotly.graph_objects as go

from app_utils import query_date_df, plot_time_series, set_index_and_datetime, get_last_days_datetime

# load data, set time column to index, set to datetime
fivemindemand = set_index_and_datetime(pd.read_csv("data/5mindemand.csv"))
hourlydemand = set_index_and_datetime(pd.read_csv("data/hourlydemand.csv"))
dailydemand = set_index_and_datetime(pd.read_csv("data/dailydemand.csv"))
monthlydemand = set_index_and_datetime(pd.read_csv("data/monthlydemand.csv"))

# map dataframes 
dataframes = {
    "5-Min": fivemindemand,
    "Hourly": hourlydemand,
    "Daily": dailydemand,
    "Monthly": monthlydemand
}

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

image_path = "assets/slrpEVlogo.png"

# app layout
app.layout = html.Div([
    html.Div([
        dcc.DatePickerRange(
            id="date_time_picker",
            clearable=True,
            start_date=("08/15/2022" if True else get_last_days_datetime(7)), # placeholder, no new data yet
            start_date_placeholder_text="mm/dd/yyyy",
            end_date_placeholder_text="mm/dd/yyyy",
            with_portal=False
        ),
        dcc.Dropdown(
            id = "granularity_picker",
            options=[
                {'label':'5-Min', 'value':'5-Min'},
                {'label':'Hourly', 'value':'Hourly'},
                {'label':'Daily', 'value':"Daily"},
                {'label':'Monthly', 'value':'Monthly'}
            ],
            value='Hourly', # default value
            clearable=False,
            searchable=False
        ),
        dcc.Dropdown(
            id="quantity_picker",
            options=[
                {'label':'Energy Demand', 'value':'energy_demand'},
                {'label':'Average Power Demand', 'value':'power_demand'},
                {'label':'Peak Power Demand', 'value':'peak_power_demand'}
            ],
            value = 'peak_power_demand', # default value
            clearable=False,
            searchable=False
        )
    ]),
    html.Div([
        dcc.Graph(
            id="time_series_plot",
        )
    ]),
    dcc.Store(id='current_df'), # stores current dataframe
    html.Div([
        "Maybe some useful metrics..."
    ])
])


# calendar and granularity dropdown callback function  
@app.callback(
    Output("time_series_plot", "figure"),
    Output("current_df", "data"),
    Input("granularity_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_time_picker", "start_date"),
    Input("date_time_picker", "end_date"),
    )
def display_main_figure(granularity, quantity, start_date, end_date):
    
    df = dataframes[granularity]

    df = df[[quantity, "day"]]
    
    df = query_date_df(df, start_date, end_date)

    fig = plot_time_series(df, granularity, quantity)
    jsonified_df = df.to_json(orient='split')
    return fig, jsonified_df
        
# running the app
if __name__ == '__main__':
    app.run(debug=True)
