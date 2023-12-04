import pandas as pd 
from typing import Annotated, List
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from src.db.utils import db
from datetime import datetime, timedelta

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

# get column names for each df
col_names = {}
for df_name in ["fivemindemand", "hourlyforecasts", "chargers"]:
    df = db.get_df(r, df_name)
    col_names[df_name] = str(df.columns.to_list()).replace("'", "")[1:-1] # remove brackets and quotes


@app.get("demand/fivemindemand")
async def five_minute_demand(start: str = None, end: str = None, columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['fivemindemand']}`.")] = []):
    fivemindemand = db.get_df(r, "fivemindemand")
    fivemindemand = query_date_df(fivemindemand, start, end)

    if columns:
        fivemindemand = fivemindemand[columns]

    data = {
        "data": fivemindemand.to_json(),
        "start_date": start,
        "end_date": end
    }
    return data


@app.get("demand//hourlydemand")
async def hourly_demand(start: str = None, end: str = None, columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['fivemindemand']}`.")] = []):
    hourlydemand = db.get_df(r, "hourlydemand")
    hourlydemand = query_date_df(hourlydemand, start, end)

    if columns:
        hourlydemand = hourlydemand[columns]

    data = {
        "data": hourlydemand.to_json(),
        "start_date": start,
        "end_date": end
    } 
    return data

@app.get("demand//dailydemand")
async def daily_demand(start: str = None, end: str = None, columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['fivemindemand']}`.")] = []):
    dailydemand = db.get_df(r, "dailydemand")
    dailydemand = query_date_df(dailydemand, start, end)

    print(columns)
    if columns:
        dailydemand = dailydemand[columns]

    data = {
        "data": dailydemand.to_json(),
        "start_date": start,
        "end_date": end
    }
    return data


@app.get("demand//monthlydemand")
async def monthly_demand(start: str = None, end: str = None, columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['fivemindemand']}`.")] = []):
    monthlydemand = db.get_df(r, "monthlydemand")
    monthlydemand = query_date_df(monthlydemand, start, end)

    if columns:
        monthlydemand = monthlydemand[columns]

    data = {
        "data": monthlydemand.to_json(),
        "start_date": start,
        "end_date": end
    }
    return data


@app.get("forecasts/dailyforecasts")
async def daily_forecasts(columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['hourlyforecasts']}`.")] = []):
    dailyforecasts = db.get_df(r, "dailyforecasts")

    if columns:
        dailyforecasts = dailyforecasts[columns]

    data = {
        "data": dailyforecasts.to_json(),
        "start_date": dailyforecasts.index[0],
        "end_date": dailyforecasts.index[-1]
    }

    return data


@app.get("forecasts/hourlyforecasts")
async def hourly_forecasts(columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['hourlyforecasts']}`.")] = []):
    hourlyforecasts = db.get_df(r, "hourlyforecasts")

    if columns:
        hourlyforecasts = hourlyforecasts[columns]

    data = {
        "data": hourlyforecasts.to_json(),
        "start_date": hourlyforecasts.index[0],
        "end_date": hourlyforecasts.index[-1]
    }

    return data


@app.get("demand/chargers")
async def chargers(columns: Annotated[List[str], Query(description=f"Query select columns. Options are `{col_names['chargers']}`.")] = []):
    chargers = db.get_df(r, "chargers")

    current_time = pd.to_datetime("today")

    if columns:
        chargers = chargers[columns]
    
    data = {
        "data": chargers.to_json(),
        "time": current_time
    }

    return data
