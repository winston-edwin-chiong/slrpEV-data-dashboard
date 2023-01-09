import numpy as np 
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV

class kNNCrossValidate:
    granularity = 24
    col_quantity = "energy_demand_kWh"

    def __init__(self, max_depth, max_neighbors, data_path:str):
        self.max_depth = max_depth
        self.max_neighbors = max_neighbors
        self.data_path = data_path
        self.best_params = {
            "best_depth":None,
            "best_rmse":np.inf,
            "best_n_neighbors":None
        }

    def __create_df(self):
        demand_df = self.__prepare_TS(pd.read_csv(self.data_path))
        self.__kNN_df = self.__create_lag_features(demand_df, self.max_depth, self.granularity)
        return self.__kNN_df

    def __train_val_split(self):
        X_train, X_validation, y_train, y_validation = train_test_split(
            self.__kNN_df.drop(
                columns=[
                    self.col_quantity, "day", 
                ]
            ), 
            self.__kNN_df[[self.col_quantity]],
            test_size = 0.2, 
            shuffle=False            
        )
        return X_train, X_validation, y_train, y_validation

    def cross_validate(self):
        X_train, X_validation, y_train, y_validation = self.__train_val_split()
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
            cv=[(np.arange(0,len(X_train)), np.arange(len(X_train),len(self.__kNN_df)))]
        )
        grid.fit(X_train, y_train)

    def __create_lag_features(self, df, num_lag_depths, num_pts_per_day):
        """Function takes in a dataframe with a 'kWh' column at a below daily granularity, and returns a 
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
            column = with_lags_df["kWh"].shift(num_pts_per_day*lag_depth)
            with_lags_df = pd.concat([with_lags_df, column.rename("lag" + f"{lag_depth}")], axis=1)
        return with_lags_df.dropna()

    def __prepare_TS(self, df):
        """
        Function takes in a dataframe and sets the index to the "time" column, 
        changes that index to a pd.datetime-like object.
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
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