from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


class kNNPredict(BaseEstimator, TransformerMixin):

    columns = ["avg_power_demand_W", "energy_demand_kWh", "peak_power_W"]

    def __init__(self, best_params: dict) -> None:
        super().__init__()
        self.best_params = best_params

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        # add 24 hours to end of data 
        X = self.__create_24hrs_future(X)
        # copy prediction interval
        forecasts = pd.DataFrame(index=X.index[-24:])

        for column in self.columns:
            # get params
            params = self.best_params.get(column)

            # create regressor
            regressor = KNeighborsRegressor(
                n_neighbors=params["best_n_neighbors"])
            
            # isolate column, create features
            df = X[[column]].copy()
            df = self.__create_lag_features(df,params["best_depth"], col_name=column)

            # split into training set and test set
            X_train, X_test, y_train, y_test = self.__train_test_split(df, col_name=column)

            # train regressor and predict 24 hours ahead
            regressor.fit(X_train, y_train)
            forecasts[column + "_predictions"] = regressor.predict(X_test).reshape(-1)

        return forecasts 


    @staticmethod
    def __create_24hrs_future(df):
        prediction_range = pd.DataFrame(index=df.index[-24:] + pd.Timedelta(hours=24), columns=df.columns)
        df = pd.concat([df, prediction_range])
        return df 

    @staticmethod
    def __create_lag_features(df, num_lag_depths, col_name):
        df_with_lags = df.copy(deep=True)
        for lag_depth in np.arange(1, num_lag_depths+1):
            column = df_with_lags[col_name].shift(24*lag_depth)
            df_with_lags = pd.concat([df_with_lags, column.rename("lag" + f"{lag_depth}")], axis=1)
        return df_with_lags.dropna(subset=df_with_lags.columns.drop(col_name)) # only rows with NaN as features, NaN in true value column is OK
    
    @staticmethod
    def __train_test_split(df, col_name):
        """
        Withhold the last 24 hours to predict the next 24 hours.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(columns=col_name),
            df[[col_name]],
            test_size=24, # withhold last 24 hours
            shuffle=False
        )
        return X_train, X_test, y_train, y_test
