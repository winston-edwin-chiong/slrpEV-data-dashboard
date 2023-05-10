import dash
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime 
from dash import html, dcc, dash_table
import dash_daq as daq
import redis
import pickle

dash.register_page(__name__, path="/data")

redis_client = redis.Redis(host='localhost', port=6360)

# load data
df = pickle.loads(redis_client.get("raw_data"))
# drop helper columns 
df = df.drop(
        columns=[
            "finishChargeTime",
            "trueDurationHrs",
            "true_peakPower_W",
            "Overstay",
            "Overstay_h"
        ]
    )
# filter data to only today's sessions 
df["connectTime"] = pd.to_datetime(df["connectTime"])
df = df.loc[df["connectTime"] > datetime.now().strftime("%D")]

layout = \
    html.Div([
        html.Div([
            dash_table.DataTable(data=df.to_dict("records"),
                                 columns=[{"name": i, "id": i}
                                          for i in df.columns],
                                 style_cell={
                "overflow": "hidden",
                "maxWidth": 200,
                "textOverflow": "ellipsis"
                },
                
            )
        ]),
    ])
