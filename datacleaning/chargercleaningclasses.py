from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import pytz
from datetime import datetime

class CleanChargers(BaseEstimator, TransformerMixin):
    """
    This step will take in a raw data dataframe with helpers, and create 
    a new dataframe with rows `stationId`, `inUse`, `currChargingRate`, `choice`,
    `currPowerUtilRate`, `currOccupUtilRate`, `cumEnergy_Wh`, `todayEnergyDelivered`. 
    This dataframe details the current state of each charger. 
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:

        now = datetime.now(pytz.timezone('US/Pacific')).strftime("%D") # mm/dd/yyyy

        X = X[(X["siteId"] == 25)].copy() # Restrict to UC Berkeley

        # subset data to only current ongoing sessions
        # calculate the time difference (in minutes) between the `lastUpdate` column and the current time
        X["lastUpdate"] = pd.to_datetime(X["lastUpdate"]).dt.tz_localize('US/Pacific')
        X['time_difference'] = (datetime.now(pytz.timezone('US/Pacific')) - X['lastUpdate']).dt.total_seconds() / 60

        # *** Note that this padding is included due to Modal's data query from DynamoDB happening every 10 minutes, and AWS Lambda running every 5 minutes. 
        # *** In the worst case, Modal gets the data just before AWS Lambda executes (5 minutes behind), and you get the data right before Modal executes, 
        # *** i.e., 10 minutes after Modal last got the data, which was already 5 minutes behind, meaning data is 15 minutes behind reality. 
        # *** We'll do 16 just in case. 
        inuse = X[X['time_difference'] <= 16]

        # include handling for when a charger appears to be in use by two sessions; select more recent
        inuse = inuse.groupby("stationId").apply(lambda x: x.sort_values("lastUpdate", ascending=False).iloc[0]).reset_index(drop=True)

        inuse = inuse.drop(columns=['time_difference']).sort_values("lastUpdate", ascending=False)

        chargers = pd.DataFrame()

        # unique Chargers
        chargers["stationId"] = X["stationId"].unique()

        # chargers in use as `1` or `0``
        chargers["inUse"] = chargers["stationId"].isin(inuse["stationId"]).astype(int)

        # assume each charger is outputting power at the peak power rate 
        chargers = chargers.merge(inuse[["stationId", "true_peakPower_W"]].rename(columns={"true_peakPower_W": "currentChargingRate"}), on='stationId', how='left')

        # add choice
        chargers = chargers.merge(inuse[["stationId", "choice"]], on='stationId', how='left')

        # add vehicle model
        chargers = chargers.merge(inuse[["stationId", "vehicle_model"]], on='stationId', how='left')

        # add cumulative energy delivered by each charger 
        chargers = chargers.merge(X[["stationId", "cumEnergy_Wh"]].groupby("stationId").sum(), on='stationId', how='left')

        # add energy delivered by each charger today 
        chargers = chargers.merge(
            X[X["finishChargeTime"] >= now][["stationId", "cumEnergy_Wh"]].groupby("stationId").sum().rename(columns={"cumEnergy_Wh": "todayEnergy_Wh"}), 
            on='stationId', 
            how='left'
            )
        chargers["todayEnergy_Wh"] = chargers["todayEnergy_Wh"].fillna(0)

        # Today's Utilization Rate by Power:
        # assume each charger is rated at 6.6 kW 
        chargers = chargers.merge(
            X[X["finishChargeTime"] >= now][["stationId", "cumEnergy_Wh"]].groupby("stationId").sum().rename(columns={"cumEnergy_Wh": "currPowerUtilRate"}), 
            on='stationId', 
            how='left')
        chargers["currPowerUtilRate"] = (chargers["currPowerUtilRate"] / (6600 * 24)).fillna(0)

        # Today's Utilization Rate by Occupation:
        chargers = chargers.merge(
            X[X["finishChargeTime"] >= now][["stationId", "trueDurationHrs"]].groupby("stationId").sum().rename(columns={"trueDurationHrs": "currOccupUtilRate"}), 
            on='stationId', 
            how='left')
        chargers["currOccupUtilRate"] = (chargers["currOccupUtilRate"] / 24).fillna(0)

        return chargers
