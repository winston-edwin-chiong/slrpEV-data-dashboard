import modal
import logging 
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from db.utils import db
from machinelearning.crossvalidation.DailyCrossValidator import DailyCrossValidator
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from machinelearning.crossvalidation.HourlyCrossValidator import HourlyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts


# create image
image = modal.Image.debian_slim().pip_install("pandas", "numpy", "redis", "boto3", "python-dotenv", "scikit-learn", "pmdarima", "statsmodels")

stub = modal.Stub()

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# query data
@stub.function(
        schedule=modal.Cron('55 * * * *'), 
        secret=modal.Secret.from_name("slrpEV-data-dashboard-ENVS"), 
        image=image,
        mounts=[modal.Mount.from_local_python_packages("datacleaning.FetchData", "datacleaning.CleanData", "db.utils")]
)
def query_data():
    r = db.get_redis_connection()

    logger.info("Fetching data...")
    raw_data = FetchData.scan_all_records()

    logger.info("Cleaning data...")
    cleaned_dataframes = CleanData.clean_save_raw_data(raw_data)

    logger.info("Serializiing data...")
    for key in cleaned_dataframes.keys():
        db.send_df_chunks(r, cleaned_dataframes.get(key), key)

    logger.info("Done!")


# validate model parameters
@stub.function(
        schedule=modal.Cron('5 3 1 * *'), 
        secret=modal.Secret.from_name("slrpEV-data-dashboard-ENVS"), 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.crossvalidation.DailyCrossValidator", 
            "machinelearning.forecasts.DailyForecast",
            "machinelearning.crossvalidation.HourlyCrossValidator",
            "machinelearning.forecasts.HourlyForecast",
            )]
        )
def update_params():
    r = db.get_redis_connection()

    ### DAILY PARAMETERS ###
    logger.info("Loading daily demand data...")
    data = db.get_df_chunks(r, "dailydemand")

    logger.info("Cross validating daily forecast parameters...")
    params = DailyCrossValidator.cross_validate(data)

    logger.info("Serializing data..")
    db.send_item(r, "dailyparams", params)

    logger.info("Clearing Forecasts...")
    db.send_item(r, "dailyforecasts", CreateDailyForecasts.get_empty_prediction_df())

    logger.info("Forecasting daily demand...")
    existing_forecasts = db.get_item(r, "dailyforecasts")
    forecasts = CreateDailyForecasts.run_daily_forecast(data, params, existing_forecasts)
    db.send_item(r, "dailyforecasts", forecasts)

    ### HOURLY PARAMETERS ###
    logger.info("Loading hourly demand data...")
    data = db.get_df_chunks(r, "hourlydemand")

    logger.info("Cross validating hourly forecast parameters...")
    params = HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data)

    logger.info("Serializing data...")
    db.send_item(r, "hourlyparams", params)

    logger.info("Clearing Forecasts...")
    db.send_item(r, "hourlyforecasts", CreateHourlyForecasts.get_empty_prediction_df())

    logger.info("Forecasting hourly demand...")
    existing_forecasts = db.get_item(r, "hourlyforecasts")
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, params, existing_forecasts)
    db.send_item(r, "hourlyforecasts", forecasts)


    logger.info("Done!")


# forecast hourly demand
@stub.function(schedule=modal.Cron('5 * * * *'), 
        secret=modal.Secret.from_name("slrpEV-data-dashboard-ENVS"), 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.forecasts.HourlyForecast",
            )]
        )
def forecast_hourly():
    r = db.get_redis_connection()

    logger.info("Loading data...")
    data = db.get_df_chunks(r, "hourlydemand")

    logger.info("Forecasting hourly demand...")
    best_params = db.get_item(r, "hourlyparams")
    existing_forecasts = db.get_item(r, "hourlyforecasts")
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params, existing_forecasts)

    logger.info("Serializing data...")
    db.send_item(r, "hourlyforecasts", forecasts)

    logger.info("Done!")


# forecast daily demand
@stub.function(schedule=modal.Cron('45 7,15,23 * * *'), 
        secret=modal.Secret.from_name("slrpEV-data-dashboard-ENVS"), 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.forecasts.DailyForecast",
            )]
        )
def forecast_daily():
    r = db.get_redis_connection()

    logger.info("Loading data...")
    data = db.get_df_chunks(r, "dailydemand")

    logger.info("Forecasting daily demand...")
    best_params = db.get_item(r, "dailyparams")
    existing_forecasts = db.get_item(r, "dailyforecasts")
    forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params, existing_forecasts)

    logger.info("Serializing data...")
    db.send_item(r, "dailyforecasts", forecasts)

    logger.info("Done!")

