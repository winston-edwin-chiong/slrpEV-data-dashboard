from sklearn.pipeline import Pipeline
from datacleaning.pipelineclasses import *


class CleanData:

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

    def __init__(self):
        pass

    @classmethod
    def clean_save_raw_data(cls):
        cls.__pipeline.fit_transform(cls.__raw_data)
