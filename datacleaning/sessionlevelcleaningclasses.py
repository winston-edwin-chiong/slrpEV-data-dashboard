from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd 
import numpy as np 


class SortDropCast(BaseEstimator, TransformerMixin):
    """
    This pipeline step will sort values by field "connectTime",
    drop columns "user_email", "slrpPaymentId", 
    and cast columns "cumEnergy_Wh", "peakPower_W" as float values. 
    """
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform(X) -> pd.DataFrame:
        X = X.sort_values(by="connectTime").drop(columns=["user_email", "slrpPaymentId"]).reset_index(drop=True)
        X["cumEnergy_Wh"] = X["cumEnergy_Wh"].astype(float)
        X["peakPower_W"] = X["peakPower_W"].astype(float)
        return X


class HelperFeatureCreation(BaseEstimator, TransformerMixin):
    """
    This pipeline step will drop any records that contain 0 for 
    "peakPower_W" or "cumEnergy_Wh". Two additional columns will be created:
    "reqChargeTime" and "finishChargeTime".
    """
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform(X) -> pd.DataFrame:
        X = X.loc[(X["peakPower_W"] != 0) & (X["cumEnergy_Wh"] != 0)]
        X = X.assign(reqChargeTime_h=(X["cumEnergy_Wh"] / X["peakPower_W"]))
        X = X.assign(connectTime=(pd.to_datetime(X["connectTime"])))
        X = X.assign(
            finishChargeTime=(X["connectTime"] + pd.to_timedelta(X['reqChargeTime_h'], unit='hours').round("s"))
        )
        return X 


class CreateNestedSessionTimeSeries(BaseEstimator, TransformerMixin):
    """
    This pipeline step will create a time series for each session. Two new columns will be created, 
    "time_vals" and "power_vals", respective lists for a time and power demand.
    """ 
    def __init__(self) -> None:
        self.ts_df = pd.DataFrame(columns=["time_vals", "power_vals"])
        super().__init__()
    
    def fit(self, X, y=None):
        return self 

    def transform(self, X) -> pd.DataFrame:
        X.apply(self.__create_ts, axis=1)
        X = pd.concat([X.reset_index(), self.ts_df], axis=1)
        return X

    def __create_ts(self, session):
        date_range = pd.date_range(start=session["connectTime"], end=session["finishChargeTime"], freq="5min").to_list()
        power_vals = np.ones(len(date_range)) * session["peakPower_W"]
        temp_df = pd.DataFrame([[date_range, power_vals]], columns=self.ts_df.columns)
        self.ts_df = pd.concat([self.ts_df, temp_df], ignore_index=True)


class FeatureCreation(BaseEstimator, TransformerMixin):
    """
    This pipeline step will create an "energy_demand_kWh" and "peak_power_W" column. 
    The name of the dataframe's index will be set to "time", and "day" and "month" columns 
    will be created. 
    """
    def fit(self, X, y=None):
        return self 

    @ staticmethod
    def transform(X) -> pd.DataFrame:
        X["energy_demand_kWh"] = (X["avg_power_demand_W"]/1000)/12
        # for the highest granularity, peak power is equal to the power demand
        # (different for different granularities though)
        X["peak_power_W"] = X["avg_power_demand_W"] 
        X.index.name = "time"
        X["day"] = X.index.day_name()
        X["month"] = X.index.month_name()
        return X
