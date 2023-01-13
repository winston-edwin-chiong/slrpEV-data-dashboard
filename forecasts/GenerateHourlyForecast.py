from HourlyForecastOneColumn import *
from sklearn.pipeline import Pipeline

class GenerateHourlyForecasts():

    def __init__(self):
        self.__add_pipeline()
        self.data = self.__prepare_TS(pd.read_csv("data/hourlydemand.csv"))
        self.columns = self.data.columns
        self.prediction_dataframes = []

    def __add_pipeline(self):
        self.__pipeline = Pipeline(
            [
                ("generate_one_forecast", GenerateOneHourlyDayAheadForecast())
            ]
        )

    def generate_forecasts(self):
        for col_name in self.columns:
            data = self.data[[col_name]]
            one_prediction = self.__pipeline.fit_transform(data)
            self.prediction_dataframes.append(one_prediction)
        predictions = pd.concat([self.prediction_dataframes], axis=1)
        predictions._to_csv("forecasts/data/hourlypredictions")

    def __prepare_TS(self, df):
        """
        Function takes in a dataframe and sets the index to the "time" column, 
        changes that index to a pd.datetime-like object.
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df