import time 
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from pandas.tseries.holiday import USFederalHolidayCalendar

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