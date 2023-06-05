import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_daq as daq
import pickle
from plotting import plottingfunctions as pltf
from dash.dependencies import Input, Output, State
from dash import html, dcc, Patch
from tasks.schedule import redis_client

dash.register_page(__name__, path="/today")


layout = \
    html.Div([
        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 ms-2 mt-1 rounded", id="today-open-settings-btn"),
        dbc.Collapse([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div("Graph Picker"),
                            dcc.Dropdown(
                                id="today-graph-picker",
                                options=[
                                    {"label": "Today's 5-Min Aggregate Power", "value": "today-aggregate-power"},
                                    {"label": "Today's Energy Distribution by Vehicle Model", "value": "today-energy-dist"},                                    
                                ],
                                value="today-aggregate-power",
                                clearable=False,
                                searchable=False,
                            )
                        ], className="d-inline-flex flex-column px-2 py-2 border rounded mx-2 my-2")
                    ], className="col-lg-5 col-sm-12 col-12"),
                    dbc.Col([
                        html.Div([
                            html.Div("Toggle Yesterday"),
                            dmc.Switch(
                                size="lg",
                                radius="lg",
                                checked=False,
                                id="toggle-yesterday",
                            ),
                            html.Div("Toggle Peak Power Forecast"),
                            dmc.Switch(
                                size="lg",
                                radius="lg",
                                checked=False,
                                id="toggle-daily-forecast",
                            ),
                        ], className="d-inline-flex flex-column px-2 py-2 border rounded mx-2 my-2")
                    ], className="col-lg-4 col-sm-12 col-12")
                ], className="justify-content-start")
            ], fluid=True),
        ], id="today-settings-collapse"),
        html.Div([
        ], id="today-graph", className="my-2")
    ])


@dash.callback(
    Output("daily_time_series", "figure"),
    Input("data_refresh_signal", "data"),
    Input("toggle-yesterday", "checked"),
    Input("toggle-daily-forecast", "checked")
)
def display_daily_time_series(signal, yesterday, forecast):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessions.plot_daily_time_series(data)
    # plot yesterday's time series
    if yesterday:
        fivemindemand = pickle.loads(redis_client.get("fivemindemand"))
        fig = pltf.PlotDailySessions.plot_yesterday(fig, fivemindemand)
    if forecast:
        daily_forecast = pickle.loads(redis_client.get("daily_forecasts"))
        fig = pltf.PlotDailySessions.plot_today_forecast(fig, daily_forecast)
    return fig


@dash.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("data_refresh_signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessions.plot_daily_energy_breakdown(data)
    return fig


@dash.callback(
    Output("num_sessions_user", "children"),
    Output("avg_duration_user", "children"),
    Output("freq_connect_time_user", "children"),
    Output("total_nrg_consumed_user", "children"),
    Input("daily_time_series", "hoverData"),
    prevent_initial_call=True
)
def display_user_hover(hoverData):
    # place holder for no hover
    if hoverData is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    # load data
    data = pickle.loads(redis_client.get("raw_data"))
    # get user ID
    userId = int(hoverData["points"][0]["customdata"][2])
    # get user hover data
    num_sessions, avg_duration, freq_connect, total_nrg = pltf.GetUserHoverData.get_user_hover_data(
        data, userId)
    
    text = (
        f"{num_sessions}", 
        f"{avg_duration} hours", 
        f"{freq_connect}", 
        f"{round(total_nrg, 1)} kWh"
    )

    return text


@dash.callback(
    Output("today-graph", "children"),
    Input("today-graph-picker", "value")
)
def display_today_graph(value):
    if value == "today-aggregate-power":
        return (            
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            dcc.Loading([
                                dcc.Graph(
                                    id="daily_time_series",
                                    config={
                                        "displaylogo": False,
                                        "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                    },
                                    className="p-1 border border-dark rounded"
                                ),
                            ]),
                        ], className="col-md-10 col-sm-12 px-2"),
                        dbc.Col([
                            html.Div("User Information", className="fw-bold"),
                            html.Div([
                                html.Ul([
                                    html.Span("Lifetime number of sessions: ", className="fst-italic"),
                                    html.Span(id="num_sessions_user")
                                    ], className="p-1"),
                                html.Ul([
                                    html.Span("Average charge duration: ", className="fst-italic"), 
                                    html.Span(id="avg_duration_user")
                                    ], className="p-1"),
                                html.Ul([
                                    html.Span("Usual charge time: ", className="fst-italic"), 
                                    html.Span(id="freq_connect_time_user")
                                    ], className="p-1"),
                                html.Ul([
                                    html.Span("Lifetime energy consumption: ", className="fst-italic"), 
                                    html.Span(id="total_nrg_consumed_user")
                                    ], className="p-1")
                            ], id='user-information', className="p-3 border border-dark rounded"),
                        ], className="col-md-2 col-sm-12 d-inline-flex flex-column align-items-center justify-content-center px-2")
                    ], className="row mx-2")
                ], className="mt-2 p-0", fluid=True),
            ]),
        )
    elif value == "today-energy-dist":
        return (
            html.Div([
                dcc.Loading([
                    dcc.Graph(
                        id="vehicle_pie_chart",
                        config={
                            "displaylogo": False
                        },
                        className="p-1 border border-dark rounded"
                    ),
                ])
            ], className="mx-2"),
        )


# toggle settings collapse
@dash.callback(
    Output("today-settings-collapse", "is_open"),
    Input("today-open-settings-btn", "n_clicks"),
    State("today-settings-collapse", "is_open"),
)
def toggle_tab_one_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open
