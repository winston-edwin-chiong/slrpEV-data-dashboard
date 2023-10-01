from sklearn.pipeline import Pipeline
import datacleaning.fullcleaningclasses as fcc
import datacleaning.todaysessioncleaningclasses as scc


class CleanData:
    """
    Clean raw slrpEV data from AWS DynamoDB. 
    """

    def __init__(self):
        pass

    @staticmethod
    def clean_raw_data(raw_data) -> dict:
        """
        This function cleans raw data slrpEV data and returns six cleaned dataframes in a dictionary with keys:
        `fivemindemand`, `hourlydemand`, `dailydemand`, `monthlydemand`, `todays_sessions`, `raw_data`.
        """

        # raw data pipeline (adds helper columns)
        raw_data_pipeline = Pipeline(
            [
                ("sort_drop_cast", fcc.SortDropCast()),
                ("create_helpers", fcc.HelperFeatureCreation()),
            ]
        )
        raw_data_w_helpers = raw_data_pipeline.fit_transform(raw_data)

        # full time series pipeline
        full_ts_pipeline = Pipeline(
            [
                ("sort_drop_cast", fcc.SortDropCast()),
                ("create_helpers", fcc.HelperFeatureCreation()),
                ("create_session_ts", fcc.CreateSessionTimeSeries()),
                ("impute_zero", fcc.ImputeZero()),
                ("create_features", fcc.FeatureCreation()),
                ("create_granularities", fcc.CreateGranularities()),
            ]
        )
        # fivemindemand, hourlydemand, dailydemand, monthlydemand are keys here
        cleaned_dataframes = full_ts_pipeline.fit_transform(raw_data)

        # today's sessions pipeline
        todays_sessions_pipeline = Pipeline(
            [
                ("sort_drop_cast", scc.SortDropCastSessions()),
                ("create_helpers", scc.HelperFeatureCreation()),
                ("nested_ts", scc.CreateNestedSessionTimeSeries()),
            ]
        )

        cleaned_dataframes["todays_sessions"] = todays_sessions_pipeline.fit_transform(raw_data)
        cleaned_dataframes["raw_data"] = raw_data_w_helpers

        return cleaned_dataframes
