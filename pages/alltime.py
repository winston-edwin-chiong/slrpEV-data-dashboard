import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import pickle
from dash_bootstrap_templates import ThemeChangerAIO
from plotting import plottingfunctions as pltf
from datetime import timedelta, datetime
from dash import html, dcc
from dash.dependencies import Output, Input, State
from db.utils import db

dash.register_page(__name__, path="/alltime")

r = db.get_redis_connection()

### --> Helper Functions <-- ###

def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


def prediction_to_run(granularity):
    if granularity == "fivemindemand":
        return  # not yet supported
    elif granularity == "hourlydemand":
        # return pickle.loads(r.get("hourly_forecasts"))
        return pd.read_csv("data/hourlyforecasts.csv", index_col="time", parse_dates=True)
    elif granularity == "dailydemand":
        # return pickle.loads(r.get("daily_forecasts"))
        return pd.read_csv("data/dailyforecasts.csv", index_col="time", parse_dates=True)
    elif granularity == "monthlydemand":
        return  # not yet supported
    
### --> <-- ###

tab_one_content = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###

                ### --> Main Content <-- ###
                dbc.Col([
                    ### --> Tab One Control Box <-- ###
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 rounded", id="tab-one-open-settings-btn"),
                        ], className="d-inline-block"),
                    dbc.Collapse([
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Date Picker"]),
                                        dcc.DatePickerRange(
                                            id="maints-date-picker",
                                            clearable=True,
                                            start_date=get_last_days_datetime(14),
                                            end_date=get_last_days_datetime(0),
                                            start_date_placeholder_text="mm/dd/yyyy",
                                            end_date_placeholder_text="mm/dd/yyyy",
                                            with_portal=False,
                                            className="dbc"
                                        ),
                                    ], className="w-100 d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-3 col-sm-6 col-12 d-flex"),
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Granularity & Units"]),
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
                                            className="dbc py-1"
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
                                            className="dbc py-1"
                                        ),
                                    ], className="w-100 d-flex flex-column w-100 px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-3 col-sm-6 col-12 d-flex"),
                                dbc.Col([
                                    html.Div([
                                        html.Div("Jump to..."),
                                        html.Div([
                                            html.Button( "Last 7 Days", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 mt-1 rounded", id="jump_to_last_seven_days_btn"), 
                                            html.Button( "This Month", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 mt-1 rounded", id="jump_to_month_btn"),
                                            html.Button( "YTD", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 mt-1 rounded", id="jump_to_year_btn"),
                                            html.Button( "All Time", className="btn btn-outline-secondary btn-sm py-1 px-2 me-1 mt-1 rounded", id="jump_to_alltime_btn")
                                        ], className="gap-2 d-block"),
                                    ], className="w-100 d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-3 col-sm-6 col-12 d-flex"),
                                dbc.Col([ 
                                    html.Div([
                                        html.Div(["Toggle Forecasts"]),
                                        dmc.Switch(size="md", radius="lg", checked=False, id="toggle-forecasts", color="gray"),
                                        html.Div(["Toggle Histograms"]),
                                        dmc.Switch(size="md", radius="lg", checked=True, id="toggle-histograms", color="gray"),
                                    ], className="w-100 d-flex justify-content-center flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-3 col-sm-6 col-12 d-flex")
                            ])
                        ], fluid=True),
                    ], id="tab-one-settings-collapse", is_open=False),
                    ### --> <-- ###

                    ### --> Tab One Main Graphs <-- ###
                    html.Div([            
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        dcc.Loading([
                                            dcc.Graph(
                                                id="time-series-plot",
                                                style={"height": "70vh"},
                                                config={
                                                    "displaylogo": False,
                                                    "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                                },
                                                className="p-1"
                                            ),
                                        ], type="graph", className="dbc")
                                    ], className="border rounded shadow")
                                ], className="col-xl-9 col-12 px-2 flex-grow-1"),
                                dbc.Col([
                                    html.Div([
                                        dcc.Graph(
                                            id="hour-histogram",
                                            style={"height": "35vh"},
                                            config={
                                                "displaylogo": False
                                            },
                                            className="p-1"
                                        ),
                                        dcc.Graph(
                                            id="day-histogram",
                                            style={"height": "35vh"},
                                            config={
                                                "displaylogo": False
                                            },
                                            className="p-1"
                                        )
                                    ], className="d-flex flex-column border rounded shadow")
                                ], className="col-xl-3 col-12 px-2", id="hover-histogram-col")
                            ])
                        ], className="mt-2", fluid=True),
                    ],),
                    ### --> <-- ###
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###

            ]),
        ], fluid=True)
    ])

tab_two_content = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###

                ### --> Main Content <-- ###
                dbc.Col([
                    ### --> Tab Two Control Box <-- ###
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 rounded", id="tab-two-open-settings-btn"),
                    ], className="d-inline-block"),
                    dbc.Collapse([
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Date Picker"]),
                                        dcc.DatePickerRange(
                                            id="cumulative-date-picker",
                                            clearable=True,
                                            start_date_placeholder_text="mm/dd/yyyy",
                                            end_date_placeholder_text="mm/dd/yyyy",
                                            with_portal=False,
                                            className="dbc"
                                        ),
                                    ], className="w-100 d-flex flex-column px-2 py-2 border rounded mx-0 my-2"),
                                ], className="col-12 col-md-4 d-flex"),
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Graph Picker"]),
                                        dcc.Dropdown(
                                            id="cumulative-graph-picker",
                                            options=[
                                                {"label": "Cumulative Energy Demand", "value": "cumulative-energy-delivered"},
                                                {"label": "Cumulative Number of Unique Users", "value": "cumulative-num-users"},
                                                {"label": "Cumulative Energy Consumption\n by Vehicle Model", "value": "cumulative-vehicle-model-energy"},
                                            ],
                                            value="cumulative-energy-delivered",
                                            clearable=False,
                                            searchable=False,
                                            className="dbc"
                                        )
                                    ], className="w-100 d-flex flex-column px-2 py-2 border rounded mx-0 my-2"),
                                ], className="col-12 col-md-4 d-flex")
                            ]),
                        ], fluid=True),
                    ], id="tab-two-settings-collapse", is_open=False),
                    ### --> <-- ###

                    ### --> Tab Two Main Graphs <-- ###
                    html.Div([
                        dbc.Container([
                            html.Div([
                                dcc.Loading([
                                    dcc.Graph(
                                        id="cumulative-graph",
                                        style={"height": "70vh"},
                                        config={
                                            "displaylogo": False
                                        },
                                        className="p-1"
                                    ),
                                ], type="graph", className="dbc")
                            ], className="border rounded shadow")
                        ], className="mt-2", fluid=True)
                    ],),
                    ### --> <-- ###
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True)
    ])

tab_three_content = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###

                ### --> Main Content <-- ###
                dbc.Col([
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 rounded", id="tab-three-open-settings-btn"),
                    ], className="d-inline-block"),
                    dbc.Collapse([
                        dbc.Container([
                        ], fluid=True),
                    ], id="tab-three-settings-collapse", is_open=False),

                    ### --> Tab Three Main Graphs <-- ###
                    html.Div([
                        dbc.Container([
                            html.Div([
                                dcc.Loading([
                                    dcc.Graph(
                                        id="sched-vs-reg-scatter",
                                        style={"height": "70vh"},
                                        config={
                                            "displaylogo": False
                                        },
                                        className="p-1"
                                    ),
                                ], type="graph", className="dbc")
                            ], className="border rounded shadow")
                        ], className="mt-2", fluid=True)
                    ],),
                    ### --> <-- ###
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True)
    ])

layout = \
    dbc.Tabs([
        dbc.Tab(tab_one_content, label="Demand Analytics"),
        dbc.Tab(tab_two_content, label="Cumulative Demand"),
        dbc.Tab(tab_three_content, label="Choice Analytics")
    ], className="my-3 mx-2")


# update main time series callback
@dash.callback(
    Output("time-series-plot", "figure"),
    Input("dataframe-picker", "value"),
    Input("quantity-picker", "value"),
    Input("maints-date-picker", "start_date"),
    Input("maints-date-picker", "end_date"),
    Input("toggle-forecasts", "checked"),
    Input("data_refresh_signal", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value")
)
def display_main_figure(granularity, quantity, start_date, end_date, forecasts, data_signal, theme):
    # load data
    # data = db.get_chunks(r, granularity)
    data = pd.read_csv(f"data/{granularity}.csv", index_col="time", parse_dates=True)
    # plot main time series
    fig = pltf.PlotMainTimeSeries.plot_main_time_series(data, granularity, quantity, start_date, end_date, theme)

    # plot predictions (if supported)
    if forecasts and granularity != "fivemindemand" and granularity != "monthlydemand":
        forecast_df = prediction_to_run(granularity)
        fig = pltf.PlotForecasts.plot_forecasts(fig, forecast_df, quantity, granularity)

    return fig


# update histograms callback
@dash.callback(
    Output("day-histogram", "figure"),
    Output("hour-histogram", "figure"),
    Input("time-series-plot", "hoverData"),
    State("quantity-picker", "value"),
    State("dataframe-picker", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def display_histogram_hover(hoverData, quantity, granularity, theme):

    # place holder for no hover
    if hoverData is None:
        return pltf.PlotHoverHistogram.default(theme), pltf.PlotHoverHistogram.default(theme)

    # load data
    # hourlydemand = db.get_chunks(r, "hourlydemand")
    # dailydemand = db.get_chunks(r, "dailydemand")
    hourlydemand = pd.read_csv("data/hourlydemand.csv", index_col="time", parse_dates=True)
    dailydemand = pd.read_csv("data/dailydemand.csv", index_col="time", parse_dates=True)

    # create hover histograms
    if granularity == "dailydemand":
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(hoverData, dailydemand, quantity, granularity, theme)
        return day_hist, pltf.PlotHoverHistogram.empty_histogram_figure(theme)

    elif granularity == "monthlydemand":
        return pltf.PlotHoverHistogram.empty_histogram_figure(theme), pltf.PlotHoverHistogram.empty_histogram_figure(theme)
    
    elif granularity == "hourlydemand" or granularity == "fivemindemand":
        day_hist = pltf.PlotHoverHistogram.plot_day_hover_histogram(hoverData, dailydemand, quantity, granularity, theme)
        hour_hist = pltf.PlotHoverHistogram.plot_hour_hover_histogram(hoverData, hourlydemand, quantity, theme)
        return day_hist, hour_hist


# jump to present button
@dash.callback(
    Output("maints-date-picker", "start_date"),
    Output("maints-date-picker", "end_date"),
    Input("jump_to_last_seven_days_btn", "n_clicks"),
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
    return pd.Timestamp.now().date().replace(day=1).strftime("%m/%d/%Y"), get_last_days_datetime(-1)


# jump to this year button
@dash.callback(
    Output("maints-date-picker", "start_date", allow_duplicate=True),
    Output("maints-date-picker", "end_date", allow_duplicate=True),
    Input("jump_to_year_btn", "n_clicks"),
    prevent_initial_call=True
)
def jump_to_year(button_press):
    return pd.Timestamp.now().date().replace(month=1, day=1).strftime("%m/%d/%Y"), get_last_days_datetime(-1)


# jump to this alltime button
@dash.callback(
    Output("maints-date-picker", "start_date", allow_duplicate=True),
    Output("maints-date-picker", "end_date", allow_duplicate=True),
    Input("jump_to_alltime_btn", "n_clicks"),
    prevent_initial_call=True
)
def jump_to_alltime(button_press):
    return None, None


# toggle settings collapse one
@dash.callback(
    Output("tab-one-settings-collapse", "is_open"),
    Input("tab-one-open-settings-btn", "n_clicks"),
    State("tab-one-settings-collapse", "is_open"),
)
def toggle_tab_one_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open


# toggle settings collapse two
@dash.callback(
    Output("tab-two-settings-collapse", "is_open"),
    Input("tab-two-open-settings-btn", "n_clicks"),
    State("tab-two-settings-collapse", "is_open"),
)
def toggle_tab_two_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open

# toggle settings collapse three
@dash.callback(
    Output("tab-three-settings-collapse", "is_open"),
    Input("tab-three-open-settings-btn", "n_clicks"),
    State("tab-three-settings-collapse", "is_open"),
)
def toggle_tab_three_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open


# update cumulative graph shown
@dash.callback(
    Output("cumulative-graph", "figure"),
    Input("cumulative-date-picker", "start_date"),
    Input("cumulative-date-picker", "end_date"),
    Input("cumulative-graph-picker", "value"),
    Input("data_refresh_signal", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def display_cumulative_graph(start_date, end_date, value, data_signal, theme):
    # load data
    # data = db.get_chunks(r, "raw_data")
    data = pd.read_csv("data/raw_data.csv")
    # plot figure
    if value == "cumulative-energy-delivered":
        return pltf.PlotCumulatives.plot_cumulative_energy_delivered(data, start_date, end_date, theme)
    elif value == "cumulative-num-users":
        return pltf.PlotCumulatives.plot_cumulative_num_users(data, start_date, end_date, theme)
    elif value == "cumulative-vehicle-model-energy":
        return pltf.PlotCumulatives.plot_cumulative_vehicle_model_energy(data, start_date, end_date, theme)


# update scheduled vs. regular scatter
@dash.callback(
    Output("sched-vs-reg-scatter", "figure"),
    Input("data_refresh_signal", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def display_reg_vs_sched_scatter(data_signal, theme):
    # load data
    # data = db.get_chunks(r, "raw_data")
    data = pd.read_csv("data/raw_data.csv")
    # plot figure
    fig = pltf.PlotSchedVsReg.plot_sched_vs_reg(data, theme)
    return fig

# hide histograms
@dash.callback(
    Output("hover-histogram-col", "style"),
    Input("toggle-histograms", "checked")
)
def toggle_histograms(checked):
    if checked: 
        return {"display": "inline"}
    return {"display": "none"}
