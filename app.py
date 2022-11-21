import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import pandas as pd
import time
import plotly.graph_objects as go

from app_utils import query_date_df, resample_df, plot_time_series

# load data 
fiveminenergydemand = pd.read_csv("data/5minenergydemand.csv")
fiveminpowerdemand = pd.read_csv("data/5minpowerdemand.csv")

fiveminenergydemand.set_index("time", inplace=True)
fiveminenergydemand.index = pd.to_datetime(fiveminenergydemand.index)
fiveminpowerdemand.set_index("time", inplace=True)
fiveminpowerdemand.index = pd.to_datetime(fiveminpowerdemand.index)

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

image_path = "assets/slrpEVlogo.png"

# app layout
app.layout = html.Div([
    html.Div([
        dcc.DatePickerRange(
            id = "date_time_picker",
            clearable=True,
            start_date_placeholder_text="mm/dd/yyyy",
            end_date_placeholder_text="mm/dd/yyyy",
            with_portal = False
        ),
        dcc.Dropdown(
            id = "granularity_picker",
            options=[
                {'label':'5-Min', 'value':'5-Min'},
                {'label':'Hourly', 'value':'Hourly'},
                {'label':'Daily', 'value':"Daily"},
                {'label':'Monthly', 'value':'Monthly'}
            ],
            value = '5-Min', # default value
            clearable=False,
            searchable=False
        ),
        dcc.Dropdown(
            id = "quantity_picker",
            options=[
                {'label':'Energy Demand', 'value':'Energy Demand'},
                {'label':'Power Demand', 'value':'Power Demand'},
                {'label':'Peak Power Demand', 'value':'Peak Power Demand'}
            ],
            value = 'Energy Demand', # default value
            clearable=False,
            searchable=False
        )
    ]),
    html.Div([
        dcc.Graph(
            id = "time_series_plot",
        )
    ]),
    dcc.Store(id='current_df') # stores current dataframe
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
    
    if quantity == "Energy Demand":
        df = fiveminenergydemand

    elif quantity == "Power Demand":
        df = fiveminpowerdemand

    elif quantity == "Peak Power Demand":
        df = fiveminpowerdemand
    
    df = query_date_df(df, start_date, end_date)
    df = resample_df(df, granularity, peak=(True if "Peak" in quantity else False))

    fig = plot_time_series(df, granularity, quantity)
    jsonified_df = df.to_json(orient='split')
    return fig, jsonified_df
        
# running the app
if __name__ == '__main__':
    app.run(debug=True)
