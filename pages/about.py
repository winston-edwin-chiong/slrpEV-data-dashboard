import dash 
from dash import html, dcc

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        html.Div([
            html.P("The intent of this dashboard is to visualize and analyze slrpEV demand."),
        ], className="text-center m-2")
    ])

