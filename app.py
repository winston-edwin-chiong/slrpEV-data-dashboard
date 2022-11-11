import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import pandas as pd
import time

import plotly.graph_objects as go

def plot_daily_peak_power():
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x = df_24h.index, y = df_24h["power_demand"] , name = "Daily Peak Power" , hovertext=df_24h["day"])
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
        ),
        dcc.Dropdown(
            id = "granularity_picker",
            options=["5-Min", "Hourly", "Daily"], 
            value='5-Min',
            clearable=False
        )
    ]),
    html.Div([
        html.H1("slprEV Dashboard",
                style={'display': 'inlineBlock', 
                       "textAlign": "center", 
                       "color": "black", 
                       "fontFamily": 'Sans-Serif', 
                       "fontWeight": 800}),
        html.H2(
            dcc.Graph(
                id = "daily peak time series",
            )
        )
    ])
])

# # callback function for calendar 
# @app.callback(Output("daily peak time series", "figure"),
#               Input("date_time_picker", "start_date"),
#               Input("date_time_picker", "end_date"),
#              )
# def display_selected_time(start_date, end_date):
#     df = pd.read_csv("data/5minpowerdemand.csv")
#     df.set_index("time", inplace=True)
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x = df.index, y = df["power_demand"], name = "Daily Peak Power" , hovertext=df["day"]))
#     fig.update_layout(title = f"Daily Peak Power Demand", xaxis_title = "Time", yaxis_title="Peak Demand (W)")
#     if start_date == None and end_date == None:
#         return fig
#     elif start_date != None and end_date == None:
#         fig.update_layout(xaxis_range = [start_date, df["power_demand"].index[-1]])
#         return fig
#     elif start_date == None and end_date != None:
#         fig.update_layout(xaxis_range=[df["power_demand"].index[0], end_date])
#         return fig
#     fig.update_layout(xaxis_range=[start_date, end_date])
#     return fig

# callback function for calendar 
@app.callback(Output("daily peak time series", "figure"),
              Input("date_time_picker", "start_date"),
              Input("date_time_picker", "end_date"),
             )
def display_selected_time(start_date, end_date):
    df = pd.read_csv("data/5minpowerdemand.csv")
    df.set_index("time", inplace=True)
    fig = go.Figure()
    if start_date != None and end_date != None:
        df = df.loc[(df.index >= start_date) & (df.index <= end_date)]
    elif start_date != None and end_date == None:
        df = df.loc[df.index >= start_date]
    elif start_date == None and end_date != None:
        df = df.loc[df.index <= end_date]
    fig.add_trace(go.Scatter(x = df.index, y = df["power_demand"], name = "Daily Peak Power" , hovertext=df["day"]))
    fig.update_layout(title = f"Daily Peak Power Demand", xaxis_title = "Time", yaxis_title="Peak Demand (W)")
    return fig

# running the app
if __name__ == '__main__':
    app.run(debug=True)
