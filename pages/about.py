import dash 
from dash import html, dcc

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        html.H1([
            "THIS IS THE ABOUT PAGE SLAY"
        ])
    ])