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
    ])
