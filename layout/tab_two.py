import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_daq as daq


def tab_two_layout():
    layout = \
        dcc.Tab(
            label="Today's Sessions",
            children=[
                html.Div([
                    "Today's Sessions",
                    dcc.Graph(
                        id="daily_time_series",
                        config={
                            "displaylogo": False,
                            "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                        }
                    ),
                    "User Information",
                    dcc.Graph(
                        id="user_graph_hover"
                    ),
                    "Energy Breakdown",
                    dcc.Graph(
                        id="vehicle_pie_chart"
                    )
                ]),
            ]
        )
    return layout
