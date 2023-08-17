import pandas as pd
import statsmodels.api as sm
import os


class CreateDailyForecasts:

    columns = ["avg_power_demand_W", "energy_demand_kWh", "peak_power_W"]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'data'))
    csv_path = os.path.join(data_folder, 'dailyforecasts.csv')

    def __init__():
        pass

    @classmethod
    def run_daily_forecast(cls, df, best_params: dict):

        try: 
            existing_forecasts = pd.read_csv("data/dailyforecasts.csv", index_col="time", parse_dates=True)
        except:
            existing_forecasts = pd.DataFrame()

        new_forecasts = pd.DataFrame()

        for column in cls.columns:

            # train on ALL available data
            train = df[[column]].copy()

            # create ARIMA model
            best_model_arima = sm.tsa.arima.ARIMA(train, order=best_params.get(column).get("order"), seasonal_order=best_params.get(column).get("seasonal_order")).fit()

            # forecast on day ahead, convert to a dataframe
            one_column_forecast = best_model_arima.forecast(7)
            one_column_forecast = pd.DataFrame(one_column_forecast)
            one_column_forecast.rename(columns={one_column_forecast.columns[0]: column+'_predictions'}, inplace=True)
            new_forecasts = pd.concat([new_forecasts, one_column_forecast], axis=1)
            new_forecasts.index.name = "time"

        # append new forecasts existing set of forecasts
        forecasts = pd.concat([existing_forecasts, new_forecasts], axis=0).resample("1D").last()  # get more recent forecast
        forecasts.to_csv(cls.csv_path)

        return forecasts

    @classmethod
    def save_empty_prediction_df(cls):
        empty_df = pd.DataFrame(columns=["avg_power_demand_W_predictions", "energy_demand_kWh_predictions", "peak_power_W_predictions"], index=pd.Index([], name="time"))
        empty_df.to_csv(cls.csv_path)
        return empty_df

