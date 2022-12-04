import pandas as pd
from machinelearningpipeline import *
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsRegressor
from app_utils import set_index_and_datetime
from cleaningpipeline import OHEOnlyDayName

# load cleaned data
cleaned_data = set_index_and_datetime(pd.read_csv("data/hourlydemand.csv"))

# 
best_depth = 60

# ML pipeline
ml_pipe = Pipeline([
        ("append_24hour_ahead", Append24HourForecast(extra_days=1)),
        ("add_day_name", OHEOnlyDayName()),
        ("relevent_columns", ExtractHourlyEnergyDemand()),
        ("create_lags", CreateHourlyEnergyLags(best_depth)),
])

# preprocess data
preprocessed_data = ml_pipe.fit_transform(cleaned_data)
print(preprocessed_data)

# X_train and y_train 
# TODO: Overly complex; clean this up! It's fine for now tho. 
X_train = preprocessed_data.drop(columns=["energy_demand"]).iloc[:len(preprocessed_data)-48]
y_train = preprocessed_data["energy_demand"].iloc[:len(preprocessed_data)-48]
X_test = preprocessed_data.tail(48).drop(columns=["energy_demand"])

# 
best_num_neighbors = 20
kNNRegressor = KNeighborsRegressor(n_neighbors=best_num_neighbors)
kNNRegressor.fit(X_train, y_train)

# 
in_sample = pd.DataFrame(data={"energy_demand_predictions": kNNRegressor.predict(X_train).reshape(-1)}, index = X_train.index)
out_sample = pd.DataFrame(data={"energy_demand_predictions": kNNRegressor.predict(X_test).reshape(-1)}, index=X_test.index)

#
predictions_df = pd.concat([in_sample, out_sample])
predictions_df.to_csv("predictions/hourlydemandpredictions")