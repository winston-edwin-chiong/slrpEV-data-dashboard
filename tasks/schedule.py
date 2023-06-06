import logging
import redis
import pickle
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts
from machinelearning.crossvalidation.HoulrlyCrossValidator import HourlyCrossValidator

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='localhost', port=6360)

app = Celery("tasks", broker="redis://localhost:6360")
app.conf.beat_schedule = {
    "fetch-clean-store-data": {
        "task": "fetch-clean-store-data",
        # update 5 minutes after the beginning of every hour
        "schedule": crontab(minute=5, hour="*")
    },
    "forecast-daily": {
        "task": "forecast-daily",
        # update at 7:30 and 23:30 every day
        "schedule": crontab(minute=44, hour="*")
    },
    "forecast-hourly": {
        "task": "forecast-hourly",
        # update 5 minutes before the start of every hour
        "schedule": crontab(minute=55, hour="*")
    },
    "update-daily-params": {
        "task": "update-daily-params",
        # update at Sunday 03:15 on the 1st and 15th every month
        "schedule": crontab(minute=15, hour=3, day_of_month="1,15")
    },
    "update-hourly-params": {
        "task": "update-hourly-params",
        # update at Sunday 03:20 on the 1st and 15th every month
        "schedule": crontab(minute=20, hour=3, day_of_month="1,15")
    }
}


@app.task(name="fetch-clean-store-data")
def query_data():
    logger.info("Fetching data...")
    raw_data = FetchData.scan_save_all_records()

    logger.info("Cleaning data...")
    cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

    logger.info("Serializiing data...")
    for key in cleaned_dataframes.keys():
        redis_client.set(key, pickle.dumps(cleaned_dataframes.get(key)))

    redis_client.set("last_updated_time", datetime.now().strftime('%H:%M:%S'))

    logger.info("Done!")


@app.task(name="forecast-daily")
def forecast_daily():
    logger.info("Loading data...")
    data = pickle.loads(redis_client.get("dailydemand"))

    logger.info("Forecasting daily demand...")
    best_params = pickle.loads(redis_client.get("daily_params"))
    forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params)

    logger.info("Serializing data...")
    redis_client.set("daily_forecasts", pickle.dumps(forecasts))

    logger.info("Done!")


@app.task(name="forecast-hourly")
def forecast_hourly():
    logger.info("Loading data...")
    data = pickle.loads(redis_client.get("hourlydemand"))

    logger.info("Forecasting hourly demand...")
    best_params = pickle.loads(redis_client.get("hourly_params"))
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params)

    logger.info("Serializing data...")
    redis_client.set("hourly_forecasts", pickle.dumps(forecasts))

    logger.info("Done!")


@app.task(name="update-daily-params")
def update_daily_params():
    logger.info("Loading data...")
    data = pickle.loads(redis_client.get("dailydemand"))

    logger.info("Cross validating daily forecast parameters...")
    params = DailyCrossValidator.cross_validate(data)

    logger.info("Serializing data..")
    redis_client.set("daily_params", pickle.dumps(params))

    logger.info("Clearing Forecasts...")
    CreateDailyForecasts.save_empty_prediction_df()

    logger.info("Forecasting daily demand...")
    forecast_daily()

    logger.info("Done!")


@app.task(name="update-hourly-params")
def update_hourly_params():
    logger.info("Loading data...")
    data = pickle.loads(redis_client.get("hourlydemand"))

    logger.info("Cross validating hourly forecast parameters...")
    params = HourlyCrossValidator(
        max_neighbors=25, max_depth=60).cross_validate(data)

    logger.info("Serializing data...")
    redis_client.set("hourly_params", pickle.dumps(params))

    logger.info("Clearing Forecasts...")
    CreateHourlyForecasts.save_empty_prediction_df()

    logger.info("Forecasting hourly demand...")
    forecast_hourly()

    redis_client.set("last_validated_time",
                     datetime.now().strftime('%m/%d/%y %H:%M:%S'))

    logger.info("Done!")


@beat_init.connect
def run_startup_tasks(**kwargs):
    if not redis_client.get("raw_data"):
        query_data()

    if not redis_client.get("daily_params"):
        update_daily_params()

    if not redis_client.get("hourly_params"):
        update_hourly_params()

    if not redis_client.get("daily_forecasts"):
        forecast_daily()

    if not redis_client.get("hourly_forecasts"):
        forecast_hourly()
