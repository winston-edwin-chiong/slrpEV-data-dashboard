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
        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 ms-2 mt-1 rounded", id="tab-one-open-settings-btn"),
        dbc.Collapse([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div("Date Picker"),
                            dcc.DatePickerRange(
                                id="maints-date-picker",
                                clearable=True,
                                start_date=get_last_days_datetime(14),
                                end_date=get_last_days_datetime(0),
                                start_date_placeholder_text="mm/dd/yyyy",
                                end_date_placeholder_text="mm/dd/yyyy",
                                with_portal=False,
                            ),
                        ], className="analytics-control-box d-inline-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                    ], className="col-lg-3 col-sm-6 d-flex justify-content-center align-items-center"),
                    dbc.Col([
                        html.Div([
                            html.Div("Granularity & Units"),
                            dcc.Dropdown(
                                id="dataframe-picker",
                                options=[
                                    {'label': '5-Min', 'value': 'fivemindemand'},
                                    {'label': 'Hourly', 'value': 'hourlydemand'},
                                    {'label': 'Daily', 'value': "dailydemand"},
                                    {'label': 'Monthly', 'value': 'monthlydemand'}
                                ],
                                value='hourlydemand',  # default value
                                clearable=False,
                                searchable=False,
                                className="py-1"
                            ),
                            dcc.Dropdown(
                                id="quantity-picker",
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
                                className="py-1"
                            ),
                        ], className="analytics-control-box d-inline-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                    ], className="col-lg-3 col-sm-6 d-flex justify-content-center align-items-center"),
                    dbc.Col([
                        html.Div([
                            html.Div("Jump to..."),
                            html.Div([
                                html.Button("Today", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 rounded", id="jump_to_present_btn"),
                                html.Button("This Month", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 rounded", id="jump_to_month_btn"),
                                html.Button("This Year", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 rounded", id="jump_to_year_btn"),
                                html.Button("All Time", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 rounded", id="jump_to_alltime_btn")
                            ], className="d-grid gap-2 d-md-block"),
                        ], className="analytics-control-box d-inline-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                    ], className="col-lg-3 col-sm-6 d-flex justify-content-center align-items-center"),
                    dbc.Col([
                        html.Div([
                            html.Div("Toggle Forecasts"),
                            dmc.Switch(
                                size="lg",
                                radius="lg",
                                checked=False,
                                id="toggle-forecasts",
                            ),
                            html.Div("Toggle Histograms"),
                            dmc.Switch(
                                size="lg",
                                radius="lg",
                                checked=True,
                                id="toggle-histograms",
                            )
                        ], className="analytics-control-box d-inline-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                    ], className="col-lg-3 col-sm-6 d-flex justify-content-center align-items-center")
                ])
            ], fluid=True),
            dbc.Tooltip("Only supported for hourly and daily granularities.", target="toggle-forecasts", placement="bottom", delay={"show":2000}),
        ], id="tab-one-settings-collapse", is_open=False),
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="time-series-plot",
                            style={"height": "600px"},
                            config={
                                "displaylogo": False,
                                "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                            },
                            className="p-1 border border-dark rounded"
                        ),                    
                    ], className="col-md-9 col-sm-12"),                    
                    dbc.Col([
                            dcc.Graph(
                            id="hour-histogram",
                            style={"height": "300px"},
                            config = {
                                "displaylogo": False
                            },
                            className="p-1 border border-dark border-bottom-0 rounded-top"
                        ),
                        dcc.Graph(
                            id="day-histogram",
                            style={"height": "300px"},                                
                            config = {
                                "displaylogo": False
                            },
                            className="p-1 border border-dark border-top-0 rounded-bottom"
                        )
                    ], className="col-md-3 col-sm-12")                    
                ])
            ], className="mt-2", fluid=True),
        ]),
    ])

tab_two_content = \
    html.Div([
        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 ms-2 mt-1 rounded", id="tab-two-open-settings-btn"),
        dbc.Collapse([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div("Date Picker"),
                            dcc.DatePickerRange(
                                id="cumulative-date-picker",
                                clearable=True,
                                start_date_placeholder_text="mm/dd/yyyy",
                                end_date_placeholder_text="mm/dd/yyyy",
                                with_portal=False,
                            ),
                        ], className="d-inline-flex flex-column px-2 py-2 border rounded mx-2 my-2"),
                    ], className="col-md-3 col-sm-12"),
                    dbc.Col([
                        html.Div([
                            html.Div("Graph Picker"),
                            dcc.Dropdown(
                                id="cumulative-graph-picker",
                                options=[
                                    {"label": "Cumulative Energy Demand", "value": "cumulative-energy-delivered"},
                                    {"label": "Cumulative Number of Unique Users", "value": "cumulative-num-users"},
                                    {"label": "Cumulative Energy Consumption by Vehicle Model", "value": "cumulative-vehicle-model-energy"},                                    
                                ],
                                value="cumulative-energy-delivered",
                                clearable=False,
                                searchable=False,
                            )
                        ], className="d-inline-flex flex-column px-2 py-2 border rounded mx-2 my-2"),
                    ], className="col-md-3 col-sm-12")
                ], className="justify-content-start"),
            ], fluid=True),
        ], id="tab-two-settings-collapse", is_open=False),
        dcc.Graph(
            id="cumulative-graph",
            config={
                "displaylogo": False
            },
            className="vh-50 border m-2 p-1 border border-dark rounded"
        ),
    ])

tab_three_content = \
    html.Div([
        dcc.Graph(
            id="sched-vs-reg-scatter",           
            config={
                "displaylogo": False
            },
            className="vh-50 border m-2 p-1 border border-dark rounded"
        ),
    ])

layout = \
    dbc.Tabs([
        dbc.Tab(tab_one_content, label="Demand Analytics"),
        dbc.Tab(tab_two_content, label="Cumulative Demand"),
        dbc.Tab(tab_three_content, label="Choice Analytics")
    ], className="pt-1")


# update main time series callback
@dash.callback(
    Output("time-series-plot", "figure"),
    Input("dataframe-picker", "value"),
    Input("quantity-picker", "value"),
    Input("maints-date-picker", "start_date"),
    Input("maints-date-picker", "end_date"),
    Input("toggle-forecasts", "checked"),
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
    Output("day-histogram", "figure"),
    Output("hour-histogram", "figure"),
    Input("time-series-plot", "hoverData"),
    State("quantity-picker", "value"),
    State("dataframe-picker", "value"),
)
def display_histogram_hover(hoverData, quantity, granularity):

    # place holder for no hover
    if hoverData is None:
        return pltf.PlotHoverHistogram.default(), pltf.PlotHoverHistogram.default()

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
    Output("maints-date-picker", "start_date"),
    Output("maints-date-picker", "end_date"),
    Input("jump_to_present_btn", "n_clicks"),
)
def jump_to_present(button_press):
    return get_last_days_datetime(7), get_last_days_datetime(-1)


# jump to this month button
@dash.callback(
    Output("maints-date-picker", "start_date", allow_duplicate=True),
    Output("maints-date-picker", "end_date", allow_duplicate=True),
    Input("jump_to_month_btn", "n_clicks"),
    prevent_initial_call=True
)
def jump_to_month(button_press):
    return get_last_days_datetime(31), get_last_days_datetime(-1)


# jump to this year button
@dash.callback(
    Output("maints-date-picker", "start_date", allow_duplicate=True),
    Output("maints-date-picker", "end_date", allow_duplicate=True),
    Input("jump_to_year_btn", "n_clicks"),
    prevent_initial_call=True
)
def jump_to_year(button_press):
    return get_last_days_datetime(365), get_last_days_datetime(-1)


# jump to this alltime button
@dash.callback(
    Output("maints-date-picker", "start_date", allow_duplicate=True),
    Output("maints-date-picker", "end_date", allow_duplicate=True),
    Input("jump_to_alltime_btn", "n_clicks"),
    prevent_initial_call=True
)
def jump_to_alltime(button_press):
    return None, None


# toggle settings collapse
@dash.callback(
    Output("tab-one-settings-collapse", "is_open"),
    Input("tab-one-open-settings-btn", "n_clicks"),
    State("tab-one-settings-collapse", "is_open"),
)
def toggle_tab_one_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open


# toggle settings collapse
@dash.callback(
    Output("tab-two-settings-collapse", "is_open"),
    Input("tab-two-open-settings-btn", "n_clicks"),
    State("tab-two-settings-collapse", "is_open"),
)
def toggle_tab_two_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open


# update cumulative graph shown
@dash.callback(
    Output("cumulative-graph", "figure"),
    Input("cumulative-date-picker", "start_date"),
    Input("cumulative-date-picker", "end_date"),
    Input("cumulative-graph-picker", "value")
)
def display_cumulative_graph(start_date, end_date, quantity):
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # plot figure
    return pltf.PlotCumulatives.plot_cumulative(quantity, data, start_date, end_date)


# update scheduled vs. regular scatter
@dash.callback(
    Output("sched-vs-reg-scatter", "figure"),
    Input("data_refresh_signal", "data")
)
def display_cumulative_num_users(signal):
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # plot figure
    fig = pltf.PlotSchedVsReg.plot_sched_vs_reg(data)
    return fig 


@dash.callback(
    Output("main-ts-div", "children"),
    Input("toggle-histograms", "checked")
)
def toggle_histograms(checked):
    if checked:
        return # main ts w/ histograms
    return # main ts w/o histograms
