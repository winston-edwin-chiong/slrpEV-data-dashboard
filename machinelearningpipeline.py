import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

def create_energy_demand_lags(df, depth):
    """
    """
    hourly_energy_demand_with_lags_df = df.copy(deep=True)
    for lag_depth in np.arange(1, depth+1):
        hourly_energy_demand_with_lags_df["lag" + f"{lag_depth}"] = hourly_energy_demand_with_lags_df["energy_demand"].shift(24*lag_depth)
        
    # drops only rows with NaN features ("energy_demand" can be NaN, for future predictions)
    return hourly_energy_demand_with_lags_df.dropna(subset=hourly_energy_demand_with_lags_df.columns.drop("energy_demand"))

class Append24HourForecast(BaseEstimator, TransformerMixin):

    def __init__ (self, extra_days):
        super().__init__()
        self.extra_days = extra_days
    
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return pd.concat([X, pd.DataFrame(index=(X.tail(24).index + pd.Timedelta(days=self.extra_days)))])


class CreateHourlyEnergyLags(BaseEstimator, TransformerMixin):

    def __init__(self, depth):
        super().__init__()
        self.depth = depth

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return create_energy_demand_lags(X, depth=self.depth)


class ExtractHourlyEnergyDemand(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[["energy_demand"]]
