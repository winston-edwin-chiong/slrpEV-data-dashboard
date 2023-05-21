import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
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
        return # not yet supported 
    elif granularity == "hourlydemand":
        return pickle.loads(redis_client.get("hourly_forecasts"))
    elif granularity == "dailydemand":
        return pickle.loads(redis_client.get("daily_forecasts"))
    elif granularity == "monthlydemand":
        return # not yet supported 


layout = \
    dbc.Container([
        html.Div([
            html.Div([
                html.Div([
                    dcc.DatePickerRange(
                        id="date_picker",
                        clearable=True,
                        start_date=get_last_days_datetime(7),
                        end_date=get_last_days_datetime(0),
                        start_date_placeholder_text="mm/dd/yyyy",
                        end_date_placeholder_text="mm/dd/yyyy",
                        with_portal=False,
                    ),
                ],
                    className="calendar"),
                html.Div([
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
                ]),
                html.Button("Today", className="btn btn-primary", id="jump_to_present_btn"),
                daq.ToggleSwitch(
                    label="Toggle Forecasts",
                    value=False,
                    id="toggle_forecasts",
                )
            ]),
            html.Button("Hide Histograms", id="hide-histogram-btn"),
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(
                                id="time_series_plot",
                                config={
                                    "displaylogo": False,
                                    "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                },
                            ),                    
                        width=9,),                    dbc.Col([
                                dcc.Graph(
                                id="hour_histogram",
                                config = {
                                    "displaylogo": False
                                },
                            ),
                            dcc.Graph(
                                id="day_histogram",
                                config = {
                                    "displaylogo": False
                                },
                            )
                        ], width=3)                    
                    ])
                ], fluid=True),
            ]),
            html.Div([
                dcc.Graph(
                    id="cumulative_energy_delivered",
                    config={
                        "displaylogo": False
                    }
                ),
            ]),
            # Interval components, refresh/validation timestamps
            html.Div([
                html.Div([
                    dcc.Interval(
                        id="data_refresh_interval_component",
                        interval=30 * 60 * 1000,  # update every 30 minutes
                        n_intervals=0
                    ),
                    dcc.Store(id="data_refresh_signal"),
                ]),
                html.Div(
                    id="last_updated_timer"
                ),
                html.Div([
                    dcc.Interval(
                        id="CV_interval_component",
                        interval=2 * 24 * 60 * 60 * 1000,  # update every two days
                        n_intervals=0
                    ),
                    dcc.Store(id="CV_signal"),
                ]),
                html.Div(
                    id="last_validated_timer"
                ),
            ])
        ])
    ])


@dash.callback(
    Output('hour_histogram', 'style'), 
    Output('day_histogram', 'style'), 
    Input('hide-histogram-btn','n_clicks'),
    prevent_initial_call=True
)
def hide_graph(n):
    if n % 2 != 0:
        return {'display':'none'}, {'display':'none'}
    else:
        return {'display':'block'}, {'display':'block'}


@dash.callback(
    Output("time_series_plot", "figure"),
    Input("dataframe_picker", "value"),
    Input("quantity_picker", "value"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("toggle_forecasts", "value"),
    Input("data_refresh_signal", "data"),
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, data_signal,):
    # load data
    data = pickle.loads(redis_client.get(granularity))
    # plot main time series
    fig = pltf.PlotMainTimeSeries.plot_main_time_series(
        data, granularity, quantity, start_date, end_date)
    
    # plot predictions (if supported)
    if forecasts and granularity != "fivemindemand" and granularity != "monthlydemand":
        forecast_df = prediction_to_run(granularity)
        fig = pltf.PlotForecasts.plot_forecasts(fig, forecast_df, quantity, granularity)

    return fig

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

    # extract hour and day 
    if hoverData["points"][0]["curveNumber"] == 0:
        day = hoverData["points"][0]["customdata"][0] 
        hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))
    elif hoverData["points"][0]["curveNumber"] == 1:
        day = pd.to_datetime(hoverData["points"][0]["x"]).day_name()
        hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))
    
    # create hover histograms
    if granularity == "dailydemand":
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        return day_hist, pltf.PlotHoverHistogram.empty_histogram_figure()
    
    elif granularity == "monthlydemand":
        return pltf.PlotHoverHistogram.empty_histogram_figure(), pltf.PlotHoverHistogram.empty_histogram_figure()
    
    else:
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(dailydemand, quantity, day)
        hour_hist = pltf.PlotHoverHistogram.plot_hour_hover_histogram(hourlydemand, quantity, hour)
        return day_hist, hour_hist


# jump to present button
@dash.callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks"),
)
def jump_to_present(button_press):
    return get_last_days_datetime(7), get_last_days_datetime(-1)


@dash.callback(
    Output("cumulative_energy_delivered", "figure"),
    Input("date_picker", "start_date"),
    Input("date_picker", "end_date"),
    Input("data_refresh_signal", "data")
)
def display_cumulative_energy_figure(start_date, end_date, signal):
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # plot figure
    fig = pltf.PlotCumulativeEnergyDelivered.plot_cumulative_energy_delivered(
        data, start_date, end_date)
    return fig