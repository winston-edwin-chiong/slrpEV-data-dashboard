import logging
import pickle
import os
import pytz
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator

def START_SCHEDULER():

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.INFO)
    logger = logging.getLogger('apscheduler')

    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('cron', minute=35, coalesce=True)
    def query_data():
        logger.info("Fetching data...")
        raw_data = FetchData.scan_save_all_records()

        logger.info("Cleaning data...")
        cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', hour="7,15,23")
    def forecast_daily():
        logger.info("Loading data...")
        data = pd.read_csv("data/dailydemand.csv", index_col="time", parse_dates=True)

        logger.info("Forecasting and saving daily demand...")
        best_params = pd.read_pickle("data/dailyparams.pkl")
        
        forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=55)
    def forecast_hourly():
        logger.info("Loading data...")
        data = pd.read_csv("data/hourlydemand.csv")

        logger.info("Forecasting and saving hourly demand...")
        best_params = pd.read_pickle("data/hourlyparams.pkl")

        forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params)

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=15, hour=3, day="1,15")
    def update_daily_params():
        logger.info("Loading data...")
        data = pd.read_csv("data/dailydemand.csv", index_col="time", parse_dates=True)

        logger.info("Cross validating daily forecast parameters...")
        params = DailyCrossValidator.cross_validate(data)


        logger.info("Saving parameters...")
        with open("data/dailyparams.pkl", "wb") as f:
            pickle.dump(params, f)

        logger.info("Clearing Forecasts...")
        CreateDailyForecasts.save_empty_prediction_df()

        logger.info("Forecasting daily demand...")
        forecast_daily()

        logger.info("Done!")


    @scheduler.scheduled_job('cron', minute=20, hour=3, day="1,15")
    def update_hourly_params():
        logger.info("Loading data...")
        data = pd.read_csv("data/hourlydemand.csv", index_col="time", parse_dates=True)

        logger.info("Cross validating hourly forecast parameters...")
        params = HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data)

        logger.info("Saving parameters...")
        with open("data/hourlyparams.pkl", "wb") as f:
            pickle.dump(params, f)

        logger.info("Clearing Forecasts...")
        CreateHourlyForecasts.save_empty_prediction_df()

        logger.info("Forecasting hourly demand...")
        forecast_hourly()

        logger.info("Done!")

    scheduler.start()
