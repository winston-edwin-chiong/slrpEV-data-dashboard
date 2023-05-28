import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import pickle
from plotting import plottingfunctions as pltf
from datetime import timedelta
from dash import html, dcc
from dash.dependencies import Output, Input, State
from tasks.schedule import redis_client


dash.register_page(__name__, path="/alltime")


def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


def prediction_to_run(granularity):
    if granularity == "fivemindemand":
        return  # not yet supported
    elif granularity == "hourlydemand":
        return pickle.loads(redis_client.get("hourly_forecasts"))
    elif granularity == "dailydemand":
        return pickle.loads(redis_client.get("daily_forecasts"))
    elif granularity == "monthlydemand":
        return  # not yet supported

tab_one_content = \
        html.Div([
            html.Div([ # control options div
                    dcc.DatePickerRange(
                        id="ts_date_picker",
                        clearable=True,
                        start_date=get_last_days_datetime(7),
                        end_date=get_last_days_datetime(0),
                        start_date_placeholder_text="mm/dd/yyyy",
                        end_date_placeholder_text="mm/dd/yyyy",
                        with_portal=False,
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
                        searchable=False,
                    ),
                    dcc.Dropdown(
                        id="quantity_picker",
                        options=[
                            {'label': 'Energy Demand',
                            'value': 'energy_demand_kWh'},
                            {'label': 'Average Power Demand',
                            'value': 'avg_power_demand_W'},
                            {'label': 'Peak Power Demand',
                            'value': 'peak_power_W'}
                        ],
                        value='energy_demand_kWh',  # default value
                        clearable=False,
                        searchable=False,
                    ),
                html.Button("Today", className="btn btn-primary py-1", id="jump_to_present_btn"),
                dmc.Switch(
                    size="lg",
                    radius="lg",
                    checked=False,
                    id="toggle_forecasts",
                )
            ], className="d-flex justify-content-center my-5"),
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(
                                id="time_series_plot",
                                style={"height": "700px"},
                                config={
                                    "displaylogo": False,
                                    "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                },
                            ),                    
                        width=9,),                    
                        dbc.Col([
                                dcc.Graph(
                                id="hour_histogram",
                                style={"height": "350px"},
                                config = {
                                    "displaylogo": False
                                },
                            ),
                            dcc.Graph(
                                id="day_histogram",
                                style={"height": "350px"},                                
                                config = {
                                    "displaylogo": False
                                },
                            )
                        ], width=3)                    
                    ])
                ], fluid=True),
            ]),
        ])

tab_two_content = \
    html.Div([
        dcc.DatePickerRange(
            id="cumulative_date_picker",
            clearable=True,
            start_date=get_last_days_datetime(7),
            end_date=get_last_days_datetime(0),
            start_date_placeholder_text="mm/dd/yyyy",
            end_date_placeholder_text="mm/dd/yyyy",
            with_portal=False,
        ),
        dcc.Graph(
            id="cumulative_energy_delivered",
            style={"height": "700px"},            
            config={
                "displaylogo": False
            }
        ),
    ])

tab_three_content = \
    html.Div([
        "Monki"
    ])

layout = \
    dbc.Tabs([
        dbc.Tab(tab_one_content, label="Power & Energy Demand Analytics"),
        dbc.Tab(tab_two_content, label="Cumulative Demand"),
        dbc.Tab(tab_three_content, label="Choice Analytics")
    ])


# update main time series callback
@dash.callback(
    Output("time_series_plot", "figure"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("ts_date_picker", "start_date"),
    Input("ts_date_picker", "end_date"),
    Input("toggle_forecasts", "checked"),
    Input("data_refresh_signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, data_signal):
    # load data
    data = pickle.loads(redis_client.get(granularity))
    # plot main time series
    fig = pltf.PlotMainTimeSeries.plot_main_time_series(
        data, granularity, quantity, start_date, end_date)

    # plot predictions (if supported)
    if forecasts and granularity != "fivemindemand" and granularity != "monthlydemand":
        forecast_df = prediction_to_run(granularity)
        fig = pltf.PlotForecasts.plot_forecasts(
            fig, forecast_df, quantity, granularity)

    return fig

# update histograms callback


@dash.callback(
    Output("day_histogram", "figure"),
    Output("hour_histogram", "figure"),
    Input("time_series_plot", "hoverData"),
    State("quantity_picker", "value"),
    State("dataframe_picker", "value"),
    prevent_initial_call=True
)
def display_histogram_hover(hoverData, quantity, granularity):

    # place holder for no hover
    if hoverData is None:
        return dash.no_update, dash.no_update

    # load data
    hourlydemand = pickle.loads(redis_client.get("hourlydemand"))
    dailydemand = pickle.loads(redis_client.get("dailydemand"))

    # create hover histograms
    if granularity == "dailydemand":
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(
            hoverData, dailydemand, quantity)
        return day_hist, pltf.PlotHoverHistogram.empty_histogram_figure()

    elif granularity == "monthlydemand":
        return pltf.PlotHoverHistogram.empty_histogram_figure(), pltf.PlotHoverHistogram.empty_histogram_figure()

    else:
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(
            hoverData, dailydemand, quantity)
        hour_hist = pltf.PlotHoverHistogram.plot_hour_hover_histogram(
            hoverData, hourlydemand, quantity)
        return day_hist, hour_hist


# jump to present button
@dash.callback(
    Output("ts_date_picker", "start_date"),
    Output("ts_date_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks"),
)
def jump_to_present(button_press):
    return get_last_days_datetime(7), get_last_days_datetime(-1)


@dash.callback(
    Output("cumulative_energy_delivered", "figure"),
    Input("cumulative_date_picker", "start_date"),
    Input("cumulative_date_picker", "end_date"),
    Input("data_refresh_signal", "data")
)
def display_cumulative_energy_figure(start_date, end_date, signal):
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # plot figure
    fig = pltf.PlotCumulativeEnergyDelivered.plot_cumulative_energy_delivered(
        data, start_date, end_date)
    return fig
