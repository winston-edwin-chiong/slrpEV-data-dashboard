import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
from datetime import timedelta
from dash import html, dcc
from dash.dependencies import Output, Input, State


dash.register_page(__name__, path="/alltime")


def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


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