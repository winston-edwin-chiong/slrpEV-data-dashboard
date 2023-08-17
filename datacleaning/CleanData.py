from sklearn.pipeline import Pipeline
import pandas as pd
import datacleaning.fullcleaningclasses as fcc
import datacleaning.sessionlevelcleaningclasses as scc


class CleanData:

    def __init__(self):
        pass

    @staticmethod
    def clean_save_raw_data(raw_data) -> dict:

        # full time series pipeline
        full_ts_pipeline = Pipeline(
            [
                ("sort_drop_cast", fcc.SortDropCast()),
                ("create_helpers", fcc.HelperFeatureCreation()),
                ("create_session_TS", fcc.CreateSessionTimeSeries()),
                ("impute_zero", fcc.ImputeZero()),
                ("create_features", fcc.FeatureCreation()),
                ("save_to_csv", fcc.SaveToCsv()),
            ]
        )
        cleaned_dataframes = full_ts_pipeline.fit_transform(raw_data)

        # today's sessions pipeline
        todays_sessions_pipeline = Pipeline(
            [
                ("sort_drop_cast", scc.SortDropCastSessions()),
                ("create_helpers", scc.HelperFeatureCreation()),
                ("nested_ts", scc.CreateNestedSessionTimeSeries()),
                ("save_csv", scc.SaveTodaySessionToCSV())
            ]
        )

        cleaned_dataframes["todays_sessions"] = todays_sessions_pipeline.fit_transform(raw_data)
        cleaned_dataframes["raw_data"] = pd.read_csv("data/raw_data.csv")

        return cleaned_dataframes
