import time 
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from pandas.tseries.holiday import USFederalHolidayCalendar
import plotly.graph_objects as go

def round_format_UNIX_time(time_value):
    """
    Function takes in a UNIX time value, and rounds this value up 5 minutes.
    The time value is then converted into the format 'year-month-day hour:minute'.
    """
    
    # round time up 5 minutes 
    time_value = time_value // (5 * 60) * (5*60) + (5*60)
    
    # format time value
    time_value = time.strftime('%Y-%m-%d %H:%M', time.localtime(time_value))
    
    return time_value 

def ohe_day_name(dataframe):
    """
    Function takes in dataframe with a datetime like index, and returns a new dataframe with a
    column 'day', which consists of the name of the day of the week, and one-hot encodes
    the day of the week, with column names "Monday", "Tuesday", "Wednesday", etc.
    """
    dataframe["day"] = dataframe.index.day_name()
    oh_enc = OneHotEncoder()
    temp = pd.DataFrame(oh_enc.fit_transform(dataframe[["day"]]).toarray(), columns = oh_enc.get_feature_names_out(), index = dataframe.index)
    temp.rename(columns={"day_Friday":"Friday", "day_Monday":"Monday","day_Saturday":"Saturday",
                        "day_Sunday":"Sunday","day_Thursday":"Thursday","day_Tuesday":"Tuesday",
                        "day_Wednesday":"Wednesday"},
                inplace = True)
    return pd.concat([dataframe , temp], axis = 1)

def ohe_federal_holiday(dataframe):
    """
    Function takes in a dataframe with a datetime like index, and returns a new dataframe with a column "Federal Holiday" added,
    which is one-hot encoded if the date is a federal holiday. 
    """
    copy = dataframe.copy(deep=True)
    calendar = USFederalHolidayCalendar()
    holidays = calendar.holidays(start=min(dataframe.index), end=max(dataframe.index))
    # round to midnight, compare to holidays index, cast Boolean values to binary
    copy["Federal Holiday"] = dataframe.index.normalize().isin(holidays).astype(int)
    return copy 

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

def resample_df(df, granularity, peak: bool = False):
    """
    Function takes in a dataframe with a demand unit (power or energy, assumed to be the first column), 
    and OHE-encoded calendar variables. Function will return a resampled dataframe, aggregated by sum or max.  
    For example, a dataframe representing 5-min power demand can be resampled to a new dataframe 
    representing hourly peak power demand. 
    """

    # convert to pd.resample type granularity argument
    convert_granularity = {
        '5-Min':'5min',
        'Hourly':"1H",
        'Daily':"24H",
        "Monthly":'1M',
    }

    if peak == True:
        df = df.resample(convert_granularity[granularity]).max()
        df.rename(columns={"power_demand":"peak_power_demand"}, inplace=True)
        return df 

    # sum will not return correct OHE variables, unlike max
    df = df.resample(convert_granularity[granularity]).agg({
        df.columns[0]:"sum","day":"first",
        "Monday":"first","Tuesday":"first",
        "Wednesday":"first","Thursday":"first",
        "Friday":"first","Saturday":"first",
        "Sunday":"first","Federal Holiday":"first", 
        })

    return df

def plot_time_series(df, granularity, quantity):
    """
    Function takes in a dataframe and returns figure of the plotted dataframe.
    """
    plot_specifics = {
    "Energy Demand": {
        "column_name":"energy_demand",
        "units_measurement":"(kWh)"
    },
    "Power Demand": {
        "column_name":"power_demand",
        "units_measurement":"(W)"
    },
    "Peak Power Demand": {
        "column_name":"peak_power_demand",
        "units_measurement":"(W)"
    },
}   
    plot_layout = plot_specifics[quantity]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[plot_layout["column_name"]],
            name=granularity + " " + quantity,
            hovertext=df["day"],
        )
)
    fig.update_layout(
        title=granularity + " " + quantity,
        xaxis_title="Time",
        yaxis_title=quantity + " " + plot_layout["units_measurement"]
    )

    return fig 