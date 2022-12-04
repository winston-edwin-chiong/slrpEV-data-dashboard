import dash 
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input
import dash_daq as daq
import pandas as pd
from app_utils import query_date_df, plot_time_series, set_index_and_datetime, get_last_days_datetime, add_predictions

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
# today's date
today_date = "08/15/2022" if True else get_last_days_datetime(7)

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
            value = 'energy_demand', # default value
            clearable=False,
            searchable=False
        ),
        html.Button("Jump to Past 7 Days", id="jump_to_present_btn"),
        daq.ToggleSwitch(label="Toggle Predictions", value=True, id="toggle_predictions")
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
    ])
])


# jump to present button 
@app.callback(
    Output("date_time_picker", "start_date"),
    Output("date_time_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks")
)
def jump_to_present(button_press):
    return "08/15/2022", None # placeholder, no new data yet


# calendar and granularity dropdown callback function  
@app.callback(
    Output("time_series_plot", "figure"),
    Output("current_df", "data"),
    Input("granularity_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_time_picker", "start_date"),
    Input("date_time_picker", "end_date"),
    Input("toggle_predictions", "value")
    )
def display_main_figure(granularity, quantity, start_date, end_date, predictions):
    
    df = dataframes[granularity]
    df = df[[quantity, "day"]]
    df = query_date_df(df, start_date, end_date)

    fig = plot_time_series(df, granularity, quantity)

    if predictions == True:
        add_predictions(fig, start_date, end_date)

    jsonified_df = df.to_json(orient='split')

    return fig, jsonified_df
        
# running the app
if __name__ == '__main__':
    app.run(debug=True)
