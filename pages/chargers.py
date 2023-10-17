import dash 
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, "/chargers")

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