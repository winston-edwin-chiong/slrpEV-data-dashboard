from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta


class SortDropCastSessions(BaseEstimator, TransformerMixin):
    """
    This pipeline step will sort values by field `connectTime`,
    drop columns `user_email`, `slrpPaymentId`, 
    and cast columns `cumEnergy_Wh`, `peakPower_W` as float values.
    This pipeline step will drop any records that contain 0 for 
    `peakPower_W` or `cumEnergy_Wh`. 
    Time-based columns will be converted into pandas timedate-like.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:

        X["cumEnergy_Wh"] = X["cumEnergy_Wh"].astype(float)
        X["peakPower_W"] = X["peakPower_W"].astype(float)
        X["userId"] = X["userId"].astype(str)

        X["connectTime"] = pd.to_datetime(X["connectTime"])
        X["startChargeTime"] = pd.to_datetime(X["startChargeTime"])
        X["Deadline"] = pd.to_datetime(X["Deadline"])
        X["lastUpdate"] = pd.to_datetime(X["lastUpdate"])

        X = X.loc[(X["peakPower_W"] != 0) & (X["cumEnergy_Wh"] != 0)].copy()

        X = X.sort_values(by="connectTime").drop(columns=["user_email", "slrpPaymentId"]).reset_index(drop=True)

        return X


class HelperFeatureCreation(BaseEstimator, TransformerMixin):
    """
    This pipeline step will drop any records that contain 0 for 
    `peakPower_W` or `cumEnergy_Wh`. Four additional columns will be created:
    `finishChargeTime`, `true_peakPower_W`, `Overstay`, and `Overstay_h`. 
    Any records with calculated charging durations greater than a day will be dropped. 
    This step accounts for inconsistencies in the slrpEV data. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:

        X["finishChargeTime"] = X["lastUpdate"]
        X["true_peakPower_W"] = round(X["cumEnergy_Wh"] / X["DurationHrs"], 0)

        X = X[X["finishChargeTime"] >= datetime.now(pytz.timezone('US/Pacific')).strftime("%D")].copy()

        # filter out bad rows (this occurs when there is a very low peak power and high energy delivered). also filter out excessively high duration from raw data
        X = X.loc[X["DurationHrs"] <= 24].copy()
        X = X[~(X["Duration"].str[0].astype(int) >= 2)]

        X['temp_0'] = pd.Timedelta(days=0, seconds=0)
        X['Overstay'] = X["lastUpdate"] - X['Deadline']
        X["Overstay"] = X[["Overstay", "temp_0"]].max(axis=1)
        X['Overstay_h'] = X['Overstay'].dt.seconds / 3600
        X.drop(columns=['temp_0'], inplace=True)

        return X

    @staticmethod
    def __get_duration(row):
        """
        This helper function calculates the charging duration of a session. 
        The calculation is `lastUpdate - startChargeTime`. 
        """
        return round(((row["lastUpdate"] - row["startChargeTime"]).seconds/3600), 3)

    @staticmethod
    def __get_finishChargeTime(row):
        """
        This helper function calculates the finished charge time of a session. If the session is `REGULAR`, 
        the finish charge time is `lastUpdate`. If the session is `SCHEDULED`, the finish charge time is `Deadline`.
        DEPRECATED: Currently, every session finishes at `lastUpdate` becaused SCHEDULED sessions can end early.
        """        
        if row["regular"] == 1:
            return row["lastUpdate"]
        else:
            return row["Deadline"]


class CreateNestedSessionTimeSeries(BaseEstimator, TransformerMixin):
    """
    This pipeline step will create a time series for each session TODAY. Two new columns will be created, 
    `time_vals` and `power_vals`, respective lists for time and power demand. `time_vals` are rounded to the 
    closest 5 min. The dataframe is optionally saved to a `data/` file.
    """

    def __init__(self, save=False) -> None:
        self.save = save
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        self.ts_df = pd.DataFrame(columns=["time_vals", "power_vals"])

        X.apply(self.__create_ts, axis=1)

        X = pd.concat([X.reset_index(), self.ts_df], axis=1)

        X = X.explode(["time_vals", "power_vals"])
        X.rename(columns={"time_vals": "Time", "power_vals": "Power (W)"}, inplace=True)

        X = X[(X["Time"] >= datetime.now(pytz.timezone('US/Pacific')).strftime("%D"))].copy()  # keep sessions within today

        # for scheduled charging, values are simulated; return up to current time to feel like dashboard is in "real time"
        now = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')
        now = pd.to_datetime(now).floor("5T").strftime('%Y-%m-%d %H:%M:%S')
        X = X[X["Time"] <= now].copy()

        if self.save:
            X.to_csv("data/todays_sessions.csv")

        return X

    def __create_ts(self, session: pd.Series) -> pd.DataFrame:
        """
        This helper function takes a row, and using the `startChargeTime` and `finishChargeTime` columns, fills in a time series
        at five minute granularity.
        """

        date_range = pd.date_range(start=session["startChargeTime"].round("5MIN"), end=session["finishChargeTime"].round("5MIN"), freq="5min").to_list()
        power_vals = np.ones(len(date_range)) * session["true_peakPower_W"]

        temp_df = pd.DataFrame({"power": power_vals}, index=date_range)

        date_range = temp_df.index.to_list()
        power_vals = temp_df["power"].to_list()

        temp_df = pd.DataFrame([[date_range, power_vals]], columns=self.ts_df.columns)

        self.ts_df = pd.concat([self.ts_df, temp_df], ignore_index=True)

