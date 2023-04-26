import dash 
from dash import html, dcc 

dash.register_page(__name__, path="/")

layout = \
    html.Div([
        html.H1("THIS IS THE HOME PAGE!"),
        html.Img(src=r'assets/cat1.jpg', alt='image', className="Mac")
    ])