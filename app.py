import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import pandas as pd
import time
import plotly.graph_objects as go

from app_utils import query_date_df

# load data 
hourlyenergydemand = pd.read_csv("data/hourlyenergydemand.csv").set_index("time")
fiveminpowerdemand = pd.read_csv("data/5minpowerdemand.csv").set_index("time")

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
            with_portal=True
        ),
        dcc.Dropdown(
            id = "granularity_picker",
            options=[
                {'label':'5-Min', 'value':'5minpowerdemand'},
                {'label':'Hourly', 'value':'hourlyenergydemand'}
            ],
            value = '5minpowerdemand', # default value
            clearable=False,
            searchable=False
        ),
        dcc.Dropdown(
            id = "unit_picker",
            options=[
                {'label':'Energy Demand', 'value':'energydemand'},
                {'label':'Power Demand', 'value':'powerdemand'},
                {'label':'Peak Power Demand', 'value':'peakpowerdemand'}
            ],
            value = 'energydemand', # default value
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
    Input("unit_picker", "value"),
    Input("date_time_picker", "start_date"),
    Input("date_time_picker", "end_date"),
    )
def display_main_figure(granularity, start_date, end_date):
    fig = go.Figure()

    if granularity == '5minpowerdemand':
        df = query_date_df(fiveminpowerdemand, start_date=start_date, end_date=end_date)
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df["power_demand"], 
                name="Daily Peak Power", 
                hovertext=df["day"]))
        fig.update_layout(
            title="5-Min Power Demand",
            xaxis_title="Time",
            yaxis_title="Peak Demand (W)")

    elif granularity == 'hourlyenergydemand':
        df = query_date_df(hourlyenergydemand, start_date=start_date, end_date=end_date)
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df["energy_demand"], 
                name="Hourly Energy Demand",
                hovertext=df["day"]))
        fig.update_layout(
            title="Hourly Energy Demand", 
            xaxis_title="Time", 
            yaxis_title="Energy Demand (kWh)")

    return fig, df.to_json(orient='split')


# running the app
if __name__ == '__main__':
    app.run(debug=True)
