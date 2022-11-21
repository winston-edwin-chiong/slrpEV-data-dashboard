import pandas as pd
from pipeline import *
from sklearn.pipeline import Pipeline

# create pipelines
pipe= Pipeline([
    ("clean_session", CleanSession()),
    ("clean_time", ExtractUpsampleGroupby5Min()),
    ("day_name", OnlyDayName()),
    ("create_energy", CreateEnergyDemand())
])

# load raw data
raw_data = pd.read_csv("data/slrpEV11052020-09222022.csv")

# clean data 
fivemindemand = pipe.fit_transform(raw_data)

# save to csv
fivemindemand.to_csv("data/5mindemand.csv")
