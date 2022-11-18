import pandas as pd
from pipeline import *
from sklearn.pipeline import Pipeline

# create pipelines
pipe_power = Pipeline([
    ("clean_session", CleanSession()),
    ("clean_time", ExtractUpsampleGroupby5Min()),
    ("holidays", OHEDaysHolidays()),
])

pipe_energy = Pipeline([
    ("clean_session", CleanSession()),
    ("clean_time", ExtractUpsampleGroupby5Min()),
    ("holidays", OHEDaysHolidays()),
    ("create_energy", CreateEnergyDemand())
])

# load raw data
raw_data = pd.read_csv("data/slrpEV11052020-09222022.csv")

# clean data 
fiveminpowerdemand = pipe_power.fit_transform(raw_data)
fiveminenergydemand = pipe_energy.fit_transform(raw_data)

# save to csv
fiveminpowerdemand.to_csv("data/5minpowerdemand.csv")
fiveminenergydemand.to_csv("data/5minenergydemand.csv")