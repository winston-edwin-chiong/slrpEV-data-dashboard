import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pickle
import pandas as pd
from plotting import plottingfunctions as pltf
from dash.dependencies import Input, Output, State
from dash import html, dcc, Patch
from tasks.schedule import redis_client

dash.register_page(__name__, path="/today")


def get_chunks(name, chunk_size=30):
    deserialized_chunks = []
    for i in range(chunk_size):
        serialized_chunk = redis_client.get(f"{name}_{i}")
        chunk = pickle.loads(serialized_chunk)
        deserialized_chunks.append(chunk)

    result = pd.concat(deserialized_chunks)
    return result

layout = \
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                dbc.Col([
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 my-3 rounded mt-3 mb-1", id="today-open-settings-btn"),
                    ], className="d-inline-block"),
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
                                    ], className="d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-6 col-12"),
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Toggle Yesterday"]),
                                        dmc.Switch(
                                            size="lg",
                                            radius="lg",
                                            checked=False,
                                            id="toggle-yesterday",
                                        ),
                                        html.Div(["Toggle Peak Power Forecast"]),
                                        dmc.Switch(
                                            size="lg",
                                            radius="lg",
                                            checked=False,
                                            id="toggle-daily-forecast",
                                        ),
                                    ], className="d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-lg-6 col-12")
                            ], className="justify-content-center")
                        ], fluid=True),
                    ], id="today-settings-collapse"),
                    html.Div([
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        dcc.Loading([
                                            dcc.Graph(
                                                id="today-graph",
                                                style={"height": "70vh"},
                                                config={
                                                    "displaylogo": False,
                                                    "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                                },
                                                className="p-1"
                                            ),
                                        ]),
                                    ], className="border rounded shadow")
                                ], className="col-md-10 col-12 px-2"),
                                dbc.Col([
                                    html.Div([
                                        html.Div(["User Information"], className="p-3 fw-bold"),
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
                                        ], id='user-information', className="p-3 text-break"),
                                    ], className="border rounded shadow"),
                                ], className="col-md-2 col-12 px-2")
                            ],)
                        ], className="mt-2", fluid=True),
                    ]),
                ], className="col-12 col-lg-10"),
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
            ])
        ], fluid=True),
    ])



# @dash.callback(
#     Output("daily_time_series", "figure"),
#     Input("data_refresh_signal", "data"),
#     Input("toggle-yesterday", "checked"),
#     Input("toggle-daily-forecast", "checked")
# )
# def display_daily_time_series(signal, yesterday, forecast):
#     # load data
#     data = get_chunks("todays_sessions")
#     # plot figure
#     fig = pltf.PlotDailySessions.plot_daily_time_series(data)
#     # plot yesterday's time series
#     if yesterday:
#         fivemindemand = get_chunks("fivemindemand")
#         fig = pltf.PlotDailySessions.plot_yesterday(fig, fivemindemand)
#     if forecast:
#         daily_forecast = pickle.loads(redis_client.get("daily_forecasts"))
#         fig = pltf.PlotDailySessions.plot_today_forecast(fig, daily_forecast)
#     return fig


# @dash.callback(
#     Output("vehicle_pie_chart", "figure"),
#     Input("data_refresh_signal", "data"),
# )
# def display_vehicle_pie_chart(signal):
#     # load data
#     data = get_chunks("todays_sessions")
#     # plot figure
#     fig = pltf.PlotDailySessions.plot_daily_energy_breakdown(data)
#     return fig


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
    data = get_chunks("raw_data")
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
    Input("today-graph-picker", "value"),
    Input("toggle-yesterday", "checked"),
    Input("toggle-daily-forecast", "checked"),
    Input("data_refresh_signal", "data"),
)
def display_today_graph(value, yesterday, forecast, data_signal):
    # load data
    data = get_chunks("todays_sessions")
    fivemindemand = get_chunks("fivemindemand")
    daily_forecasts = get_chunks("daily_forecasts")

    return pltf.PlotDailySessions.plot_daily(data, value, yesterday, fivemindemand, daily_forecasts, forecast)
    # if value == "today-aggregate-power":
    #     return (            
    #         html.Div([
    #             dbc.Container([
    #                 dbc.Row([
    #                     dbc.Col([
    #                         dcc.Loading([
    #                             dcc.Graph(
    #                                 id="daily_time_series",
    #                                 config={
    #                                     "displaylogo": False,
    #                                     "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
    #                                 },
    #                                 className="p-1 border border-dark rounded"
    #                             ),
    #                         ]),
    #                     ], className="col-md-10 col-sm-12 px-2"),
    #                     dbc.Col([
    #                         html.Div("User Information", className="fw-bold"),
    #                         html.Div([
    #                             html.Ul([
    #                                 html.Span("Lifetime number of sessions: ", className="fst-italic"),
    #                                 html.Span(id="num_sessions_user")
    #                                 ], className="p-1"),
    #                             html.Ul([
    #                                 html.Span("Average charge duration: ", className="fst-italic"), 
    #                                 html.Span(id="avg_duration_user")
    #                                 ], className="p-1"),
    #                             html.Ul([
    #                                 html.Span("Usual charge time: ", className="fst-italic"), 
    #                                 html.Span(id="freq_connect_time_user")
    #                                 ], className="p-1"),
    #                             html.Ul([
    #                                 html.Span("Lifetime energy consumption: ", className="fst-italic"), 
    #                                 html.Span(id="total_nrg_consumed_user")
    #                                 ], className="p-1")
    #                         ], id='user-information', className="p-3 border border-dark rounded"),
    #                     ], className="col-md-2 col-sm-12 d-inline-flex flex-column align-items-center justify-content-center px-2")
    #                 ], className="row mx-2")
    #             ], className="mt-2 p-0", fluid=True),
    #         ]),
    #     )
    # elif value == "today-energy-dist":
    #     return (
    #         html.Div([
    #             dcc.Loading([
    #                 dcc.Graph(
    #                     id="vehicle_pie_chart",
    #                     config={
    #                         "displaylogo": False
    #                     },
    #                     className="p-1 border border-dark rounded"
    #                 ),
    #             ])
    #         ], className="mx-2"),
    #     )


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
