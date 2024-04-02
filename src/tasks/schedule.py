import modal
import logging 
from datacleaning.FetchData import FetchData
from datacleaning.CleanData import CleanData
from db.utils import db
from machinelearning.crossvalidation.DailyCV import DailyCrossValidator
from machinelearning.forecasts.DailyForecast import CreateDailyForecasts
from machinelearning.crossvalidation.HourlyCV import HourlyCrossValidator
from machinelearning.forecasts.HourlyForecast import CreateHourlyForecasts


# create image
image = modal.Image.debian_slim().pip_install("pandas", "numpy", "redis", "boto3", "python-dotenv", "scikit-learn", "pmdarima", "statsmodels", "pyarrow", "fastparquet")

stub = modal.Stub()

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# query data
@stub.function(
        schedule=modal.Cron('0,10,20,30,40,50 * * * *'), 
        secrets=[modal.Secret.from_name("slrpEV-data-dashboard-ENVS")], 
        image=image,
        mounts=[modal.Mount.from_local_python_packages(
            "datacleaning.FetchData", 
            "datacleaning.CleanData", 
            "db.utils"
            )]
        )
def query_data():
    r = db.get_redis_connection()

    logger.info("Fetching slrpEV data from AWS DyanmoDB...")
    raw_data = FetchData.scan_all_records()

    logger.info("Cleaning slrpEV data...")
    cleaned_dataframes = CleanData.clean_raw_data(raw_data)

    logger.info("Serializiing data into parquet and sending to Redis...")
    for key in cleaned_dataframes.keys():
        db.send_df(r, cleaned_dataframes[key], key)

    logger.info("Done!")


# validate model parameters
@stub.function(
        schedule=modal.Cron('5 3 1 * *'), 
        secrets=[modal.Secret.from_name("slrpEV-data-dashboard-ENVS")], 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.crossvalidation.DailyCV", 
            "machinelearning.forecasts.DailyForecast",
            "machinelearning.crossvalidation.HourlyCV",
            "machinelearning.forecasts.HourlyForecast",
            )],
        timeout=600,
        retries=2
        )
def update_params():
    r = db.get_redis_connection()

    ### DAILY PARAMETERS ###
    logger.info("Loading daily demand data...")
    data = db.get_df(r, "dailydemand")

    logger.info("Cross validating daily forecast parameters...")
    params = DailyCrossValidator.cross_validate(data)

    logger.info("Pickling data and sending to Redis...")
    db.send_item(r, "dailyparams", params)

    logger.info("Clearing Forecasts...")
    db.send_df(r, CreateDailyForecasts.get_empty_prediction_df(), "dailyforecasts")

    logger.info("Forecasting daily demand...")
    forecasts = CreateDailyForecasts.run_daily_forecast(data, params)
    db.send_df(r, forecasts, "dailyforecasts")

    ### HOURLY PARAMETERS ###
    logger.info("Loading hourly demand data...")
    data = db.get_df(r, "hourlydemand")

    logger.info("Cross validating hourly forecast parameters...")
    params = HourlyCrossValidator(max_neighbors=25, max_depth=60).cross_validate(data)

    logger.info("Pickling data and sending to Redis...")
    db.send_item(r, "hourlyparams", params)

    logger.info("Clearing Forecasts...")
    db.send_df(r, CreateHourlyForecasts.get_empty_prediction_df(), "hourlyforecasts")

    logger.info("Forecasting hourly demand...")
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, params)
    db.send_df(r, forecasts, "hourlyforecasts")

    logger.info("Done!")


# forecast hourly demand
@stub.function(schedule=modal.Cron('15 * * * *'), 
        secrets=[modal.Secret.from_name("slrpEV-data-dashboard-ENVS")], 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.forecasts.HourlyForecast",
            )]
        )
def forecast_hourly():
    r = db.get_redis_connection()

    logger.info("Loading data...")
    data = db.get_df(r, "hourlydemand")

    if not db.get_item(r, "hourlyparams"):
        logger.info("No parameters found. Updating model parameters...")
        update_params()

    logger.info("Forecasting hourly demand...")
    best_params = db.get_item(r, "hourlyparams")
    existing_forecasts = db.get_df(r, "hourlyforecasts")
    forecasts = CreateHourlyForecasts.run_hourly_forecast(data, best_params, existing_forecasts)

    logger.info("Serializing data...")
    db.send_df(r, forecasts, "hourlyforecasts")

    logger.info("Done!")


# forecast daily demand
@stub.function(schedule=modal.Cron('45 7,15,23 * * *'), 
        secrets=[modal.Secret.from_name("slrpEV-data-dashboard-ENVS")], 
        image=image, 
        mounts=[modal.Mount.from_local_python_packages(
            "db.utils", 
            "machinelearning.forecasts.DailyForecast",
            )]
        )
def forecast_daily():
    r = db.get_redis_connection()

    logger.info("Loading data...")
    data = db.get_df(r, "dailydemand")

    if not db.get_item(r, "dailyparams"):
        logger.info("No parameters found. Updating model parameters...")
        update_params()

    logger.info("Forecasting daily demand...")
    best_params = db.get_item(r, "dailyparams")
    existing_forecasts = db.get_df(r, "dailyforecasts")
    forecasts = CreateDailyForecasts.run_daily_forecast(data, best_params, existing_forecasts)

    logger.info("Serializing data...")
    db.send_df(r, forecasts, "dailyforecasts")

    logger.info("Done!")

