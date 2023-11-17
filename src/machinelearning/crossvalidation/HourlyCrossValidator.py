import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.base import BaseEstimator, TransformerMixin


# Main Class
class HourlyCrossValidator:

    columns = ["energy_demand_kWh", "peak_power_W"]

    def __init__(self, max_neighbors, max_depth):
        self.max_neighbors = max_neighbors
        self.max_depth = max_depth

    def cross_validate(self, df):

        best_params = {}

        for column in self.columns:
            # initalize cross validator, cross validate
            params = kNNCrossValidator(self.max_neighbors, self.max_depth, column).cross_validate_one(df)
            best_params[column] = params

        # same data, different units, so same parameters
        best_params["avg_power_demand_W"] = best_params["energy_demand_kWh"]

        return best_params


# Helper Class
class kNNCrossValidator:

    test_size = 0.2

    def __init__(self, max_neighbors, max_depth, col_name):
        self.max_neighbors = max_neighbors
        self.max_depth = max_depth
        self.col_name = col_name

    def cross_validate_one(self, df) -> dict:
        # create features
        df = self.__create_all_lag_features(df)

        # create validation pipeline
        validation_pipeline = Pipeline([
            ("subset_features", SubsetLags()),
            ("estimator", KNeighborsRegressor())
        ])

        # create parameter grid
        params = {
            # start searching at 10 neighbors
            "estimator__n_neighbors": np.arange(10, self.max_neighbors+1),
            # start searching at 40 lags as features
            "subset_features__num_lags": np.arange(40, self.max_depth+1)
        }

        # split data into train, validation, and test
        X_train_validation, X_train, X_validation, X_test, y_train_validation, y_train, y_validation, y_test = self.__train_test_split(
            df)

        # create grid and iteratively search
        grid = GridSearchCV(
            estimator=validation_pipeline,
            param_grid=params,
            scoring="neg_mean_squared_error",
            verbose=4,
            cv=[(np.arange(0, len(X_train)), np.arange(len(X_train), len(X_train_validation)))]
        )
        grid.fit(X_train_validation, y_train_validation)
        # TODO: Instead of returning parameters, return the best model?
        best_params = {
            "best_depth": grid.best_params_["subset_features__num_lags"],
            "best_n_neighbors": grid.best_params_["estimator__n_neighbors"]
        }

        return best_params

    def __create_all_lag_features(self, df) -> pd.DataFrame:
        # create pipeline, pass data, create features
        pipeline = Pipeline([
            ("create_features", CreateLagFeatures(
                self.max_depth, self.col_name))
        ])
        df_with_features = pipeline.fit_transform(df)

        return df_with_features

    def __train_test_split(self, df):

        # split into train+validation and test
        X_train_validation, X_test, y_train_validation, y_test = train_test_split(
            df.filter(regex="lag"),  # select only "lag-" features
            df[[self.col_name]],
            test_size=self.test_size,
            shuffle=False  # time series split
        )

        # split into train and validation
        X_train, X_validation, y_train, y_validation = train_test_split(
            X_train_validation,
            y_train_validation,
            test_size=0.2,
            shuffle=False
        )

        return X_train_validation, X_train, X_validation, X_test, y_train_validation, y_train, y_validation, y_test


# Pipeline Classes
class CreateLagFeatures(BaseEstimator, TransformerMixin):
    """
    This pipeline step creates lag features into the training data.
    """

    def __init__(self, num_lag_depths, col_name):
        super().__init__()
        self.num_lags_depths = num_lag_depths
        self.col_name = col_name

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.__create_lag_features(X, self.num_lags_depths, self.col_name)

    @staticmethod
    def __create_lag_features(df, num_lag_depths, col_name):
        df_with_lags = df.copy(deep=True)
        for lag_depth in np.arange(1, num_lag_depths+1):
            column = df_with_lags[col_name].shift(24*lag_depth)
            df_with_lags = pd.concat(
                [df_with_lags, column.rename("lag" + f"{lag_depth}")], axis=1)
        return df_with_lags.dropna()


class SubsetLags(BaseEstimator, TransformerMixin):
    """
    This pipeline step subsets lag features of training data.
    """

    def __init__(self, num_lags=1):
        super().__init__()
        self.num_lags = num_lags

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.__select_subset_lags(X, self.num_lags)

    @staticmethod
    def __select_subset_lags(df, num_lags):
        return df[[f"lag{depth}" for depth in np.arange(1, num_lags+1)]]
