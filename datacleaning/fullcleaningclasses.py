from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import pytz
from datetime import datetime


class SortDropCast(BaseEstimator, TransformerMixin):
    """
    This pipeline step will sort values by field `connectTime`,
    drop columns `user_email`, `slrpPaymentId`, 
    and cast columns `cumEnergy_Wh`, `peakPower_W` as float values. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        X = X.sort_values(by="connectTime").drop(columns=["user_email", "slrpPaymentId"]).reset_index(drop=True)
        X["cumEnergy_Wh"] = X["cumEnergy_Wh"].astype(float)
        X["peakPower_W"] = X["peakPower_W"].astype(float)
        return X


class HelperFeatureCreation(BaseEstimator, TransformerMixin):
    """
    This pipeline step will drop any records that contain 0 for 
    `peakPower_W` or `cumEnergy_Wh`. Four additional columns will be created:
    `finishChargeTime`, `trueDurationHrs`, `true_peakPower_W`, `Overstay`, and `Overstay_h`. 
    Any records with calculated charging durations greater than a day will be dropped. 
    This step accounts for inconsistencies in the slrpEV data. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        # filter out rows where peakPower_W and cumEnergy_Wh contain bad (0) values
        X = X.loc[(X["peakPower_W"] != 0) & (X["cumEnergy_Wh"] != 0)].copy(deep=True)

        # cast dates to pandas datetime
        X["connectTime"] = pd.to_datetime(X["connectTime"])
        X["startChargeTime"] = pd.to_datetime(X["startChargeTime"])
        X["Deadline"] = pd.to_datetime(X["Deadline"])
        X["lastUpdate"] = pd.to_datetime(X["lastUpdate"])

        X["finishChargeTime"] = X.apply(self.__get_finishChargeTime, axis=1)
        X["trueDurationHrs"] = X.apply(self.__get_duration, axis=1)
        # "cumEnergy_Wh" is seen as a column of truth
        X["true_peakPower_W"] = round(X["cumEnergy_Wh"] / X["trueDurationHrs"], 0)

        # filter out bad rows (this occurs when there is a very low peak power and high energy delivered)
        # also filter out excessively high duration from raw data
        X = X.loc[X["trueDurationHrs"] <= 24].copy()
        X = X[~(X["Duration"].str[0].astype(int) >= 2)]

        # calculate overstay 
        X['temp_0'] = pd.Timedelta(days=0, seconds=0)
        X['Overstay'] = X["lastUpdate"] - X['Deadline']
        X["Overstay"] = X[["Overstay", "temp_0"]].max(axis=1)
        X['Overstay_h'] = X['Overstay'].dt.seconds / 3600

        X.drop(columns=['temp_0'], inplace=True)

        return X

    @staticmethod
    def __get_duration(row):
        """
        This helper function calculates the charging duration of a session. If the session is `REGULAR`,
        the calculation is `lastUpdate - startChargeTime`. If the session is `SCHEDULED`, the calculation is 
        `Deadline - startChargeTime`. 
        """
        if row["regular"] == 1:
            return round(((row["lastUpdate"] - row["startChargeTime"]).seconds/3600), 3)
        else:
            return round(((row["Deadline"] - row["startChargeTime"]).seconds/3600), 3)

    @staticmethod
    def __get_finishChargeTime(row):
        """
        This helper function calculates the finished charge time of a session. If the session is `REGULAR`, 
        the finish charge time is `lastUpdate`. If the session is `SCHEDULED`, the finish charge time is `Deadline`.
        """
        if row["regular"] == 1:
            return row["lastUpdate"]
        else:
            return row["Deadline"]


class CreateSessionTimeSeries(BaseEstimator, TransformerMixin):
    """
    This pipeline step will create a time series for each session. A dataframe
    with 5-min granularity will be returned, with one column, `power_demand_W`.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        self.rows = []
        X.apply(self.__create_ts, axis=1)
        X = pd.concat(self.rows, axis=0).sort_index()
        X = X.resample("5MIN").sum()
        return X

    def __create_ts(self, session: pd.Series):
        """
        This helper function takes in a session, with a `connectTime`, `finishChargeTime`, and 
        a `peakPower_W` column. Function will return a time series at 5-min granularity. 
        """
        date_range = pd.date_range(start=session["startChargeTime"].round("5MIN"), end=session["finishChargeTime"].round("5MIN"), freq="5min")
        temp_df = pd.DataFrame(index=date_range)
        temp_df["avg_power_demand_W"] = session["true_peakPower_W"]  # rename
        self.rows.append(temp_df)


class ImputeZero(BaseEstimator, TransformerMixin):
    """
    The way the data is pulled means data is only updated when there is a session ongoing. This class imputes zero 
    to makes the data feel like it's in real time. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        # get start and end dates
        start = X.index[-1]
        end = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')
        end = pd.to_datetime(end).floor("5T").strftime('%Y-%m-%d %H:%M:%S')

        if str(start) == end:  # data up to date
            return X

        # "missing chunk"
        missing_dates = pd.date_range(start=X.index[-1], end=end, freq="5MIN", inclusive="right")
        missing = pd.DataFrame(index=missing_dates, columns=["avg_power_demand_W"], data=0)  # impute zero
        imputed = pd.concat([X, missing], axis=0)
        # for scheduled charging, values are simulated; return up to current time to feel like dashboard is in "real time"
        return imputed[imputed.index <= end].copy()


class FeatureCreation(BaseEstimator, TransformerMixin):
    """
    This pipeline step will create an "energy_demand_kWh" and "peak_power_W" column. 
    The name of the dataframe's index will be set to `time`, and `day` and `month` columns 
    will be created. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        X["energy_demand_kWh"] = (X["avg_power_demand_W"]/1000)/12
        # for the highest granularity, peak power is equal to the power demand (different for different granularities though)
        X["peak_power_W"] = X["avg_power_demand_W"]
        X.index.name = "time"
        X["day"] = X.index.day_name()
        X["month"] = X.index.month_name()
        return X


class CreateGranularities(BaseEstimator, TransformerMixin):
    """
    This pipeline step takes each dataframe and creates new granularities--hourly, daily, and monthly.
    Returns a dictionary with all dataframes with keys: `fivemindemand`, `hourlydemand`, `dailydemand`, and `monthlydemand`.
    Each dataframe is optionally saved to a `data/` file. 
    """

    def __init__(self, save=False) -> None:
        self.agg_key = {
            "avg_power_demand_W": "mean",
            "energy_demand_kWh": "sum",
            "peak_power_W": "max",
            "day": "first",
            "month": "first"
        }
        self.dataframe_names = [
            "fivemindemand",
            "hourlydemand",
            "dailydemand",
            "monthlydemand"
        ]
        self.save = save
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> dict:
        # create new granularities
        hourlydemand = X.resample("1H").agg(self.agg_key)
        dailydemand = X.resample("1D").agg(self.agg_key)
        monthlydemand = X.resample("M").agg(self.agg_key)

        new_dataframes = {
            "fivemindemand": X,
            "hourlydemand": hourlydemand,
            "dailydemand": dailydemand,
            "monthlydemand": monthlydemand
        }

        # save to file system
        if self.save:
            for idx, dataframe in enumerate(new_dataframes.values()):
                dataframe.to_csv(f"data/{self.dataframe_names[idx]}.csv")

        return new_dataframes
