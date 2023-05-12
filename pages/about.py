import dash 
from dash import html, dcc

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        html.H1([
            "THIS IS THE ABOUT PAGE!"
        ]),
        html.P("SlrpEV is a University of California research project developing the next-generation of EV charging stations that intelligently manages electric power and parking through machine learning."),
        html.Img(src=r'assets/cat1.jpg', alt='image', className="Mac")
    ])