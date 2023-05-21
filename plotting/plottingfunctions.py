import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta


# Plot empty figure if no sessions
def empty_session_figure() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        {
            "xaxis": {
                "visible": False,
                "rangeslider": {
                    "visible": False
                }
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": "No sessions today!<br>Check back soon :)",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    )
    return fig


def add_training_end_vline(self, start_date, end_date):
    """
    """
    training_end = "2022-08-15"

    plotly_friendly_date = datetime.strptime(training_end,
                                             "%Y-%m-%d").timestamp() * 1000  # this is a known bug

    if start_date is None and end_date is None:
        self.add_vline(x=plotly_friendly_date, line_color="green", line_dash="dash",
                       annotation_text="End of Training Data")
    elif start_date is not None and end_date is None and start_date <= training_end:
        self.add_vline(x=plotly_friendly_date, line_color="green", line_dash="dash",
                       annotation_text="End of Training Data")
    elif start_date is None and end_date is not None and training_end <= end_date:
        self.add_vline(x=plotly_friendly_date, line_color="green", line_dash="dash",
                       annotation_text="End of Training Data")
    elif start_date is not None and end_date is not None and start_date <= training_end <= end_date:
        self.add_vline(x=plotly_friendly_date, line_color="green", line_dash="dash",
                       annotation_text="End of Training Data")


# Class to plot main time series
class PlotMainTimeSeries:
    other_columns = {
        'fivemindemand': {
            "hoverdata": ["day"]
        },
        'hourlydemand': {
            "hoverdata": ["day"]
        },
        'dailydemand': {
            "hoverdata": ["day"]
        },
        'monthlydemand': {
            "hoverdata": ["month"]
        }
    }
    plot_layout_key = {
        "energy_demand_kWh": {
            "column_name": "energy_demand_kWh",
            "units_measurement": "(kWh)",
            "cleaned_quantity": "Energy Demand"
        },
        "avg_power_demand_W": {
            "column_name": "avg_power_demand_W",
            "units_measurement": "(W)",
            "cleaned_quantity": "Average Power Demand"
        },
        "peak_power_W": {
            "column_name": "peak_power_W",
            "units_measurement": "(W)",
            "cleaned_quantity": "Peak Power Demand"
        },
    }
    hover_template_key = {
        "fivemindemand": "<extra></extra>" + "%{customdata[0]}, %{x|%b %d, %Y, %H:%M}" + "<br>%{y} %{customdata[1]}",
        "hourlydemand": "<extra></extra>" + "%{customdata[0]}, %{x|%b %d, %Y, %H:%M}" + "<br>%{y} %{customdata[1]}",
        "dailydemand": "<extra></extra>" + "%{customdata[0]}, %{x|%b %d, %Y}" + "<br>%{y} %{customdata[1]}",
        "monthlydemand": "<extra></extra>" + "%{customdata[0]} %{x|%Y}" + "<br>%{y} %{customdata[1]}",
    }

    @classmethod
    def plot_main_time_series(cls, df: pd.DataFrame, granularity: str, quantity: str, start_date: str, end_date: str) -> go.Figure:

        # prepare df for plotting
        df = cls.__query_df(df, granularity, quantity, start_date, end_date)

        plot_layout = cls.plot_layout_key[quantity]

        hover_column = cls.other_columns[granularity].get("hoverdata")
        hoverdata = df[hover_column]
        hoverdata["units"] = plot_layout["units_measurement"]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[plot_layout["column_name"]],
                name=plot_layout["cleaned_quantity"] +
                " " + plot_layout["units_measurement"],
                customdata=hoverdata,
                hovertemplate=cls.hover_template_key[granularity],
                fill="tozeroy",
            )
        )
        fig.update_layout(
            title=plot_layout["cleaned_quantity"],
            xaxis_title="Time",
            yaxis_title=plot_layout["cleaned_quantity"] +
            " " + plot_layout["units_measurement"],
            template="plotly",
        )

        return fig


    @classmethod
    def __query_df(cls, df: pd.DataFrame, granularity: str, quantity: str, start_date: str, end_date: str) -> pd.DataFrame:
        # get relevant columns
        hoverdata = cls.other_columns.get(granularity).get("hoverdata")
        df = df[[quantity] + hoverdata]
        # query df by date
        df = cls.__query_date_df(df, start_date, end_date)
        return df


    @staticmethod
    def __query_date_df(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
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
        if start_date is None and end_date is None:
            return df
        elif start_date is not None and end_date is None:
            return df.loc[(df.index >= start_date)]
        elif start_date is None and end_date is not None:
            return df.loc[(df.index <= end_date)]
        else:
            return df.loc[(df.index >= start_date) & (df.index <= end_date)]


# Class to plot daily session time series
class PlotDailySessionTimeSeries:

    def plot_daily_time_series(df: pd.DataFrame) -> go.Figure:

        if len(df) == 0:
            return empty_session_figure()

        fig = go.Figure()

        for dcosId in df["dcosId"].unique():
            fig.add_trace(
                go.Bar(
                    x=df[df["dcosId"] == dcosId]["Time"],
                    y=df[df["dcosId"] == dcosId]["Power (W)"],
                    customdata=df[df["dcosId"] == dcosId][[
                        "vehicle_model", "choice", "userId"]],
                    name="User ID: " + df[df["dcosId"]
                                          == dcosId]["userId"].iloc[0],
                    offsetgroup=1,
                    hovertemplate="<br>Date: %{x}" +
                    "<br>Power: %{y} Watts" +
                    "<br>Vehicle Model: %{customdata[0]}" +
                    "<br>Choice: %{customdata[1]}",
                    hoverlabel={"font":{"size":10}},
                )
            )
        fig.update_layout(
            {
                "title": "Today's Sessions",
                "xaxis_title": "Time",
                "yaxis_title": "Power (W)",
                "barmode": "stack",
                "showlegend": True,
                "xaxis_range": [datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")],
            }
        )
        return fig
    

    @classmethod
    def plot_yesterday(cls, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        # query dataframe
        start_date = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")
        end_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        df = cls.__query_date_df(df, start_date, end_date)
        df.index = df.index + pd.Timedelta('1 day')

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["avg_power_demand_W"],
                mode='lines',
                hoverinfo='skip',
                line_color='rgba(0, 0, 0, 0.35)',
                name = "Yesterday's Load Curve"
            )
        )

        return fig 


    @classmethod
    def plot_daily_peak_forecast(cls, fig: go.Figure, peak: float) -> go.Figure:
        return 
        

    @staticmethod
    def __query_date_df(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Function querys a dataframe based on a specified start date and end date. If any argument is None, 
        function will ignore those bounds. Start and end dates are also assumed to be in the form 'yyyy-mm-dd'.
        ~~~
        Parameters:
        df : Dataframe to be queried.
        start_date : Inclusive start date in 'yyyy-mm-dd' format.
        end_date : Inclusive end date in 'yyyy-mm-dd' format.  
        """

        if start_date is None and end_date is None:
            return df
        elif start_date is not None and end_date is None:
            return df.loc[(df.index >= start_date)]
        elif start_date is None and end_date is not None:
            return df.loc[(df.index <= end_date)]
        else:
            return df.loc[(df.index >= start_date) & (df.index <= end_date)]


# Class to plot vehicle donut chart
class PlotDailySessionEnergyBreakdown:

    def plot_daily_energy_breakdown(df: pd.DataFrame) -> go.Figure:

        if len(df) == 0:
            return empty_session_figure()

        df = df[["dcosId", "cumEnergy_Wh", "vehicle_model"]
                ].groupby("dcosId").first().copy()

        fig = go.Figure(data=[go.Pie(
            labels=df["vehicle_model"],
            values=df["cumEnergy_Wh"]/1000,
            hole=0.6,
            hovertemplate="<extra></extra>" +
            "Vehicle Model: %{label}" +
            "<br>Energy Consumed Today: %{value} kWh")
        ]
        )

        fig.update_layout(
            title_text=f'Total Energy Delivered Today: {df["cumEnergy_Wh"].sum(axis=0) / 1000} kWh',
        )
        return fig

    
# Class to plot cumulative energy delivered
class PlotCumulativeEnergyDelivered:

    @classmethod
    def plot_cumulative_energy_delivered(cls, df: pd.DataFrame, start_date: str, end_date: str) -> go.Figure:

        # necessary for some reason, even though 'finishChargeTime' is already cast to datetime during cleaning
        df["finishChargeTime"] = pd.to_datetime(df["finishChargeTime"])
        df = df.sort_values(by="finishChargeTime")
        # df["cum_sum_kWh"] = df["cumEnergy_Wh"].cumsum(axis=0) / 1000
        df = cls.__query_date_df(df, start_date, end_date, "finishChargeTime")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["finishChargeTime"],
                # calculate cumulative sum in kWh
                y=df["cumEnergy_Wh"].cumsum(axis=0) / 1000,
                fill="tozeroy",
                mode="lines"
            )
        )

        fig.update_layout(
            title="Cumulative Energy Delivered",
            xaxis_title="Time",
            yaxis_title="Energy Delivered (kWh)",
            # yaxis = dict(range=[df["cum_sum_kWh"].min(), df["cum_sum_kWh"].max()]),
        )

        return fig

    @staticmethod
    def __query_date_df(df: pd.DataFrame, start_date: str, end_date: str, col:str) -> pd.DataFrame:
        """
        Function querys a dataframe based on a specified start date and end date. If any argument is None, 
        function will ignore those bounds. Start and end dates are also assumed to be in the form 'yyyy-mm-dd'.
        ~~~
        Parameters:
        df : Dataframe to be queried.
        start_date : Inclusive start date in 'yyyy-mm-dd' format.
        end_date : Inclusive end date in 'yyyy-mm-dd' format.
        col : Column to query date on.  
        """

        if start_date is None and end_date is None:
            return df
        elif start_date is not None and end_date is None:
            return df.loc[(df[col] >= start_date)]
        elif start_date is None and end_date is not None:
            return df.loc[(df[col] <= end_date)]
        else:
            return df.loc[(df[col] >= start_date) & (df[col] <= end_date)]


# Class to hover histograms
class PlotHoverHistogram:
    cleaned_column_names = {
        "energy_demand_kWh": {
            "col_name": "Energy Demand (kWh)"
        },
        "avg_power_demand_W": {
            "col_name": "Avg. Power Demand (W)"
        },
        "peak_power_W": {
            "col_name": "Peak Power (W)"
        },
    }

    @classmethod 
    def plot_day_hover_histogram(cls, data, quantity, day):
        data = data.loc[data["day"] == day]

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(x=data[quantity])
        )
        fig.update_layout(
            title=f"Distribution on {day}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            yaxis_title="Count",
        )          

        return fig 
    

    @classmethod 
    def plot_hour_hover_histogram(cls, data, quantity, hour):
        data = data[data.index.hour == hour]

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(x=data[quantity])
        )
        fig.update_layout(
            title=f"Distribution at Hour {hour}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            yaxis_title="Count",
        )         

        return fig 
    

    @staticmethod
    def empty_histogram_figure() -> go.Figure:
        '''
        Some granularities don't have day / hour distributions. 
        '''
        fig = go.Figure()
        fig.update_layout(
            {
                "xaxis": {
                    "visible": False,
                    "rangeslider": {
                        "visible": False
                    }
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No distribution<br>available!",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 15
                        }
                    }
                ]
            }
        )
        return fig


# Class to update user hover data
class GetUserHoverData:

    @classmethod
    def get_user_hover_data(cls, df: pd.DataFrame, userId: int) -> tuple:

        subset = df[df["userId"] == userId].copy()

        num_sessions = len(subset)
        average_duration = round(subset["trueDurationHrs"].mean(), 2)
         
        subset["connectTime"] = pd.to_datetime(subset["connectTime"])
        freq_connect_time = subset["connectTime"].dt.hour.apply(cls.__get_connect).value_counts().index[0]

        total_nrg_consumed = subset["cumEnergy_Wh"].sum() / 1000

        return num_sessions, average_duration, freq_connect_time, total_nrg_consumed
        
    def __get_connect(hour: int) -> str:
        if 6 <= hour <= 10:
            return "Morning! 🐦"  
        elif 10 < hour <= 16:
            return "Afternoon! ☀️"
        elif 16 < hour <= 22:
            return "Evening! 🌙"
        else:
            return "Really late at night! 🦉" 


# Class to plot forecasts 
class PlotForecasts:

    plot_layout_key = {
        "energy_demand_kWh": {
            "units_measurement": "(kWh)",
            "cleaned_quantity": "Energy Demand"
        },
        "avg_power_demand_W": {
            "units_measurement": "(W)",
            "cleaned_quantity": "Average Power Demand"
        },
        "peak_power_W": {
            "units_measurement": "(W)",
            "cleaned_quantity": "Peak Power Demand"
        },
    }


    @classmethod
    def plot_forecasts(cls, fig: go.Figure, forecasts: pd.DataFrame, quantity: str, granularity: str) -> go.Figure:

        if len(forecasts) == 0:
            return fig 

        plot_layout = cls.plot_layout_key[quantity]

        fig.add_trace(
            go.Scatter(
                x=forecasts.index,
                y=forecasts[quantity+"_predictions"],
                customdata=np.vstack(np.repeat([plot_layout["units_measurement"]], len(forecasts))),
                name=f"{plot_layout['cleaned_quantity']} Forecasts", 
                hovertemplate="<extra></extra>" +
                    "%{x}" +
                    "<br><i>%{y} %{customdata[0]}</i>",
                fill="tozeroy",
            )
        )
        return fig        
