import dash 
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, "/about")

layout = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###

                ### --> Main Content <-- ###
                dbc.Col([

                    html.Div([
                        ### --> Dashboard Descripton & Contact <-- ###
                        html.Div([
                            dbc.Alert([
                                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                                "This app is still under development. There may be some bugs 🐛..."
                            ], color="warning"),
                            html.Br(),
                            html.P([
                                html.Span([
                                    "The intent of the app is to visualize and analyze slrpEV demand. ",
                                    "The chargers are located under the Recreational Sports Facility at ",
                                    html.Span("2301 Bancroft Way, Berkeley, CA 94720. ", className="fw-italic"),
                                    "Request access ",
                                    html.A("here!", href="https://docs.google.com/forms/d/e/1FAIpQLScuI2LUrPkxfU4BdbnnULyJVHb9HFTMBapTIs9EEWjCw6-tzQ/viewform", target="_blank", className="fw-bold text-info")
                                ])
                            ]),
                            html.Div([
                                html.Iframe(
                                    src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3149.6418529753005!2d-122.26615172369235!3d37.86866970674504!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x80857c27c74eb40f%3A0x78885a7266364a6!2sRSF%20Parking%20Garage%2C%20Berkeley%2C%20CA%2094704!5e0!3m2!1sen!2sus!4v1699501502910!5m2!1sen!2sus",
                                    style={"height": "50vh", "width": "50vw"}
                                    ),
                            ], className="d-flex justify-content-center my-2"),
                            html.Br(),
                            html.H3("FAQ"),
                            dbc.Accordion([
                                dbc.AccordionItem([
                                    html.P([
                                        html.Span([
                                            "Data from the physical chargers is stored on ",
                                            html.A("AWS DynamoDB", href="https://aws.amazon.com/dynamodb/", target="_blank", className="fw-bold text-info"),
                                            " and is updated every 5 minutes. ",
                                            "Data cleaning and machine learning tasks are executed on a schedule by ",
                                            html.A("Modal", href="https://modal.com/", target="_blank", className="fw-bold text-info"),
                                            " and results are sent to ",
                                            html.A("Redis", href="https://redis.io/", target="_blank", className="fw-bold text-info"),
                                            ", this app's primary database. ",                   
                                            "This app's frontend is built with ",
                                            html.A("Plotly Dash", href="https://dash.plotly.com/", target="_blank", className="fw-bold text-info"), 
                                            " and ",
                                            html.A("Bootstrap", href="https://getbootstrap.com/", target="_blank", className="fw-bold text-info"),
                                            ". The app is deployed on ",
                                            html.A("Render", href="https://render.com/", target="_blank", className="fw-bold text-info"),
                                            "."
                                            ]),
                                    ]),
                                ], title="How is this app built?"),
                                dbc.AccordionItem([
                                    html.P([
                                        html.Span([
                                            "Please reach out to me at ",
                                            html.A("winstonchiong@berkeley.edu", href="mailto:winstonchiong@berkeley.edu", className="fst-italic fw-bold text-info"),
                                            " ! I'm super happy to chat!"
                                        ])
                                    ]),
                                ], title="I have a suggestion, comment, question, or request!"),
                                dbc.AccordionItem([
                                    ### --> Mac <-- ###
                                    html.Div([
                                        dbc.Tooltip("This is Mac!", target="Mac", placement="right"),
                                        html.Img([
                                        ], src=r"assets/images/cat1.jpg", alt="Winston's cat", className="img-fluid rounded", id="Mac", style={"max-width": "30%"})
                                    ], className="d-flex justify-content-center")
                                    ### --> <-- ###
                                ], title="🐈?"),
                            ], start_collapsed=True),
                        ], className="text-start m-2"),
                        ### --> <-- ###

                    ], className="d-flex flex-column"),
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True)
    ])

