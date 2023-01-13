import pandas as pd
import plotly.graph_objects as go
import datetime

def get_last_days_datetime(n=7):
    """
    """
    current_time = pd.to_datetime("today") - datetime.timedelta(days=7)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time 

class LoadDataFrames():

    dataframes = {}

    @classmethod
    def load_csv(cls):
        cls.dataframes["fivemindemand"] = cls.set_index_and_datetime(pd.read_csv("data/fivemindemand.csv"))
        cls.dataframes["hourlydemand"] = cls.set_index_and_datetime(pd.read_csv("data/hourlydemand.csv"))
        cls.dataframes["dailydemand"] = cls.set_index_and_datetime(pd.read_csv("data/dailydemand.csv"))
        cls.dataframes["monthlydemand"] = cls.set_index_and_datetime(pd.read_csv("data/monthlydemand.csv"))
        return cls.dataframes

    @staticmethod
    def set_index_and_datetime(df):
        """
        Function takes in a dataframe with a column "time", and sets this column
        to the index, while converting the time column to datetime-like. 
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df 

class PlotPredictions:

    def __init__(self, figure, granularity, quantity, start_date, end_date):
        self.figure = figure
        self.granularity = granularity
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date

    def add_predictions(self):
        predictions_df = self.set_index_and_datetime(pd.read_csv(f"forecasts/data/{self.quantity}_forecast.csv"))
        predictions_df = self.query_date_df(predictions_df, self.start_date, self.end_date)

        self.figure.add_trace(
            go.Scatter(
                x=predictions_df.index,
                y=predictions_df[f"{self.quantity} forecast"],
                name="Energy Demand Forecast",
                line={"dash":"dash"},
                fill="tozeroy"
            )
        )
        self.figure.update_layout(legend=dict(orientation="h"))
    
    @staticmethod
    def set_index_and_datetime(df):
        """
        Function takes in a dataframe with a column "time", and sets this column
        to the index, while converting the time column to datetime-like. 
        """
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df   

    @staticmethod
    def query_date_df(df, start_date, end_date) -> pd.DataFrame:
        """
        Function querys a dataframe based on a specified start date and end date. If any argument is None, 
        function will ignore those bounds Assumes dataframe has a datetime-like index. Start and end dates are 
        also assumed to be in the form 'yyyy-mm-dd'.
        ~~~
        Parameters:
        df : Dataframe to be queried.
        start_date : Inclusive start date in 'yyyy-mm-dd' format.
        end_date : Inclusive end date in 'yyyy-mm-dd' format.
        """
        if start_date == None and end_date == None:
            return df
        elif start_date != None and end_date == None:
            return df.loc[(df.index >= start_date)]
        elif start_date == None and end_date != None:
            return df.loc[(df.index <= end_date)]
        else:
            return df.loc[(df.index >= start_date) & (df.index <= end_date)]

    def add_training_end_vline(figure, start_date, end_date):
        """
        """
        training_end = "2022-08-15"
        
        plotly_friendly_date = datetime.datetime.strptime(training_end, "%Y-%m-%d").timestamp() * 1000 # this is a known bug

        if start_date == None and end_date == None: 
            figure.add_vline(x=plotly_friendly_date, line_color = "green", line_dash="dash", annotation_text="End of Training Data")
        elif start_date != None and end_date == None and start_date <= training_end:
            figure.add_vline(x=plotly_friendly_date, line_color = "green", line_dash="dash", annotation_text="End of Training Data")
        elif start_date == None and end_date != None and training_end <= end_date:
            figure.add_vline(x=plotly_friendly_date, line_color = "green", line_dash="dash", annotation_text="End of Training Data")
        elif start_date != None and end_date != None and start_date <= training_end <= end_date:
            figure.add_vline(x=plotly_friendly_date, line_color = "green", line_dash="dash", annotation_text="End of Training Data")

class PlotDataFrame():
    
    def __init__(self, df, granularity, quantity, start_date, end_date):
        self.df = df
        self.granularity = granularity
        self.granularity_key = {
            'fivemindemand': {
                "other_cols" : ["day"]
            },
            'hourlydemand' : {
                "other_cols" : ["day"]
            },
            'dailydemand': {
                "other_cols" : ["day"]
            },
            'monthlydemand': {
                "other_cols" : ["month"]
            }
        }
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.plot_key = {
            "energy_demand_kWh": {
                "column_name":"energy_demand_kWh",
                "units_measurement":"(kWh)",
                "cleaned_quantity": "Energy Demand"
            },
            "avg_power_demand_W": {
                "column_name":"avg_power_demand_W",
                "units_measurement":"(W)",
                "cleaned_quantity": "Average Power Demand"
            },
            "peak_power_W": {
                "column_name":"peak_power_W",
                "units_measurement":"(W)",
                "cleaned_quantity": "Peak Power Demand"
            },
        } 
    
    def plot(self):
        self.__prepare()
        return self.__plot_time_series()

    def __prepare(self):
        other_cols = self.granularity_key.get(self.granularity).get("other_cols")
        self.df = self.df[[self.quantity] + other_cols]
        self.df = self.query_date_df(self.df, self.start_date, self.end_date)
        return self.df

    @staticmethod
    def query_date_df(df, start_date, end_date) -> pd.DataFrame:
        """
        Function querys a dataframe based on a specified start date and end date. If any argument is None, 
        function will ignore those bounds Assumes dataframe has a datetime-like index. Start and end dates are 
        also assumed to be in the form 'yyyy-mm-dd'.
        ~~~
        Parameters:
        df : Dataframe to be queried.
        start_date : Inclusive start date in 'yyyy-mm-dd' format.
        end_date : Inclusive end date in 'yyyy-mm-dd' format.
        """
        if start_date == None and end_date == None:
            return df
        elif start_date != None and end_date == None:
            return df.loc[(df.index >= start_date)]
        elif start_date == None and end_date != None:
            return df.loc[(df.index <= end_date)]
        else:
            return df.loc[(df.index >= start_date) & (df.index <= end_date)]

    def __plot_time_series(self):

        plot_layout = self.plot_key[self.quantity]
        other_layout = self.granularity_key[self.granularity]

        self.fig = go.Figure()

        self.fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df[plot_layout["column_name"]],
                name=plot_layout["cleaned_quantity"] + " " + plot_layout["units_measurement"],
                hovertext=self.df[other_layout.get('other_cols')[0]],
                fill="tozeroy",
            )
    )
        self.fig.update_layout(
            title=plot_layout["cleaned_quantity"] + " " + plot_layout["cleaned_quantity"],
            xaxis_title="Time",
            yaxis_title=plot_layout["cleaned_quantity"] + " " + plot_layout["units_measurement"],
            template="plotly",
        )

        return self.fig 