import time 
import numpy as np 
import pandas as pd
from app_utils import round_format_UNIX_time, ohe_day_name, ohe_federal_holiday

original_df = pd.read_csv("data/slrpEV11052020-09222022.csv")

pattern = r"(\[?\{'power_W':\sDecimal\(')|('timestamp':\sDecimal\(')|('\)\}?\]?)"
power_and_time = original_df["power"].str.replace(pattern, "", regex=True) # remove all pattern instances

power_and_time = power_and_time.str.split(', ')
power_and_time = power_and_time.apply(lambda lst: [int(val) for val in lst]) # cast all str value to int

power_vals = power_and_time.apply(lambda x: x[::2])
time_vals = power_and_time.apply(lambda x: x[1::2])

power_vals = power_vals.explode()
time_vals = time_vals.explode()

time_vals = time_vals.apply(round_format_UNIX_time)

temp = pd.DataFrame({"time": time_vals , "power_demand" : power_vals})
master_df = original_df.join(temp)

df_power_time = master_df[["time" , "power_demand"]]
df_power_time = df_power_time.groupby("time").sum()
df_power_time = df_power_time.sort_values(by = "time")

# resampling time series
df_power_time.index = pd.to_datetime(df_power_time.index)
df_power_time = df_power_time.resample("5min").sum()

df_power_time = ohe_day_name(df_power_time)
df_power_time = ohe_federal_holiday(df_power_time)

# save dataframe to data file
df_power_time.to_csv("data/5minpowerdemand.csv") # 5-min power demand

# create hourly energy demand
hourly_energy_demand_df = df_power_time.resample("1H").agg({"power_demand":"sum","day":"first",
                                                           "Monday":"first","Tuesday":"first","Wednesday":"first","Thursday":"first","Friday":"first",
                                                           "Saturday":"first","Sunday":"first",
                                                           "Federal Holiday":"first"})
hourly_energy_demand_df["power_demand"] = hourly_energy_demand_df["power_demand"]/1000
hourly_energy_demand_df["power_demand"] = hourly_energy_demand_df["power_demand"]/12 # convert to kWh
hourly_energy_demand_df.rename(columns={"power_demand":"energy_demand"}, inplace=True) 
hourly_energy_demand_df.to_csv("data/hourlyenergydemand.csv")