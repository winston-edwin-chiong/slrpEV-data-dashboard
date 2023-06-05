import dash
import dash_bootstrap_components as dbc
import dash_auth
import os
from tasks.schedule import redis_client 
from dash import html, dcc
from dash.dependencies import Output, Input, State
from dotenv import load_dotenv


# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True, use_pages=True)
app.title = "slrpEV Dashboard"

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
                    dbc.Row([
                        dbc.Col([
                            html.Img(src="/assets/images/ChartLogo.png", height="40px", className="me-2")
                        ]),
                    ])
                ], href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse([
                    dbc.Nav([
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-house px-1"),
                            dbc.NavLink("Home", href="/", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-graph-up px-1"),
                            dbc.NavLink("Alltime", href="/alltime", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-table px-1"),
                            dbc.NavLink("Datatable", href="/data", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-calendar-event px-1"),
                            dbc.NavLink("Today", href="/today", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                        dbc.NavItem([
                            html.I(className="navbar-icon bi bi-info-circle px-1"),
                            dbc.NavLink("About", href="/about", className="text-start")
                        ], className="navbar-item d-flex align-items-center"),
                    ], horizontal="center")
                ], id="navbar-collapse", is_open=False, navbar=True)
            ], className="navbar-container ms-2 me-2", fluid=True)
        ], className="py-2 nav-fill w-100 border-start-0 border-end-0 border-2 bg-secondary shadow-sm", sticky="top", expand="lg"),
        # --> <---#


        # --> Page Content <-- #
        dash.page_container,
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
        ])
        # --> <-- #

    ])

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
