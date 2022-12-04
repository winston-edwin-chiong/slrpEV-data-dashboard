import pandas as pd
from cleaningpipeline import *
from sklearn.pipeline import Pipeline
from cleaning_utils import resample_df   

# create pipelines
pipe= Pipeline([
    ("clean_session", CleanSession()),
    ("clean_time", ExtractUpsampleGroupby5Min()),
    ("day_name", OHEOnlyDayName()),
    ("create_energy_peak_power", CreateEnergyAndPeakPowerDemand())
])

# load raw data
raw_data = pd.read_csv("data/slrpEV11052020-09222022.csv")

# clean data 
fivemindemand = pipe.fit_transform(raw_data)

# create different granularities
hourlydemand = resample_df(fivemindemand, "1H",)
dailydemand = resample_df(fivemindemand, "24H") 
monthlydemand = resample_df(fivemindemand, "1M")


# save to csv
fivemindemand.to_csv("data/5mindemand.csv")
hourlydemand.to_csv("data/hourlydemand.csv")
dailydemand.to_csv("data/dailydemand.csv")
monthlydemand.to_csv("data/monthlydemand.csv")