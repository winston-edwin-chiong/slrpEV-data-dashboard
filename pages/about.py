import dash 
import os
from dash.dependencies import ClientsideFunction, Input, Output
from dash import html, dcc
from dotenv import load_dotenv

dash.register_page(__name__, "/about")

load_dotenv()

layout = \
    html.Div([
        html.Div([
            html.P("The intent of this dashboard is to visualize and analyze slrpEV demand."),
        ], className="text-center m-2"),

        # --> Footer <-- #
        html.Footer([
            html.Div([
                html.Div([
                    html.Div("Made with ❤️ by Winston"),
                    html.Div("Icons by Bootstrap Icons and Icons8"),
                    html.Div([
                        html.A(html.I(className="bi bi-github m-1"), href="https://github.com/winston-edwin-chiong/slrpEV-data-dashboard", target="_blank"),
                        html.A(html.I(className="bi bi-linkedin m-1"), href="https://www.linkedin.com/in/winstonechiong/", target="_blank"),
                    ], className="d-flex"),
                ], className="d-inline-flex flex-column align-items-center")
            ], className="d-flex justify-content-center align-items-center")
        ], className="my-footer p-2 mt-5 bg-secondary border-top border-2 shadow-top"),
        # --> <-- #
    ])
