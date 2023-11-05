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
        return ["IN USE", html.I(className="ms-1 bi bi-circle-fill fs-6", style={"color": "#58c21e"})] # TODO: Add in the rate and vehicle model.
    return ["IDLE", html.I(className="ms-1 bi bi-circle-fill fs-6", style={"color": "#c21e58"})]


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
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-11-usage-status")
                                        ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill"),
                                    html.Span([
                                        html.Span(["Tesla Model 3 @ 3.3 kW"])
                                        ], className="d-inline-block my-2 fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill"),
                                    html.Div([
                                        html.Div([
                                            html.Div("Utilization by Occupation", className="px-3"),
                                            dmc.RingProgress(
                                                sections=[
                                                    {
                                                        "tooltip": "Yeah!",
                                                        "value": 65,
                                                        "color": "orange"
                                                    }
                                                ],
                                                label=dmc.Center(dmc.Text("65%", color="orange")),
                                                size=120,
                                                thickness=12
                                            ),
                                        ], className="d-flex flex-column align-items-center"),
                                        html.Div([
                                            html.Div("Utilization by Power", className="px-3"),
                                            dmc.RingProgress(
                                                sections=[
                                                    {
                                                        "tooltip": "Yeah2!",
                                                        "value": 65,
                                                        "color": "blue"
                                                    }
                                                ],
                                                label=dmc.Center(dmc.Text("65%", color="blue")),
                                                size=120,
                                                thickness=12
                                            )
                                        ], className="d-flex flex-column align-items-center")
                                    ], className="my-3 d-flex align-items-center justify-content-center"),
                                    html.I(className="bi bi-plug-fill position-absolute bottom-0 end-0")
                                ], className="position-relative shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("12"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-12-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("13"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-13-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("14"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-14-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                        ], className=""),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("15"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-15-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("16"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-16-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("17"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-17-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
                            ], className="col-xxl-3 col-md-6 col-12"),
                            dbc.Col([
                                html.Div([
                                    html.H3("CHARGER"),
                                    html.H3("18"),
                                    html.Span([
                                        "Status: ",
                                        html.Span(id="charger-18-usage-status")                                        
                                        ], className="fw-bolder text-dark bg-body-secondary px-2 py-1 rounded-pill")
                                ], className="shadow border border-secondary rounded mx-2 my-2 p-2")
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
