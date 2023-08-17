import dash
import dash_bootstrap_components as dbc
import dash_auth
import os
from dash import html, dcc
from dash.dependencies import Output, Input, State
from dotenv import load_dotenv
from dash_bootstrap_templates import ThemeChangerAIO
from tasks.schedule import START_SCHEDULER


# styles
dbc_css = ( "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css" )

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css], suppress_callback_exceptions=True, use_pages=True)
server = app.server
app.title = "slrpEV Dashboard"


load_dotenv()
auth = dash_auth.BasicAuth(
    app,
    {os.getenv("DASH_USERNAME"): os.getenv("DASH_PASSWORD")}
)

# theme options
themes_options = [
    {"label": "Bootstrap, the OG 🚼", "value": dbc.themes.BOOTSTRAP},
    {"label": "Cerulean, a calm blue sky ⛱️", "value": dbc.themes.CERULEAN},
    {"label": "Cosmo, an ode to Metro 🗔", "value": dbc.themes.COSMO},
    {"label": "Cyborg, jet black and electric blue ⚫+⚡🔵", "value": dbc.themes.CYBORG},
    {"label": "Darkly, flatly in night mode 🌕", "value": dbc.themes.DARKLY},
    {"label": "Journal, crisp like a new sheet of paper 📃", "value": dbc.themes.JOURNAL},
    {"label": "Litera, the medium is the message 📰", "value": dbc.themes.LITERA},
    {"label": "Lumen, light and shadow ☀️/🌑", "value": dbc.themes.LUMEN},
    {"label": "Lux, a touch of class 👔", "value": dbc.themes.LUX},
    {"label": "Materia, material is the metaphor 📖", "value": dbc.themes.MATERIA},
    {"label": "Minty, a fresh feel 🍭", "value": dbc.themes.MINTY},
    {"label": "Morph, a neomorphic layer 🧬", "value": dbc.themes.MORPH},
    {"label": "Pulse, a trace of purple 💜", "value": dbc.themes.PULSE},
    {"label": "Quartz, a glassmorphic layer 🪟", "value": dbc.themes.QUARTZ},
    {"label": "Sandstone, a touch of warmth 🏜️", "value": dbc.themes.SANDSTONE},
    {"label": "Simplex, mini and minimalist ▫️", "value": dbc.themes.SIMPLEX},
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

        # --> Navbar <-- #
        dbc.Navbar([
            dbc.Container([
                html.A([
                    html.Img(src=r"/assets/images/ChartLogo.png", height="40px", className="me-2")
                ], href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse([
                    html.Div([
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
                        ]),
                        html.Div([
                            ThemeChangerAIO(aio_id="theme", 
                                            radio_props={"value":dbc.themes.LUX, "options":themes_options}, 
                                            button_props={"className":"px-1 py-0 rounded"},
                                            offcanvas_props={"title":"Select a theme!", "style":{"width":"27%"}}
                                            )
                        ], className="theme-change-flex d-flex justify-content-start align-items-center"),
                    ], className="navbar-flex d-flex flex-grow-1 justify-content-between")
                ], id="navbar-collapse", className="my-2", is_open=False, navbar=True)
            ], className="navbar-container ms-2 me-2", fluid=True)
        ], className="py-2 nav-fill w-100 border-start-0 border-end-0 border-2 bg-secondary shadow-sm", expand="md"),
        # --> <---#


        # --> Page Content <-- #
        html.Div([
            dash.page_container,
        ], className="d-flex flex-column flex-grow-1"),
        # --> <-- #

        
        # --> Interval Components <-- #
        html.Div([
            html.Div([
                dcc.Interval(
                    id="data_refresh_interval_component",
                    interval=30 * 60 * 1000,  # poll db every 30 minutes
                    n_intervals=0
                ),
                dcc.Store(id="data_refresh_signal"),
            ]),
        ]),
        # --> <-- #

        # --> Footer <-- #
        html.Footer([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(["Made with ❤️ & 🍵 by Winston"]),
                    ]),
                    html.Div(["Icons by Bootstrap Icons and Icons8"]),
                    html.Div([
                        html.A(html.I(className="bi bi-github me-1"), href="https://github.com/winston-edwin-chiong/slrpEV-data-dashboard", target="_blank"),
                        html.A(html.I(className="bi bi-linkedin ms-1"), href="https://www.linkedin.com/in/winstonechiong/", target="_blank"),
                    ], className="d-flex")
                ], className="d-flex flex-column justify-content-center align-items-center"),
            ], className="d-flex justify-content-center align-items-center")
        ], className="fs-6 mt-5 p-2 bg-light text-dark shadow-top"),
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
    prevent_initial_call=True
)
def data_refresh_interval(n):
    '''
    This callback polls the Redis database at regular intervals for data refresh. 
    '''
    return n

# --> <-- #


# running the app
if __name__ == '__main__':
    import logging 
    import pickle
    import pandas as pd
    from apscheduler.schedulers.background import BackgroundScheduler
    from datacleaning.FetchData import FetchData
    from datacleaning.CleanData import CleanData
    from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
    from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
    from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
    from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.INFO)
    logger = logging.getLogger('apscheduler')

    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('cron', minute=5, coalesce=True)
    def query_data():
        logger.info("Fetching data...")
        raw_data = FetchData.scan_save_all_records()

        logger.info("Cleaning data...")
        cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', hour="7,15,23")
    def forecast_daily():
        logger.info("Loading data...")
        data = pd.read_csv("data/dailydemand.csv", index_col="time", parse_dates=True)

        logger.info("Forecasting and saving daily demand...")
        best_params = pd.read_pickle("data/dailyparams.pkl")
        
        forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=55)
    def forecast_hourly():
        logger.info("Loading data...")
        data = pd.read_csv("data/hourlydemand.csv")

        logger.info("Forecasting and saving hourly demand...")
        best_params = pd.read_pickle("data/hourlyparams.pkl")

        forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=15, hour=3, day="1,15")
    def update_daily_params():
        logger.info("Loading data...")
        data = pd.read_csv("data/dailydemand.csv", index_col="time", parse_dates=True)

        logger.info("Cross validating daily forecast parameters...")
        params = DailyCrossValidator.cross_validate(data)


        logger.info("Saving parameters...")
        with open("data/dailyparams.pkl", "wb") as f:
            pickle.dump(params, f)

        logger.info("Clearing Forecasts...")
        CreateDailyForecasts.save_empty_prediction_df()

        logger.info("Forecasting daily demand...")
        forecast_daily()

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=20, hour=3, day="1,15")
    def update_hourly_params():
        logger.info("Loading data...")
        data = pd.read_csv("data/hourlydemand.csv", index_col="time", parse_dates=True)

        logger.info("Cross validating hourly forecast parameters...")
        params = HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data)

        logger.info("Saving parameters...")
        with open("data/hourlyparams.pkl", "wb") as f:
            pickle.dump(params, f)

        logger.info("Clearing Forecasts...")
        CreateHourlyForecasts.save_empty_prediction_df()

        logger.info("Forecasting hourly demand...")
        forecast_hourly()

        logger.info("Done!")

    scheduler.start()
    app.run_server()
