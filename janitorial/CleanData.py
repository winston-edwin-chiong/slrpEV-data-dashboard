import pandas as pd 
from sklearn.pipeline import Pipeline
from janitorial.pipelineclasses import *

class CleanData:

    def __init__(self):
        self.__add_pipeline()
        self.__raw_data = pd.read_csv("data/raw_data.csv")

    def __add_pipeline(self):
        self.__pipeline = Pipeline([
            ("sort_drop_cast", SortDropCast()),
            ("create_helpers", HelperFeatureCreation()),
            ("create_session_TS", CreateSessionTimeSeries()),
            ("create_features", FeatureCreation()),
            ("save_to_csv", SaveToCsv()),
        ])

    def clean_raw_data(self):
        self.cleaned_data = self.__pipeline.fit_transform(self.__raw_data)
        return self.cleaned_data
