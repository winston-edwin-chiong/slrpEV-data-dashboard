from kNNCrossValidator import kNNCrossValidator
from sklearn.neighbors import KNeighborsRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
import pandas as pd 
import numpy as np 

class GenerateOneHourlyDayAheadForecast(BaseEstimator, TransformerMixin):

    def __init__(self, granularity=24, best_depth=None, best_neighbors=None, max_depth=60, max_neighbors=20, training_pred=True) -> None:
        self.max_depth = max_depth
        self.max_neighbors = max_neighbors
        self.best_depth = best_depth
        self.best_neighbors = best_neighbors
        self.granularity = granularity 
        self.training_pred = training_pred
        super().__init__()

    def fit(self, X, y=None):

        # X = self.__prepare_TS(X) # Can be another step in the pipeline? 

        if self.best_depth == None and self.best_neighbors == None:
            # cross validate 
            CV = kNNCrossValidator(
                max_depth=self.max_depth,
                max_neighbors=self.max_neighbors,
                df=X,
                granularity=self.granularity
            )
            CV.cross_validate()
            self.best_depth, self.best_neighbors = CV.get_params()

        return self

    def transform(self, X):
        X = self.__append_forecast_index(X)
        # add features to dataframe
        X = self.__create_lag_features(
            df=X, 
            num_lag_depths=self.best_depth, 
            col_name=X.columns[0],
            num_pts_per_day=self.granularity,
            )
        # create estimator 
        estimator = KNeighborsRegressor(
            n_neighbors = self.best_neighbors,
            n_jobs=8
            )
        # train test split 
        X_train, X_test, y_train, y_test = self.__X_y_split(X)
        estimator.fit(X_train, y_train)
 
        return (pd.DataFrame(index=X_test.index, data={f"{X.columns[0]} forecast":estimator.predict(X_test).reshape(-1)}), self.best_depth, self.best_neighbors)
    
    def __X_y_split(self, df, test_days=7):
        """
        """
        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(columns=[df.columns[0]]),
            df[[df.columns[0]]],
            test_size = self.granularity*test_days, # last week of data
            shuffle=False
        )
        return X_train, X_test, y_train, y_test

    def __append_forecast_index(self, df, extra_days=1):
        """
        Adds extra datetime indicies at the end of a time series dataframe. 
        """
        appendage = pd.DataFrame(index=df.tail(24).index + pd.Timedelta(days=extra_days))
        return pd.concat([df, appendage])
    
    def __create_lag_features(self, df, num_lag_depths, col_name, num_pts_per_day):
        """
        Function takes in a dataframe at a below daily granularity, and returns a 
        new dataframe with lagged values; a "lag1" column will have the previous day's power demand at the same time, 
        a "lag2" column will have two days ago's power demand at the same time, etc. Function will drop rows with 
        any 'NaN' vlaues. 
        ~~~
        Parameters:
        df: Dataframe to append features.
        col_name: Column to use.
        num_lag_depths: Number of lagged features to create.
        num_pts_per_day: Number of data points per day. For example, an dataframe with one data point per hour will have one a parameter value of 24. 
        """
        
        with_lags_df = df.copy(deep=True)
        for lag_depth in np.arange(1,num_lag_depths+1):
            column = with_lags_df[col_name].shift(num_pts_per_day*lag_depth)
            with_lags_df = pd.concat([with_lags_df, column.rename("lag" + f"{lag_depth}")], axis=1)
        return with_lags_df.dropna(subset=with_lags_df.columns.drop(col_name))

    def __prepare_TS(self, df):
        """
        Function takes in a dataframe and sets the index to the "time" column, 
        changes that index to a pd.datetime-like object.
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df
