from sklearn.pipeline import Pipeline
from hourlyforecastclasses import kNNPredict

class CreateHourlyForecasts:

    def __init__():
        pass 
    
    @staticmethod
    def run_hourly_forecast(df, best_params: dict):

        hourly_forecast_pipeline = Pipeline([
            ("estimator", kNNPredict(best_params=best_params))
        ])
        forecasts = hourly_forecast_pipeline.fit_transform(df)

        return forecasts