import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import pickle
from plotting import plottingfunctions as pltf
from dash.dependencies import Input, Output, State
from dash import html, dcc
from tasks.schedule import redis_client

dash.register_page(__name__, path="/today")

layout = \
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([]),
                dbc.Col([])
            ])
        ])
    ])

layout = \
    html.Div([
        html.Div([
            html.Div([
                "Today's Sessions",
                html.Div([
                    daq.ToggleSwitch(
                        label="Toggle Yesterday",
                        value=False,
                        id="toggle_yesterday"),
                ]),
                dcc.Graph(
                    id="daily_time_series",
                    config={
                        "displaylogo": False,
                        "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                    },
                ),
            ]),
            "User Information",
            html.Div([
                html.Li("User has been here ",
                        id="num_sessions_user"),
                html.Li("User charges on average", id="avg_duration_user"),
                html.Li("User usually charges",
                        id="freq_connect_time_user"),
                html.Li("User has consumed",
                        id="total_nrg_consumed_user")
            ],
                id='user-information',
            ),
            html.Div([
                "Energy Breakdown",
                dcc.Graph(
                    id="vehicle_pie_chart",
                    config={
                        "displaylogo": False
                    }
                )
            ]),
        ]),
    ])


@dash.callback(
    Output("daily_time_series", "figure"),
    Input("data_refresh_signal", "data"),
    Input("toggle_yesterday", "value")
)
def display_daily_time_series(signal, yesterday):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessionTimeSeries.plot_daily_time_series(data)
    # plot yesterday's time series
    if yesterday:
        fivemindemand = pickle.loads(redis_client.get("fivemindemand"))
        fig = pltf.PlotDailySessionTimeSeries.plot_yesterday(fig, fivemindemand)
    return fig

@dash.callback(
    Output("vehicle_pie_chart", "figure"),
    Input("data_refresh_signal", "data"),
)
def display_vehicle_pie_chart(signal):
    # load data
    data = pickle.loads(redis_client.get("todays_sessions"))
    # plot figure
    fig = pltf.PlotDailySessionEnergyBreakdown.plot_daily_energy_breakdown(data)
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
        f"User has been here {num_sessions} times!", 
        f"User charges on average {avg_duration} hours!", 
        f"User usually charges: {freq_connect}", 
        f"User has consumed {total_nrg} kWh to date!"
    )

    return text