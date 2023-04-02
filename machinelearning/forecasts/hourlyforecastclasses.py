from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


class HourlyForecast(BaseEstimator, TransformerMixin):

    columns = ["avg_power_demand_W", "energy_demand_kWh", "peak_power_W"]

    def __init__(self, best_params: dict) -> None:
        super().__init__()
        self.best_params = best_params

    def fit(self, X, y=None):
        return X

    def transform(self, X, y=None):

        for column in self.columns:
            # get params
            params = self.best_params.get(column)
            # create regressor and features w/ optimal parameters
            regressor = KNeighborsRegressor(
                n_neighbors=params["best_n_neighbors"])
            df = X[[column]].copy()
            df = self.__create_lag_features(df,params["best_depth"], col_name=column)
            X_train, X_test, y_train, y_test = self.__train_test_split(
                df, column)
            regressor.fit()

        return {"training": "data", "test": "data"}

    @staticmethod
    def __train_test_split(df, column_name):
        '''
        Withhold only the last two weeks of data for model performance.
        '''

        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(columns=column_name),
            df[[column_name]],
            test_size=336,  # hours in two weeks
            shuffle=False
        )
        return X_train, X_test, y_train, y_test

    @staticmethod
    def __create_lag_features(df, num_lag_depths, col_name):
        df_with_lags = df.copy(deep=True)
        for lag_depth in np.arange(1, num_lag_depths+1):
            column = df_with_lags[col_name].shift(24*lag_depth)
            df_with_lags = pd.concat([df_with_lags, column.rename("lag" + f"{lag_depth}")], axis=1)
        return df_with_lags.dropna()
