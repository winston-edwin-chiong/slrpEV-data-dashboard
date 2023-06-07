import pandas as pd
from sklearn.model_selection import train_test_split
import pmdarima as pm


# Main Class
class DailyCrossValidator:

    columns = ["energy_demand_kWh", "peak_power_W"]

    @classmethod
    def cross_validate(cls, df):

        best_params = {}

        for column in cls.columns:
            # initalize cross validator, cross validate
            params = SARIMACrossValidator(column).cross_validate_one(df)
            best_params[column] = params

        # same data, different units, so same parameters
        best_params["avg_power_demand_W"] = best_params["energy_demand_kWh"]

        return best_params


# Helper Class
class SARIMACrossValidator:

    test_size = 0.2

    def __init__(self, col_name):
        super().__init__()
        self.col_name = col_name

    def cross_validate_one(self, df: pd.DataFrame):

        X_train, X_test, y_train, y_test = self.__train_test_split(df)

        stepwise_fit = pm.auto_arima(y_train,
                                     start_p=0, start_q=0,
                                     max_p=3, max_q=3, max_Q=3, max_P=3,
                                     d=0, D=1, m=7,
                                     X=None,
                                     seasonal=True, trace=True, stepwise=True)

        return {"order": stepwise_fit.order, "seasonal_order": stepwise_fit.seasonal_order}

    def __train_test_split(self, df: pd.DataFrame):
        # take only needed column
        df = df[[self.col_name]]

        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(columns=[self.col_name]),
            df[[self.col_name]],
            test_size=self.test_size,
            shuffle=False
        )

        return X_train, X_test, y_train, y_test
