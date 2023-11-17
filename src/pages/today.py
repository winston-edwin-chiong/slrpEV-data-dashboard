import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_bootstrap_templates import ThemeChangerAIO
from plotting import plottingfunctions as pltf
from dash.dependencies import Input, Output, State
from dash import html, dcc, Patch
from db.utils import db


dash.register_page(__name__, path="/today")

r = db.get_redis_connection()

layout = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###
                
                ### --> Main Content <-- ###
                dbc.Col([
                    ### --> Today Control Box <-- ###
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
                                            className="dbc"
                                        )
                                    ], className="d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-md-4 col-12"),
                                dbc.Col([
                                    html.Div([
                                        html.Div(["Toggle Yesterday"]),
                                        dmc.Switch( size="lg", radius="lg", checked=False, id="toggle-yesterday", color="gray"),
                                        html.Div(["Toggle Peak Power Forecast"]),
                                        dmc.Switch( size="lg", radius="lg", checked=False, id="toggle-daily-forecast", color="gray"),
                                    ], className="d-flex flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-md-3 col-12")
                            ],)
                        ], fluid=True),
                    ], id="today-settings-collapse"),
                    ### --> <-- ###

                    ### --> Today Main Graph <-- ###
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
                                        ], type="graph", className="dbc"),
                                    ], className="border rounded shadow")
                                ], className="col-md-10 col-12 px-2 flex flex-grow-1"),
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
                                                    ], className="p-1"),
                                                html.Ul([
                                                    html.Span("Preferred charging choice: ", className="fst-italic"), 
                                                    html.Span(id="pref_charging_choice_user")
                                                    ], className="p-1")
                                            ], id='user-information', className="p-3 text-break"),
                                    ], className="border rounded shadow"),
                                ], className="col-md-2 col-12 px-2", id="hover-user-col")
                            ], className="row-gap-4")
                        ], className="mt-2", fluid=True),
                    ]),
                    ### --> <-- ###
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True),
    ])


@dash.callback(
    Output("num_sessions_user", "children"),
    Output("avg_duration_user", "children"),
    Output("freq_connect_time_user", "children"),
    Output("total_nrg_consumed_user", "children"),
    Output("pref_charging_choice_user", "children"),
    Input("today-graph", "hoverData"),
    State("today-graph-picker", "value"),
    prevent_initial_call=True
)
def display_user_hover(hoverData, value):
    # place holder for no hover or if graph is not the daily time series
    if hoverData is None or value != "today-aggregate-power":
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    # load data
    data = db.get_df(r, "raw_data_subset")
    # get user ID
    userId = int(hoverData["points"][0]["customdata"][2])

    # get user hover data
    num_sessions, avg_duration, freq_connect, total_nrg, pref_charging_choice, pref_charging_choice_percent = pltf.GetUserHoverData.get_user_hover_data(data, userId)
    
    text = (
        f"{num_sessions}", 
        f"{avg_duration} hours", 
        f"{freq_connect}", 
        f"{total_nrg:.1f} kWh",
        f"{pref_charging_choice} ({pref_charging_choice_percent:.0%})"
    )

    return text 


@dash.callback(
    Output("today-graph", "figure"),
    Output("hover-user-col", "style"),
    Input("today-graph-picker", "value"),
    Input("toggle-yesterday", "checked"),
    Input("toggle-daily-forecast", "checked"),
    Input("data-refresh-signal", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def display_today_graph(value, yesterday, forecast, data_signal, theme):
    # load data
    data = db.get_df(r, "todays_sessions")

    if value == "today-aggregate-power":
        fivemindemand, daily_forecasts = db.get_multiple_df(r, ["fivemindemand", "dailyforecasts"])
        return pltf.PlotDaily.plot_daily_time_series(data, yesterday, fivemindemand, daily_forecasts, forecast, theme), {"display": "inline"}

    elif value == "today-energy-dist":
        return pltf.PlotDaily.plot_daily_energy_breakdown(data, theme), {"display": "none"}
    

# toggle settings collapse
@dash.callback(
    Output("today-settings-collapse", "is_open"),
    Input("today-open-settings-btn", "n_clicks"),
    State("today-settings-collapse", "is_open"),
)
def toggle_today_options_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open
