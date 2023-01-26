from sklearn.pipeline import Pipeline
from datacleaning.pipelineclasses import *


class CleanData:

    def __init__(self):
        pass

    @staticmethod
    def clean_save_raw_data():

        # load data, create pipeline
        __raw_data = pd.read_csv("data/raw_data.csv")
        __pipeline = Pipeline(
            [
                ("sort_drop_cast", SortDropCast()),
                ("create_helpers", HelperFeatureCreation()),
                ("create_session_TS", CreateSessionTimeSeries()),
                ("create_features", FeatureCreation()),
                ("save_to_csv", SaveToCsv()),
            ]
        )
        __pipeline.fit_transform(__raw_data)
