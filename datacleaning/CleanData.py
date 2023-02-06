from sklearn.pipeline import Pipeline
import pandas as pd
import datacleaning.pipelineclasses as pc
import datacleaning.sessionlevelcleaningclasses as sc


class CleanData:

    def __init__(self):
        pass

    @staticmethod
    def clean_save_raw_data():

        # load data
        __raw_data = pd.read_csv("data/raw_data.csv")

        # full time series pipeline
        __full_ts_pipeline = Pipeline(
            [
                ("sort_drop_cast", pc.SortDropCast()),
                ("create_helpers", pc.HelperFeatureCreation()),
                ("create_session_TS", pc.CreateSessionTimeSeries()),
                ("create_features", pc.FeatureCreation()),
                ("save_to_csv", pc.SaveToCsv()),
            ]
        )
        __full_ts_pipeline.fit_transform(__raw_data)

        # session level pipeline
        __session_lvl_pipeline = Pipeline(
            [
                ("sort_drop_cast", sc.SortDropCast()),
                ("create_helpers", sc.HelperFeatureCreation()),
                ("nested_ts", sc.CreateNestedSessionTimeSeries()),
                ("save_csv", sc.SaveCSV()),
            ]
        )
        __session_lvl_pipeline.fit_transform(__raw_data)
