import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
import dash_daq as daq
from app_utils import get_last_days_datetime

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
                    "Energy Breakdown",
                    dcc.Graph(
                        id="vehicle_pie_chart"
                    )
                ]),
            ]
        )
    return layout