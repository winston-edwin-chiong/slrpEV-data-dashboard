import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
import dash_daq as daq
import pandas as pd
from datetime import timedelta


def tab_one_layout():
    layout = \
        dcc.Tab(
            label="All Time",
            children=[
                html.Div([
                    dcc.DatePickerRange(
                        id="date_picker",
                        clearable=True,
                        start_date=get_last_days_datetime(7),
                        end_date=get_last_days_datetime(0),
                        start_date_placeholder_text="mm/dd/yyyy",
                        end_date_placeholder_text="mm/dd/yyyy",
                        with_portal=False
                    ),
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
                        searchable=False
                    ),
                    dcc.Dropdown(
                        id="quantity_picker",
                        options=[
                            {'label': 'Energy Demand', 'value': 'energy_demand_kWh'},
                            {'label': 'Average Power Demand',
                             'value': 'avg_power_demand_W'},
                            {'label': 'Peak Power Demand',
                             'value': 'peak_power_W'}
                        ],
                        value='energy_demand_kWh',  # default value
                        clearable=False,
                        searchable=False
                    ),
                    html.Button("Today", id="jump_to_present_btn"),
                    html.Button("Refresh Data", id="refresh_data_btn", disabled=True),
                    daq.ToggleSwitch(
                        label="Toggle Forecasts",
                        value=False,
                        id="toggle_forecasts",
                        disabled=True,
                    )
                ]),
                html.Div([
                    dcc.Graph(
                        id="time_series_plot",
                        config={
                            "displaylogo": False,
                            "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                        }
                    )
                ]),
                dcc.Store(id="data_refresh_signal"),
                html.Div([
                    dcc.Interval(
                        id="data_refresh_interval_component",
                        interval=60 * 60 * 1000,  # update every 60 minutes
                        n_intervals=0
                    ),
                    html.Div(
                        id="last_updated_timer"
                    ),
                ]),
                dcc.Store(id="CV_signal"),
                html.Div([
                    dcc.Interval(
                        id="CV_interval_component",
                        interval=20160 * 60 * 1000,  # update every two weeks
                        n_intervals=0
                    ),
                    html.Div(
                        id="last_validated_timer"
                    )
                ]),
                dcc.Interval(
                        id="hourly_forecast_interval_component",
                        interval=60 * 60 * 1000,  # update every 60 minutes
                        n_intervals=0                    
                ),
                html.Div([
                    "Cumulative Energy Delivered",
                    dcc.Graph(
                        id="cumulative_energy_delivered",
                        config={
                            "displaylogo": False
                        }
                    ),
                ])
            ]
        )
    return layout

def get_last_days_datetime(n=7):
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time
