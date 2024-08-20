import dash 
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from plotting import plottingfunctions as pltf
from dash_bootstrap_templates import ThemeChangerAIO
from dash import html, Input, Output, State, dcc
from db.utils import db 

dash.register_page(__name__, "/chargers")

r = db.get_redis_connection()

charger_numbers_sorted = db.get_df(r, "chargers")["stationId"].sort_values(ascending=True).unique()

def get_charger_state(inuse: int, rate: float, vehicle_model: str, choice: str, sched_price: int, reg_price: int):
    """
    Returns the on-screen display state, `IDLE` or `IN USE` for a charger given a 0 or 1. 
    """
    if inuse:
        return [
            html.Div([        
                html.Span([
                    "Status: ",
                    html.Span([
                        "IN USE", 
                        html.I(className="ms-1 bi bi-plugin fs-5 animate__animated animate__pulse animate__infinite infinite", style={"color": "#58c21e"})
                        ], className="d-inline-flex align-items-center")
                    ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill border border-info-subtle")
            ]),
            html.Div([
                html.Div([
                    html.Div([f"{vehicle_model} @ {rate/1000} kW"]),
                    html.Div([f"{choice}"])
                    ], className="my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-3 border border-info-subtle"),
            ]),
            html.Div([
                html.Span([
                    html.Div([f"Sched. Offer: {sched_price} ¢/hr"], className="px-2 py-1" + (" bg-success-subtle rounded-end rounded-pill" if choice == "SCHEDULED" else "")),
                    html.Div(className="vr"),
                    html.Div([f"Reg. Offer: {reg_price} ¢/hr"], className="px-2 py-1" + (" bg-success-subtle rounded-start rounded-pill" if choice == "REGULAR" else ""))
                    ], className="d-inline-flex align-items-center justify-content-center my-2 fw-bolder fs-6 text-dark bg-body-secondary rounded-pill border border-info-subtle")
            ])
        ]
    
    return \
    html.Div([
        html.Span([
                "Status: ", 
                html.Span([
                    "IDLE", 
                    html.I(className="ms-1 bi bi-circle-fill fs-6", style={"color": "#c21e58"})
                    ], className="d-inline-flex align-items-center")
                ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill border border-info-subtle")
        ])


def get_charger_utilization(occupation_util_percent: float, power_util_percent: float):
    """
    Given two numbers, utilization by occupation percent and utilization by power percent, returns the 
    ring progress and labels associated with each percentage.
    """
    utilization_by_occupation = \
        html.Div([
            html.Div("Utilization by Occupation", className="px-3"),
            dmc.RingProgress(
                sections=[
                    {
                        "value": occupation_util_percent,
                        "color": "#003262"
                    }
                ],
                label=dmc.Center(dmc.Text(f"{occupation_util_percent:.1f}%", color="#003262")),
                size=120,
                thickness=12
            ),
        ], className="d-flex flex-column align-items-center")
    
    utilization_by_power = \
        html.Div([
            html.Div("Utilization by Power", className="px-3"),
            dmc.RingProgress(
                sections=[
                    {
                        "value": power_util_percent,
                        "color": "#FDB515"
                    }
                ],
                label=dmc.Center(dmc.Text(f"{power_util_percent:.1f}%", color="#FDB515")),
                size=120,
                thickness=12
            )
        ], className="d-flex flex-column align-items-center")
    
    return [utilization_by_occupation, utilization_by_power]


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

                    ### --> Chargers Control Box <-- ###
                    html.Div([
                        html.Div([
                            html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 my-3 rounded mt-3 mb-1", id="chargers-open-settings-btn", disabled=True),
                        ], className="d-inline-block"),
                        html.I(id="charger-tooltip-btn", className="btn btn-sm btn-outline-secondary py-0 px-1 border border-0 rounded bi bi-info-circle fs-5"),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle(f"About Chargers!")),
                                dbc.ModalBody([
                                    dcc.Markdown(['''
                                        A _**SCHEDULED**_ session is defined as a user accepting a predetermined start and end charging time, while a _**REGULAR**_ session
                                        is your normal drop-in charging.  
                                                  
                                        The _**utilization rate by occupation**_ is defined as the total time an EV charger is connected / plugged into an EV as a ratio of the entire day.
                                        
                                        Similarly, the _**utilization rate by power**_ is defined as the ratio between the actual charging power and the rated power of an EV charger over the entire day.
                                        At slrpEV, the chargers are assumed to be rated at 6.6kW.
                                    '''])                                               
                                ]),
                            ], id=f"charger-tooltip-modal", is_open=False, size="lg"),
                    ], className="d-flex align-items-end justify-content-between"),
                    dbc.Collapse([
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Div("Options"),
                                        dcc.Dropdown(
                                            id="charger-picker",
                                            options=[
                                                {"label": "Option 1", "value": "option_1"},
                                                {"label": "Option 2", "value": "option_2"},                                    
                                            ],
                                            value="option_1",
                                            clearable=False,
                                            searchable=False,
                                            className="dbc"
                                        )
                                    ], className="flex-column px-2 py-2 border rounded mx-0 my-2")
                                ], className="col-md-4 col-12"),
                            ],)
                        ], fluid=True),
                    ], id="chargers-settings-collapse"),
                    ### --> <-- ###

                    ### --> Chargers <-- ###
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                # html.Div([
                                    html.Div([
                                        html.H3("CHARGER"),
                                        html.H3(f"{i}"),
                                        html.Div(id=f"charger-{i}-usage-status", className="mb-4 d-flex flex-column"),
                                        html.Div(id=f"charger-{i}-utilization", className="mt-auto d-flex align-items-end justify-content-center"),
                                        html.I(id=f"charger-{i}-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                        dbc.Modal(
                                            [
                                                dbc.ModalHeader(dbc.ModalTitle(f"Charger {i}")),
                                                dbc.ModalBody([
                                                    dbc.Alert([
                                                        html.I(className="bi bi-exclamation-triangle-fill me-2"),
                                                        "In development!"
                                                    ], color="warning", className="m-2"),                                                
                                                    dcc.Graph(
                                                        config={
                                                            "displaylogo": False,
                                                            "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                                        },
                                                    ),
                                                ]),
                                                dbc.ModalFooter(),           
                                            ], id=f"charger-{i}-modal", is_open=False, size="xl"),
                                    ], className="h-100 d-flex flex-column position-relative flex-grow-1 bg-light shadow border border-secondary rounded py-2 px-3")
                                # ], className="h-100"),
                            ], className="col-xxl-3 col-md-6 col-12")
                            for i in charger_numbers_sorted
                        ], className="g-4"),
                    ], className="text-center mt-2"),
                    ### --> <-- ###

                    ### --> Utilization Bar Chart <-- ###
                    html.Div([
                        dcc.Loading([
                            dcc.Graph(
                                id="charger-usage-bar-chart",
                                config={
                                    "displaylogo": False,
                                    "modeBarButtonsToAdd": ["hoverCompare", "hoverClosest"]
                                },
                                className="p-1"
                            )
                        ], type="graph", className="dbc"),
                    ], className="border rounded shadow my-5 mx-4")
                    ### --> <-- ###

                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True)
    ])


# charger states
@dash.callback(
    [Output(f"charger-{i}-usage-status", "children") for i in charger_numbers_sorted],
    Input("data-refresh-signal", "data")
)
def update_charger_usage(n):
    # load data
    chargers = db.get_df(r, "chargers")

    # calculate in use
    inuse = chargers.sort_values("stationId", ascending=True).apply(lambda row: get_charger_state(
        row["inUse"], 
        row["currentChargingRate"], 
        row["vehicle_model"], 
        row["choice"],
        row["sch_centsPerHr"],
        row["reg_centsPerHr"],
        ), 
        axis=1).to_list()
    
    return inuse

# charger utlizations
@dash.callback(
    [Output(f"charger-{i}-utilization", "children") for i in charger_numbers_sorted],
    Input("data-refresh-signal", "data")
)
def update_charger_utilizations(n):
    # load data
    chargers = db.get_df(r, "chargers")

    # calculate in use
    utilization = chargers.sort_values("stationId", ascending=True).apply(lambda row: get_charger_utilization(
        100*row["currOccupUtilRate"], 
        100*row["currPowerUtilRate"], 
        ), 
        axis=1).to_list()

    return utilization


for i in charger_numbers_sorted:
    # show/hide modal 
    @dash.callback(
        Output(f"charger-{i}-modal", "is_open"),
        Input(f"charger-{i}-open-modal", "n_clicks"),
        State(f"charger-{i}-modal", "is_open"),
    )
    def toggle_modal(n, is_open):
        if n:
            return not is_open
        return is_open
    
# charger usage bar chart 
@dash.callback(
    Output("charger-usage-bar-chart", "figure"),
    Input("data-refresh-signal", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def charger_usage_bar_chart(n, theme):
    # load data
    chargers = db.get_df(r, "chargers")

    # plot charger usage bar chart 
    return pltf.PlotChargers.plot_charger_usage_bar_chart(chargers, theme)


# toggle settings collapse
@dash.callback(
    Output("chargers-settings-collapse", "is_open"),
    Input("chargers-open-settings-btn", "n_clicks"),
    State("chargers-settings-collapse", "is_open"),
)
def toggle_chargers_options_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open

# charger tooltip show/hide modal
@dash.callback(
    Output(f"charger-tooltip-modal", "is_open"),
    Input(f"charger-tooltip-btn", "n_clicks"),
    State(f"charger-tooltip-modal", "is_open"),
)
def toggle_tooltip_modal(n, is_open):
    if n:
        return not is_open
    return is_open