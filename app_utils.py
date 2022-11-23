import pandas as pd
import plotly.graph_objects as go

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
            name=plot_layout["cleaned_quantity"] + " " + plot_layout["cleaned_quantity"],
            hovertext=(df["day"] if granularity != "Monthly" else df.index.month_name()),
        )
)
    fig.update_layout(
        title=granularity + " " + plot_layout["cleaned_quantity"],
        xaxis_title="Time",
        yaxis_title=plot_layout["cleaned_quantity"] + " " + plot_layout["units_measurement"]
    )

    return fig 


def resample_df(df, granularity):
    """
    Function takes in a dataframe with columns "power_demand", "energy_demand",
    "peak_power", and "day". Given a pd.resample()-like resample code (ex. "5min", "1H", "24H", "1M", etc.),
    returns the resampled dataframe where "power_demand" is aggregated by mean, "energy_demand" is aggregated by sum, and
    "peak_power" is aggregated by max. 
    """

    df = df.resample(granularity).agg(
        {
            "power_demand": "mean",
            "energy_demand": "sum",
            "peak_power_demand": "max",
            "day": "first"
        }
    )

    return df 


def set_index_and_datetime(df):
    """
    Function takes in a dataframe with a column "time", and sets this column
    to the index, while converting the time column to datetime-like. 
    """
    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)
    return df 

def calculate_n_day_rollings(df):
    current_time = pd.to_datetime("today")
    return
