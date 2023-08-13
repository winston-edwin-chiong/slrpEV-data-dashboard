import dash 
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        ### --> Dashboard Descripton & Contact <-- ###
        html.Div([
            html.P("Visualizing and analyzing slrpEV demand!."),
            html.P("Please reach out for suggestions, comments, questions, or requests!"),
        ], className="text-center m-2"),
        ### --> <-- ###

        ### --> Mac <-- ###
        html.Div(["This is Mac."]),
        html.Img([
        ], src=r"assets/images/cat1.jpg", alt="Winston's cat", className="h-auto w-auto", style={"max-width": "25%"})
        ### --> <-- ###
    ], className="d-flex flex-column justify-content-center align-items-center")
