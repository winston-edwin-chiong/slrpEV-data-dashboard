import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from app_utils import round_format_UNIX_time, ohe_day_name, ohe_federal_holiday

# Processing Pipeline Steps:
# - [1]  Use Regex to pattern match and clean each session
# - [1]  Separate power + time
# - [1]  Unnest power + time from each session
# - [1]  Round each to time even 5-minute intervals
# - [1]  Join w/ original df
# - [2]  Group by time (sessions happening at the same time)
# - [2]  Upsample to 5-min bins to impute 0’s where charging does not occur
# - [3]  OHE Add calendar variables (day, federal holiday)


class CleanSession(BaseEstimator, TransformerMixin):

    pattern = r"(\[?\{'power_W':\sDecimal\(')|('timestamp':\sDecimal\(')|('\)\}?\]?)"

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # TODO Create descriptive function documentation. Clean up complexity?
        # pattern match, remove pattern instances, cast to int
        power_and_time = X["power"].str.replace(self.pattern, "", regex=True)
        power_and_time = power_and_time.str.split(', ')
        power_and_time = power_and_time.apply(lambda lst: [int(val) for val in lst])

        # extract power and time values, unnest data, round time values to clean 5-minutes
        power_vals = power_and_time.apply(lambda x: x[::2]).explode()
        time_vals = power_and_time.apply(lambda x: x[1::2]).explode().apply(round_format_UNIX_time)

        # create df w/ time and power
        temp = pd.DataFrame({"time": time_vals, "power_demand": power_vals})

        # join w/ original dataframe
        return X.join(temp)


class ExtractUpsampleGroupby5Min(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # TODO Create descriptive function documentation. Clean up complexity?
        # extract time and power fields, group and sort
        new_X = X[["time", "power_demand"]]
        new_X = new_X.groupby("time").sum()
        new_X = new_X.sort_values(by="time")
        # upsample to 5-min bins, will impute 0 for missing times
        new_X.index = pd.to_datetime(new_X.index)
        new_X = new_X.resample("5min").sum()
        return new_X


class OnlyDayName(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # TODO Create descriptive function documentation.
        new_X = X.copy(deep=True)
        new_X.index = pd.to_datetime(new_X.index)
        new_X["day"] = new_X.index.day_name()
        return new_X

class OHEDaysHolidays(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # TODO Create descriptive function documentation.
        new_X = ohe_federal_holiday(X)
        new_X = ohe_day_name(new_X)
        return new_X


class CreateEnergyDemand(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # TODO Create descriptive function documentation.
        new_X = X.copy(deep=True)
        new_X["energy_demand"] = new_X["power_demand"]/1000 # convert to kW
        new_X["energy_demand"] = new_X["energy_demand"]/12 # convert to kWh
        return new_X
