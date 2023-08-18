import pandas as pd
import statsmodels.api as sm
import os


class CreateDailyForecasts:

    columns = ["avg_power_demand_W", "energy_demand_kWh", "peak_power_W"]

    def __init__():
        pass

    @classmethod
    def run_daily_forecast(cls, df: pd.DataFrame, best_params: dict, existing_forecasts: pd.DataFrame=pd.DataFrame()):
        '''
        df: Dataframe with training data.
        best_params: Dictionary with best parameters for each column.
        existing_forecasts: Dataframe with existing forecasts.
        '''

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

        return forecasts

    @classmethod
    def get_empty_prediction_df(cls):
        empty_df = pd.DataFrame(columns=["avg_power_demand_W_predictions", "energy_demand_kWh_predictions", "peak_power_W_predictions"], index=pd.Index([], name="time"))
        return empty_df

