import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
import dash_daq as daq
from app_utils import get_last_days_datetime

def tab_one_layout():
    layout = \
            dcc.Tab(
            label="Tab One",
            children=[
                html.Div([
                    dcc.DatePickerRange(
                        id="date_picker",
                        clearable=True,
                        start_date=get_last_days_datetime(7),
                        end_date = get_last_days_datetime(0),
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
                            {'label': 'Average Power Demand', 'value': 'avg_power_demand_W'},
                            {'label': 'Peak Power Demand', 'value': 'peak_power_W'}
                        ],
                        value='energy_demand_kWh',  # default value
                        clearable=False,
                        searchable=False
                    ),
                    html.Button("Today", id="jump_to_present_btn"),
                    daq.ToggleSwitch(
                        label="Toggle Predictions", 
                        value=False, 
                        id="toggle_predictions", 
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
                dcc.Store(id='current_df'),  # stores current dataframe
                dcc.Store(id="signal"),
                html.Div([
                    dcc.Interval(
                        id="interval_component",
                        interval=60* 1000,  # update every 20 minutes
                        n_intervals=0
                    ),
                    html.Div(
                        id="last_updated_timer"
                    ),
                ])
            ]
        )
    return layout