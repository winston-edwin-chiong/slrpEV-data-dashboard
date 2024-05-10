import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
from dotenv import load_dotenv
from dash_bootstrap_templates import ThemeChangerAIO
from db.utils import db

# connect to Redis
load_dotenv()
r = db.get_redis_connection()

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME, r"assets/dbc.min.css"], suppress_callback_exceptions=True, use_pages=True)
server = app.server
app.title = "slrpEV Dashboard"


# theme options
themes_options = [
    {"label": "Bootstrap, the original 🚼", "value": dbc.themes.BOOTSTRAP},
    {"label": "Cerulean, a calm blue sky ⛱️", "value": dbc.themes.CERULEAN},
    {"label": "Cosmo, an ode to Metro 🗔", "value": dbc.themes.COSMO},
    {"label": "Darkly, flatly in night mode 🌕", "value": dbc.themes.DARKLY},
    {"label": "Journal, crisp like a new sheet of paper 📃", "value": dbc.themes.JOURNAL},
    {"label": "Litera, the medium is the message 📰", "value": dbc.themes.LITERA},
    {"label": "Lumen, light and shadow ☀️/🌑", "value": dbc.themes.LUMEN},
    {"label": "Lux, a touch of class 👔", "value": dbc.themes.LUX},
    {"label": "Minty, a fresh feel 🍭", "value": dbc.themes.MINTY},
    {"label": "Morph, a neomorphic layer 🧬", "value": dbc.themes.MORPH},
    {"label": "Pulse, a trace of purple 💜", "value": dbc.themes.PULSE},
    {"label": "Sandstone, a touch of warmth 🏜️", "value": dbc.themes.SANDSTONE},
    {"label": "Sketchy, a hand-drawn look for mockups and mirth ✏️", "value": dbc.themes.SKETCHY},
    {"label": "Solar, a spin on Solarized 🌞", "value": dbc.themes.SOLAR},
    {"label": "Spacelab, silvery and sleek 🥈", "value": dbc.themes.SPACELAB},
    {"label": "Superhero, the brave and the blue 🫡", "value": dbc.themes.SUPERHERO},
    {"label": "United, Ubuntu orange and unique font 🟠", "value": dbc.themes.UNITED},
    {"label": "Vapor, a cyberpunk aesthetic 🤖", "value": dbc.themes.VAPOR},
    {"label": "Yeti, a friendly foundation ❄️", "value": dbc.themes.YETI},
    {"label": "Zephyr, breezy and beautiful 💨", "value": dbc.themes.ZEPHYR},
]

# app layout
app.layout = \
    html.Div([

        ### --> Navbar <-- ###
        dbc.Navbar([
            dbc.Container([
                html.A([
                    html.Img(src=r"assets/images/ChartLogo.png", height="40px", className="me-2")
                ], href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse([
                    html.Div([
                        dbc.Nav([
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-house ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("Home", className="d-md-none d-lg-inline")
                                ], href="/", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-graph-up ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("Alltime", className="d-md-none d-lg-inline")
                                ], href="/alltime", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-table ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("Datatable", className="d-md-none d-lg-inline")
                                ], href="/data", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-calendar-event ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("Today", className="d-md-none d-lg-inline")
                                ], href="/today", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-ev-station ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("Chargers", className="d-md-none d-lg-inline")
                                ], href="/chargers", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-cloud-arrow-down ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("API", className="d-md-none d-lg-inline")
                                ], href="https://slrpev-data-api-winston-edwin-chiong.koyeb.app/docs", className="text-md-center text-start text-primary", target="_blank")
                            ], className="d-none d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"), # disabled for now
                            dbc.NavItem([
                                dbc.NavLink([
                                    html.I(className="navbar-icon bi bi-info-circle ms-md-2 ms-lg-0 ms-1 me-2 text-primary"),
                                    html.Span("About", className="d-md-none d-lg-inline")
                                ], href="/about", className="text-md-center text-start text-primary")
                            ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 mb-2 mb-md-0 rounded-4"),
                        ]),
                        html.Div([
                            ThemeChangerAIO(
                                aio_id="theme", 
                                radio_props={"value":dbc.themes.LUX, "options":themes_options, "persistence": True}, 
                                button_props={"className":"px-1 py-0 rounded d-flex justify-content-center align-items-center"},
                                offcanvas_props={"title":"Select a theme!", "style":{"width":"27%"}},
                                )
                        ], className="d-flex flex-row align-items-center mx-2 mt-1 mt-md-0 mx-md-0"),
                    ], className="flex-md-row flex-column d-flex flex-grow-1 justify-content-between")
                ], id="navbar-collapse", className="my-2", is_open=False, navbar=True)
            ], className="navbar-container ms-2 me-2", fluid=True)
        ], className="py-2 nav-fill w-100 border-2 bg-secondary shadow-sm", expand="md"),
        # --> <---#


        ### --> Page Content <-- ###
        html.Div([
            dash.page_container,
        ], className="d-flex flex-column flex-grow-1"),
        # --> <-- #


        ### --> Interval Components <-- ###
        html.Div([
            html.Div([
                dcc.Interval(
                    id="data-refresh-interval-component",
                    interval=25 * 60 * 1000,  # poll db every 25 minutes
                    n_intervals=0
                ),
                dcc.Store(id="data-refresh-signal"),
            ]),
        ]),
        ### --> <-- ###


        ### --> Footer <-- ###
        html.Footer([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(["Made with ❤️ & 🍵 by Winston"]),
                    ]),
                    html.Div(["Icons by Bootstrap Icons & Icons8, Themes by Bootswatch"]),
                    html.Div([
                        html.A(html.I(className="bi bi-globe2 m-1"), href="https://www.winstonchiong.com/", target="_blank"),
                        html.A(html.I(className="bi bi-github m-1"), href="https://github.com/winston-edwin-chiong/slrpEV-data-dashboard", target="_blank"),
                        html.A(html.I(className="bi bi-linkedin m-1"), href="https://www.linkedin.com/in/winstonechiong/", target="_blank"),
                    ], className="d-flex")
                ], className="d-flex flex-column justify-content-center align-items-center text-center"),
            ], className="d-flex justify-content-center align-items-center")
        ], className="fs-6 mt-5 p-2 bg-light text-dark shadow-top"),
        ### --> <-- ###

    ], className="d-flex flex-column min-vh-100")


# callback for toggling the collpase on small screens 
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open")
)
def toggle_navbar_collapse(n, is_open):
    if n: 
        return not is_open 
    return is_open 


### --> Interval Components <-- ###

@app.callback(
    Output("data-refresh-signal", "data"),
    Input("data-refresh-interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def data_refresh_interval(n):
    '''
    This callback does something at regular intervals.
    '''
    return n

### --> <-- ###


# running the app
if __name__ == '__main__':
    app.run_server(debug=True)
