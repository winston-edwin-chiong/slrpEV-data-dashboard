import pandas as pd 
from datetime import date
from fastapi import FastAPI
from dotenv import load_dotenv
from src.db.utils import db
from pydantic import BaseModel

### --> Helper Functions <-- ###
def query_date_df(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:

    if start_date is None and end_date is None:
        return df
    elif start_date is not None and end_date is None:
        return df.loc[(df.index >= start_date)]
    elif start_date is None and end_date is not None:
        return df.loc[(df.index <= end_date)]
    else:
        return df.loc[(df.index >= start_date) & (df.index <= end_date)]
### --> <-- ###


app = FastAPI()

load_dotenv()
r = db.get_redis_connection()


@app.get("/fivemindemand")
async def five_minute_demand(start: None = None, end: None = None):
    fivemindemand = db.get_df(r, "fivemindemand")
    fivemindemand = query_date_df(fivemindemand, start, end)
    return fivemindemand.to_json()


@app.get("/hourlydemand")
async def hourlydemand():
    hourlydemand = db.get_df(r, "hourlydemand")
    return hourlydemand.to_json()

@app.get("/dailydemand")
async def dailydemand(start: None = None, end: None = None):
    dailydemand = db.get_df(r, "dailydemand")
    dailydemand = query_date_df(dailydemand, start, end)
    return dailydemand.to_json()

@app.get("/monthlydemand")
async def monthlydemand():
    monthlydemand = db.get_df(r, "monthlydemand")
    return monthlydemand.to_json()


@app.get("/dailyforecasts")
async def dailyforecasts():
    dailyforecasts = db.get_df(r, "dailyforecasts")
    return dailyforecasts.to_json()


@app.get("/hourlyforecasts")
async def hourlyforecasts():
    hourlyforecasts = db.get_df(r, "hourlyforecasts")
    return hourlyforecasts.to_json()
