import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_daq as daq


def tab_two_layout():
    layout = \
        dcc.Tab(
            label="Today's Usage",
            children=[
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
                        dcc.Tooltip(
                            id="daily_session_tooltip",
                        )
                    ]),
                    "User Information",
                    html.Div([
                        html.Li("# of Sessions by User",
                                id="num_sessions_user"),
                        html.Li("Avg. Stay Duration", id="avg_duration_user"),
                        html.Li("Frequent Connect Time",
                                id="freq_connect_time_user"),
                        html.Li("Total Energy Consumed",
                                id="total_nrg_consumed_user")
                    ],
                        id='user-information',
                    ),
                    html.Div([
                        "Energy Breakdown",
                        dcc.Graph(
                            id="vehicle_pie_chart"
                        )
                    ]),
                ]),
            ],
        )
    return layout
