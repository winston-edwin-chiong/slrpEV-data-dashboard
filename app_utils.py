import pandas as pd
import plotly.graph_objects as go
import datetime

def query_date_df(df, start_date, end_date):
    """
    Function querys a dataframe based on a specified start date and end date. If any argument is None, 
    function will ignore those bounds Assumes dataframe has a datetime-like index. Start and end dates are 
    also assumed to be in the form 'mm-dd-yyy'.
    """
    if start_date == None and end_date == None:
        return df
    elif start_date != None and end_date == None:
        return df.loc[(df.index >= start_date)]
    elif start_date == None and end_date != None:
        return df.loc[(df.index <= end_date)]
    else:
        return df.loc[(df.index >= start_date) & (df.index <= end_date)]


def plot_time_series(df, granularity, quantity):
    """
    Function takes in a dataframe and returns figure of the plotted dataframe.
    """
    plot_specifics = {
    "energy_demand": {
        "column_name":"energy_demand",
        "units_measurement":"(kWh)",
        "cleaned_quantity": "Energy Demand"
    },
    "power_demand": {
        "column_name":"power_demand",
        "units_measurement":"(W)",
        "cleaned_quantity": "Average Power Demand"
    },
    "peak_power_demand": {
        "column_name":"peak_power_demand",
        "units_measurement":"(W)",
        "cleaned_quantity": "Peak Power Demand"
    },
} 
        
    plot_layout = plot_specifics[quantity]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[plot_layout["column_name"]],
            name=plot_layout["cleaned_quantity"] + " " + plot_layout["units_measurement"],
            hovertext=(df["day"] if granularity != "Monthly" else df.index.month_name()),
        )
)
    fig.update_layout(
        title=granularity + " " + plot_layout["cleaned_quantity"],
        xaxis_title="Time",
        yaxis_title=plot_layout["cleaned_quantity"] + " " + plot_layout["units_measurement"]
    )

    return fig 


def set_index_and_datetime(df):
    """
    Function takes in a dataframe with a column "time", and sets this column
    to the index, while converting the time column to datetime-like. 
    """
    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)
    return df 

def get_last_days_datetime(n=7):
    """
    """
    current_time = pd.to_datetime("today") - datetime.timedelta(days=7)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time 

def add_predictions(figure, start_date, end_date):
    """
    Function should add a predictions trace to the figure.
    Currently only supports hourly. TODO: Add other granularities.
    """
    predictions_df = set_index_and_datetime(pd.read_csv("predictions/hourlydemandpredictions"))
    predictions_df = query_date_df(predictions_df, start_date, end_date)
    figure.add_trace(
        go.Scatter(
            x=predictions_df.index,
            y=predictions_df["energy_demand_predictions"],
            name="Energy Demand Forecast",
            line={"dash":"dash"}
        )
    )
