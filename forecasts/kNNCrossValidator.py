import numpy as np 
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV


class kNNCrossValidator:

    def __init__(self, max_depth, max_neighbors, df:pd.DataFrame, granularity:int):
        self.max_depth = max_depth
        self.max_neighbors = max_neighbors
        self.granularity = granularity
        self.__kNN_df = self.__create_df(df)
        self.best_params = {
            "best_depth":None,
            "best_n_neighbors":None
        }

    def __create_df(self, df):
        df = self.__create_lag_features(df, self.max_depth, self.granularity)
        return df

    def __X_y_split(self):
        X = self.__kNN_df.drop(
                columns=[
                    self.__kNN_df.columns[0] 
                ]
            ) 
        y = self.__kNN_df[[self.__kNN_df.columns[0]]]
        return X, y

    def cross_validate(self):
        X, y = self.__X_y_split()
        pipeline = Pipeline(
            [
                ("subset_features", SubsetLags()),
                ("estimator", KNeighborsRegressor())
            ]
        )
        params = {"estimator__n_neighbors":np.arange(1,self.max_neighbors+1), "subset_features__num_lags":np.arange(1,self.max_depth+1)}
        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=params,
            scoring="neg_mean_squared_error",
            n_jobs=6,
            verbose=0,
            cv=[(np.arange(0,int(0.8*len(self.__kNN_df))), np.arange(int(0.8*len(self.__kNN_df)), len(self.__kNN_df)))]
        )
        grid.fit(X, y)
        self.best_params["best_depth"] = grid.best_params_["estimator__n_neighbors"]
        self.best_params["best_n_neighbors"] = grid.best_params_["subset_features__num_lags"]

    def get_params(self):
        """
        Return order: best depth, best # of neighbors
        """
        return self.best_params["best_depth"], self.best_params["best_n_neighbors"]

    def __create_lag_features(self, df, num_lag_depths, num_pts_per_day):
        """Function takes in a dataframe at a below daily granularity, and returns a 
        new dataframe with lagged values; a "lag1" column will have the previous day's power demand at the same time, 
        a "lag2" column will have two days ago's power demand at the same time, etc. Function will drop rows with 
        any 'NaN' vlaues. 
        ~~~
        Parameters:
        df: Dataframe to append features.
        num_lag_depths: Number of lagged features to create.
        num_pts_per_day: Number of data points per day. For example, an dataframe with one data point per hour will have one a parameter value of 24. 
        """
        
        with_lags_df = df.copy(deep=True)
        for lag_depth in np.arange(1,num_lag_depths+1):
            column = with_lags_df[df.columns[0]].shift(num_pts_per_day*lag_depth)
            with_lags_df = pd.concat([with_lags_df, column.rename("lag" + f"{lag_depth}")], axis=1)
        return with_lags_df.dropna()

    def __prepare_TS(self, df):
        """
        Function takes in a dataframe and sets the index to the "time" column, 
        changes that index to a pd.datetime-like object.
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        if len(df.columns == 1):
            raise Exception("There should only be a prediction quantity. Dataframe must be Nx1!")
        return df

class SubsetLags(BaseEstimator, TransformerMixin):
    
    def __init__(self, num_lags=1):
        super().__init__()
        self.num_lags = num_lags
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return self.__select_subset_lags(X, self.num_lags)
        
    def __select_subset_lags(self, X, num_features):
        """Function takes in a dataframe with a 'energy_demand_kWh' column at select granularity with "lag1", "lag2",..., "lagN" features. 
        Function will select the first "num_features" of lags."""
        return X[[f"lag{depth}" for depth in np.arange(1, num_features+1)]]