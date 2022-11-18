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

def resample_df(df, granularity):
    
    return 