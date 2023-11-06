import dash 
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Input, Output, State, dcc
from db.utils import db 

dash.register_page(__name__, "/chargers")

r = db.get_redis_connection()

def get_charger_state(inuse: int, rate: float, vehicle_model: str, choice: str):
    """
    Returns the on-screen display state, `IDLE` or `IN USE` for a charger given a 0 or 1. 
    """
    if inuse:
        return [
        html.Span([
            "Status: ",
            html.Span([
                "IN USE", 
                html.I(className="ms-1 bi bi-circle-fill fs-6", style={"color": "#58c21e"})
                ], className="d-inline-flex align-items-center")
            ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill"),
        html.Span([
            html.Span([f"{vehicle_model} @ {rate/1000} kW"])
            ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill"),
        ]
    
    return html.Span([
        "Status: ", 
        html.Span([
            "IDLE", 
            html.I(className="ms-1 bi bi-circle-fill fs-6", style={"color": "#c21e58"})
            ], className="d-inline-flex align-items-center")
        ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")


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
                    dbc.Alert([
                        html.I(className="bi bi-exclamation-triangle-fill me-2"),
                        "In development! Working on visualizing the usage of each charger!"
                    ], color="warning", className="m-2"),

                    ### --> Chargers Control Box <-- ###
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 my-3 rounded mt-3 mb-1", id="chargers-open-settings-btn"),
                    ], className="d-inline-block"),
                    dbc.Collapse([
                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Div("Sample Label"),
                                        dcc.Dropdown(
                                            id="charger-picker",
                                            options=[
                                                {"label": "Sample Option 1", "value": "one"},
                                                {"label": "Sample Option 2", "value": "two"},                                    
                                            ],
                                            value="one",
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
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("11"),
                                    html.Div(id="charger-11-usage-status"),
                                    html.Div(id="charger-11-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-11-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 11")),
                                            dbc.ModalBody(dcc.Graph()),
                                        ],
                                        id="charger-11-modal",
                                        is_open=False,
                                    ),
                                        dbc.ModalFooter(),           
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("12"),
                                    html.Div(id="charger-12-usage-status"),
                                    html.Div(id="charger-12-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-12-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 12")),
                                            dbc.ModalBody(dcc.Graph()),
                                        ],
                                        id="charger-12-modal",
                                        is_open=False,
                                    ),
                                        dbc.ModalFooter(),           
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                                ])
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("13"),
                                    html.Div(id="charger-13-usage-status"),       
                                    html.Div(id="charger-13-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-13-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 13")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter()                 
                                        ],
                                        id="charger-13-modal",
                                    ),      
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                                                     
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("14"),
                                    html.Div(id="charger-14-usage-status"),
                                    html.Div(id="charger-14-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-14-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 14")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter(),           
                                        ],
                                        id="charger-14-modal",
                                        is_open=False,
                                    ),
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                    
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                        ], className=""),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("15"),
                                    html.Div(id="charger-15-usage-status"),
                                    html.Div(id="charger-15-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-15-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 15")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter(),           
                                        ],
                                        id="charger-15-modal",
                                        is_open=False,
                                    ),
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                    
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("16"),
                                    html.Div(id="charger-16-usage-status"),
                                    html.Div(id="charger-16-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-16-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 16")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter(),           
                                        ],
                                        id="charger-16-modal",
                                        is_open=False,
                                    ),
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                    
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("17"),
                                    html.Div(id="charger-17-usage-status"),
                                    html.Div(id="charger-17-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-17-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 17")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter(),           
                                        ],
                                        id="charger-17-modal",
                                        is_open=False,
                                    ),
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                    
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("18"),
                                    html.Div(id="charger-18-usage-status"),
                                    html.Div(id="charger-18-utilization", className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(id="charger-18-open-modal", className="bi bi-box-arrow-up-right position-absolute top-0 end-0 m-1", role="button"),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Charger 18")),
                                            dbc.ModalBody(dcc.Graph()),
                                            dbc.ModalFooter(),           
                                        ],
                                        id="charger-18-modal",
                                        is_open=False,
                                    ),
                                    html.I(className="bi bi-plugin position-absolute bottom-0 end-0 m-1")                                    
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                        ], className="")
                    ], className="text-center"),
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
    Output("charger-11-usage-status", "children"),
    Output("charger-12-usage-status", "children"),
    Output("charger-13-usage-status", "children"),
    Output("charger-14-usage-status", "children"),
    Output("charger-15-usage-status", "children"),
    Output("charger-16-usage-status", "children"),
    Output("charger-17-usage-status", "children"),
    Output("charger-18-usage-status", "children"),
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
        row["choice"]
        ), 
        axis=1).to_list()

    return inuse

# charger utlizations
@dash.callback(
    Output("charger-11-utilization", "children"),
    Output("charger-12-utilization", "children"),
    Output("charger-13-utilization", "children"),
    Output("charger-14-utilization", "children"),
    Output("charger-15-utilization", "children"),
    Output("charger-16-utilization", "children"),
    Output("charger-17-utilization", "children"),
    Output("charger-18-utilization", "children"),
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


for i in range(11, 19):
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
