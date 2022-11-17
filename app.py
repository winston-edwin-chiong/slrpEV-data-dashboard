import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import pandas as pd
import time

import plotly.graph_objects as go

def plot_daily_peak_power(df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x = df.index, y = df["power_demand"] , name = "Daily Peak Power" , hovertext=df["day"])
    )
    fig.update_layout(title = f"Peak Daily Power Demand", xaxis_title = "Time", yaxis_title="Power (W)")
    return fig

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

image_path = "assets/slrpEVlogo.png"

# app layout
app.layout = html.Div([
     html.Img(
        src=image_path, 
        height="100px", 
        style={'display': 'inlineBlock'}),
    html.Br(),
    html.Br(),
    html.Div([
        dcc.DatePickerRange(
            id = "date_time_picker",
            clearable=True,
            start_date_placeholder_text="MM/DD/YYYY",
            end_date_placeholder_text="MM/DD/YYYY",
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
        )
    ]),
    html.Div([
        html.H1("slprEV Dashboard",
                style={'display': 'inlineBlock', 
                       "textAlign": "center", 
                       "color": "black", 
                       "fontFamily": 'Sans-Serif', 
                       "fontWeight": 800}
        ),
        html.H2(
            dcc.Graph(
                id = "daily peak time series",
            )
        ),
        dcc.Store(id="dataframe")
    ])
])

# read data callback function
@app.callback(Output("dataframe", "data"),
              Input("granularity_picker", 'value')
             )
def read_granularity_data(value):
    df = pd.read_csv(f"data/{value}.csv")
    df.set_index("time", inplace=True)
    return df.to_json(date_format='iso', orient='split') 
       

# granularity callback function  
@app.callback(Output("daily peak time series", "figure"),
              Input("dataframe", "data"),
              Input("granularity_picker", "value")
             )
def display_granularity_figure(df_json, granularity):
    df = pd.read_json(df_json, orient='split')
    fig = go.Figure()
    if granularity == '5minpowerdemand':
        fig.add_trace(go.Scatter(x = df.index, y = df["power_demand"], name = "Daily Peak Power" , hovertext=df["day"]))
        fig.update_layout(title = f"Daily Peak Power Demand", xaxis_title = "Time", yaxis_title="Peak Demand (W)")
    if granularity == 'hourlyenergydemand':
        fig.add_trace(go.Scatter(x = df.index, y = df["energy_demand"], name = "Hourly Energy Demand" , hovertext=df["day"]))
        fig.update_layout(title = f"Hourly Energy Demand", xaxis_title = "Time", yaxis_title="Energy Demand (kWh)")
    return fig


# # calendar callback function 
# @app.callback(Output("daily peak time series", "figure"),
#               Input("date_time_picker", "start_date"),
#               Input("date_time_picker", "end_date"),
#              )
# def display_selected_time(start_date, end_date, value):
#     df = pd.read_csv(f"data/{value}.csv")
#     df.set_index("time", inplace=True)
#     fig = go.Figure()
#     if start_date != None and end_date != None:
#         df = df.loc[(df.index >= start_date) & (df.index <= end_date)]
#     elif start_date != None and end_date == None:
#         df = df.loc[df.index >= start_date]
#     elif start_date == None and end_date != None:
#         df = df.loc[df.index <= end_date]
#     if value == '5minpowerdemand':
#         fig.add_trace(go.Scatter(x = df.index, y = df["power_demand"], name = "Daily Peak Power" , hovertext=df["day"]))
#         fig.update_layout(title = f"Daily Peak Power Demand", xaxis_title = "Time", yaxis_title="Peak Demand (W)")
#     if value == 'hourlyenergydemand':
#         fig.add_trace(go.Scatter(x = df.index, y = df["energy_demand"], name = "Hourly Energy Demand" , hovertext=df["day"]))
#         fig.update_layout(title = f"Hourly Energy Demand", xaxis_title = "Time", yaxis_title="Energy Demand (kWh)")
#     return fig

# running the app
if __name__ == '__main__':
    app.run(debug=True)
