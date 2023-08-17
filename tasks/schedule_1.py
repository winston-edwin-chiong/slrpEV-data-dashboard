import logging
import pickle
import os
import pytz
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator
from db.utils import db

def start_scheduler():

    logger = logging.getLogger(__name__)
    load_dotenv()

    r = db.get_redis_connection()

    sched = BackgroundScheduler()

    @sched.scheduled_job('cron', day_of_week='mon-sun', minute=8)
    def query_data():
        logger.info("Fetching data...")
        raw_data = FetchData.scan_save_all_records()

        logger.info("Cleaning data...")
        cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

        logger.info("Serializiing data...")
        for key in cleaned_dataframes.keys():
            db.send_chunks(r, cleaned_dataframes.get(key), key)

        r.set("last_updated_time", datetime.now(pytz.timezone("America/Los_Angeles")).strftime('%H:%M:%S'))

        logger.info("Done!")


    @sched.scheduled_job('cron', day_of_week='mon-sun', minute=45)
    def forecast_daily():
        logger.info("Loading data...")
        data = db.get_chunks(r, "dailydemand")

        logger.info("Forecasting daily demand...")
        best_params = db.get_item(r, "daily_params")
        forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params)

        logger.info("Serializing data...")
        r.set("dailyforecasts", pickle.dumps(forecasts))

        logger.info("Done!")

    @sched.scheduled_job('cron', day_of_week='mon-sun', minute=55)
    def forecast_hourly():
        logger.info("Loading data...")
        data = db.get_chunks(r, "hourlydemand")

        logger.info("Forecasting hourly demand...")
        best_params = db.get_item(r, "hourly_params")
        forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params)

        logger.info("Serializing data...")
        r.set("hourlyforecasts", pickle.dumps(forecasts))

        logger.info("Done!")

    sched.start()
