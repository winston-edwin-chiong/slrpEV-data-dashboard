import dash 
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        ### --> Dashboard Descripton & Contact <-- ###
        html.Div([
            dbc.Alert("This app is still under development! There may be some bugs 🐛...", color="warning"),
            html.P("The intent of the app is visualizing and analyzing slrpEV demand."),
            html.P([
                html.Span("Charge at "),
                html.Span("2301 Bancroft Way, Berkeley, CA 94720. ", className="fw-italic"),
                html.Span("Request access "),
                html.Span(html.A("here!", href="https://docs.google.com/forms/d/e/1FAIpQLScuI2LUrPkxfU4BdbnnULyJVHb9HFTMBapTIs9EEWjCw6-tzQ/viewform", target="_blank", className="fw-bold text-info"))
            ]),
            html.Br(),
            html.P("ARIMA and k-NN based models are used to generate the daily and hourly forecasts. Data is refreshed hourly, and model hyperparameters are recalculated every month. This resets all past predictions and starts a new cycle."),
            html.Br(),
            html.P([
                "Please reach out for suggestions, comments, questions, or requests at ",
                html.Span([
                    html.A("winstonchiong@berkeley.edu!", href="mailto:winstonchiong@berkeley.edu", className="fst-italic fw-bold text-info")
                ])
            ]),
            html.Br(),
        ], className="text-center m-2"),
        ### --> <-- ###

        ### --> Mac <-- ###
        html.Div(["This is Mac."]),
        html.Img([
        ], src=r"assets/images/cat1.jpg", alt="Winston's cat", className="h-auto w-auto", style={"max-width": "25%"})
        ### --> <-- ###
    ], className="d-flex flex-column justify-content-center align-items-center")
