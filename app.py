import dash 
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

# app instantiation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI])

# app layout 
app.layout = html.Div([
    html.H1('Poverty And Equity Database',
            style={'color': 'blue',
                'fontSize': '40px'}),
    html.H2('The World Bank'),
    dbc.Tabs([
        dbc.Tab([
            html.Ul([
                html.Li('Number of Economies: 170'),
                html.Li('Temporal Coverage: 1974 - 2019'),
                html.Li('Update Frequency: Quarterly'),
                html.Li('Last Updated: March 18, 2020'),
                html.Li([
                'Source: ',
                    html.A('https://datacatalog.worldbank.org/dataset/poverty-and-equity-database', 
                    href='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database')
                    ])
                ])
            ], label='Key Facts'),
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li('Book title: Interactive Dashboards and Data Apps with Plotly and Dash'),
                html.Li(['GitHub repo: ', 
                    html.A('https://github.com/PacktPublishing/Interactive-Dashboards-and-Data-Apps-with-Plotly-and-Dash', 
                        href='https://github.com/PacktPublishing/Interactive-Dashboards-and-Data-Apps-with-Plotly-and-Dash')
                    ])
                ])
            ], label="TheDuJin")
        ])
    ])

# running the app
if __name__ == '__main__':
    app.run(debug=True)

