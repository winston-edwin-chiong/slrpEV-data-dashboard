import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_daq as daq

dash.register_page(__name__, path="/today")

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
                    id="vehicle_pie_chart",
                    config={
                        "displaylogo": False
                    }
                )
            ]),
        ]),
        # Interval components 
        html.Div([
            dcc.Interval(
                id="data_refresh_interval_component",
                interval=60 * 60 * 1000,  # update every 60 minutes
                n_intervals=0
            ),
            dcc.Store(id="data_refresh_signal"),
            html.Div(id="last_updated_timer")
        ]),
    ])
