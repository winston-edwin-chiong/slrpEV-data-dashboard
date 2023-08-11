import dash
import dash_bootstrap_components as dbc
import dash_auth
import os
import redis
from dash import html, dcc
from dash.dependencies import Output, Input, State
from dotenv import load_dotenv


# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME,], suppress_callback_exceptions=True, use_pages=True)
server = app.server
app.title = "slrpEV Dashboard"

# redis_client = redis.Redis(
#     host='localhost',
#     port=6360,
# )

# redis_client = redis.Redis(
#   host='redis-11349.c60.us-west-1-2.ec2.cloud.redislabs.com',
#   port=11349,
#   username="default",
#   password='gnfYJxa4j7KG9tNcsLqRyq8aQ4Bwgzu2',
#   socket_keepalive=True,)
redis_client = redis.Redis(
  host='redis-10912.c53.west-us.azure.cloud.redislabs.com',
  port=10912,
  password='gnfYJxa4j7KG9tNcsLqRyq8aQ4Bwgzu2')

load_dotenv()
auth = dash_auth.BasicAuth(
    app,
    {os.getenv("dash_username"): os.getenv("dash_password")}
)

# app layout
app.layout = \
    html.Div([

        # --> Navbar <-- #
        dbc.Navbar([
            dbc.Container([
                html.A([
                    html.Img(src="/assets/images/ChartLogo.png", height="40px", className="me-2")
                ], href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse([
                    dbc.Nav([
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-house px-1 text-primary"),
                            dbc.NavLink("Home", href="/", className="text-start text-primary")
                        ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 rounded-4"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-graph-up px-1 text-primary"),
                            dbc.NavLink("Alltime", href="/alltime", className="text-start text-primary")
                        ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 rounded-4"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-table px-1 text-primary"),
                            dbc.NavLink("Datatable", href="/data", className="text-start text-primary")
                        ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 rounded-4"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-calendar-event px-1 text-primary"),
                            dbc.NavLink("Today", href="/today", className="text-start text-primary")
                        ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 rounded-4"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-info-circle px-1 text-primary"),
                            dbc.NavLink("About", href="/about", className="text-start text-primary")
                        ], className="d-flex align-items-center btn btn-light py-0 px-1 mx-1 rounded-4"),
                    ])
                ], id="navbar-collapse", className="my-2", is_open=False, navbar=True)
            ], className="navbar-container ms-2 me-2", fluid=True)
        ], className="py-2 nav-fill w-100 border-start-0 border-end-0 border-2 bg-secondary shadow-sm", expand="lg"),
        # --> <---#


        # --> Page Content <-- #
        html.Div([
            dash.page_container,
        ], className="d-flex flex-column flex-grow-1"),
        # --> <-- #

        html.Div([
            html.Div(
                id="last_updated_timer",
            ),
            html.Div(
                id="last_validated_timer",
            ),
        ], className="d-inline-flex flex-column"),
        
        # --> Interval Components, Refresh/Validation Timestamps <-- #
        html.Div([
            html.Div([
                dcc.Interval(
                    id="data_refresh_interval_component",
                    interval=30 * 60 * 1000,  # update every 30 minutes
                    n_intervals=0
                ),
                dcc.Store(id="data_refresh_signal"),
            ]),
            html.Div([
                dcc.Interval(
                    id="CV_interval_component",
                    interval=2 * 24 * 60 * 60 * 1000,  # update every two days
                    n_intervals=0
                ),
                dcc.Store(id="CV_signal"),
            ]),
        ]),
        # --> <-- #

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
        ], className="fs-6 mt-5 p-2 bg-secondary border-top border-2 shadow-top"),
        # --> <-- #

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


# --> Interval Components <-- #

@app.callback(
    Output("data_refresh_signal", "data"),
    Output("last_updated_timer", "children"),
    Input("data_refresh_interval_component", "n_intervals"),
)
def data_refresh_interval(n):
    '''
    This callback polls the Redis database at regular intervals for data refresh. 
    '''
    # update data refresh timestamp
    last_updated = redis_client.get('last_updated_time').decode("utf-8")
    return n, f"Data last updated at {last_updated}."


@app.callback(
    Output("CV_signal", "data"),
    Output("last_validated_timer", "children"),
    Input("CV_interval_component", "n_intervals"),
)
def CV_interval(n):
    '''
    This callback polls the Redis database at regular intervals for ML parameter refresh. 
    '''
    # update CV timestamp 
    last_validated = redis_client.get("last_validated_time").decode("utf-8")
    return n, f"Parameters last validated at {last_validated}." 

# --> <-- #


# running the app
if __name__ == '__main__':
    app.run_server(debug=True)
