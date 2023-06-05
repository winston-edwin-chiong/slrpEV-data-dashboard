import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import plotly.io as pio 


def add_training_end_vline(self, start_date, end_date):

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

        # filter df by date and columns
        df = cls.__query_df(df, granularity, quantity, start_date, end_date)

        # get layout 
        plot_layout = cls.plot_layout_key[quantity]

        # get hover data
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
            margin=dict(l=20, r=20, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)
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
class PlotDailySessions:

    # Plot empty figure if no sessions
    @staticmethod
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


    @classmethod
    def plot_daily_time_series(cls, df: pd.DataFrame) -> go.Figure:

        if len(df) == 0:
            return cls.empty_session_figure()

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
    def plot_today_forecast(cls, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        # query today's forecast
        peak = df.loc[df.index == datetime.now().strftime("%Y-%m-%d")]["peak_power_W_predictions"].iloc[0]

        # add horizontal line to figure 
        fig.add_hline(
            y=peak,
            line_dash="dot",
            annotation_text=f"Peak Power Forecast: {round(peak, 1)} W"
        )
        return fig


    @classmethod
    def plot_daily_energy_breakdown(cls, df: pd.DataFrame) -> go.Figure:

        if len(df) == 0:
            return cls.empty_session_figure()

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

    
# Class to plot cumulative energy delivered
class PlotCumulatives:

    @classmethod
    def plot_cumulative(cls, quantity: str, df: pd.DataFrame, start_date: str, end_date: str) -> go.Figure:
        if quantity == "cumulative-energy-delivered":
            # necessary for some reason, even though 'finishChargeTime' is already cast to datetime during cleaning
            df["finishChargeTime"] = pd.to_datetime(df["finishChargeTime"])
            df = df.sort_values(by="finishChargeTime")
            df = cls.__query_date_df(df, start_date, end_date, "finishChargeTime")

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df["finishChargeTime"],
                    # calculate cumulative sum in kWh
                    y=df["cumEnergy_Wh"].cumsum(axis=0) / 1000,
                    fill="tozeroy",
                    mode="lines",
                )
            )

            fig.update_layout(
                title="Cumulative Energy Delivered",
                xaxis_title="Time",
                yaxis_title="Energy Delivered (kWh)",
                margin=dict(l=20, r=20, pad=0),
                title_pad=dict(l=0, r=0, t=0, b=0)
            )

            return fig
        
        elif quantity == "cumulative-num-users":
            # calculate cumulative number of unique users
            df["startChargeTime"] = pd.to_datetime(df["startChargeTime"])
            df = df[['startChargeTime', 'userId']].sort_values(['startChargeTime', 'userId'])
            df["cumulative_users"] = (~df['userId'].duplicated()).cumsum()

            # query df by date
            df = cls.__query_date_df(df, start_date, end_date, "startChargeTime")

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df["startChargeTime"],
                    y=df["cumulative_users"],
                    fill="tozeroy",
                    mode="lines",
                )
            )

            fig.update_layout(
                title="Cumulative Number of Unique Users",
                xaxis_title="Time",
                yaxis_title="Number of Unique Users",
                margin=dict(l=20, r=20, pad=0),
                title_pad=dict(l=0, r=0, t=0, b=0)
            )
            return fig
        
        elif quantity == "cumulative-vehicle-model-energy":
            # group by vehicle model 
            df = df[["vehicle_model", "cumEnergy_Wh"]].groupby("vehicle_model").sum()
            df = df.sort_values("cumEnergy_Wh", ascending=False).head(20)
            df["cumEnergy_kWh"] = round(df["cumEnergy_Wh"] / 1000, 1)

            fig = px.bar(df, x=df.index, y='cumEnergy_kWh')
            fig.update_traces(hovertemplate="Vehicle Model: %{x}<br>Energy Consumed: %{y} kWh<extra></extra>")
            fig.update_layout(
                title="Top 20 Energy Consumption by Vehicle Model",
                xaxis_title="Vehicle Model",
                yaxis_title="Cumulative Energy Consumption (kWh)",
                margin=dict(l=20, r=20, pad=0),
                title_pad=dict(l=0, r=0, t=0, b=0)
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

    @staticmethod
    def default():
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
                        "text": "Hover over a point to <br> to display more information!",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 10
                        },
                    }
                ]
            },
            margin=dict(l=0, r=0, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)  
        )
        return fig


    @classmethod 
    def plot_day_hover_histogram(cls, hoverData, df, quantity):

        # extract day name
        if hoverData["points"][0]["curveNumber"] == 0:
            day_name = hoverData["points"][0]["customdata"][0]

        elif hoverData["points"][0]["curveNumber"] == 1:
            day_name = pd.to_datetime(hoverData["points"][0]["x"]).day_name()

        # get point to hover on (if it exists in dailydemand)              
        point = df.loc[df.index == pd.to_datetime(hoverData["points"][0]["x"]).strftime("%Y-%m-%d")][quantity].iloc[0] if pd.to_datetime(hoverData["points"][0]["x"]) < pd.to_datetime((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")) else None

        # filter df 
        df = df.loc[df["day"] == day_name]

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df[quantity],
                histnorm="percent",
                hovertemplate="<extra></extra>Value: %{x}<br>% Share: %{y}",
                # marker=dict(line=dict(width=0.8, color="black"))
            )
        )
        if point is not None: 
            fig.add_trace(
                go.Scatter(
                    x=[point], 
                    mode="markers",
                    marker_symbol="arrow-up",
                    hovertemplate="Realized: %{x} <extra></extra>"
                )
            )
        fig.update_layout(
            title=f"Dist. On {day_name}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            yaxis_title="Percent Share",
            showlegend=False,
            margin=dict(l=0, r=0, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)
        )          

        return fig 
    

    @classmethod 
    def plot_hour_hover_histogram(cls, hoverData, df, quantity):

        # extract hour name
        hour = int(pd.to_datetime(hoverData["points"][0]["x"]).strftime("%H"))

        # get point to hover on 
        point = hoverData["points"][0]["y"]

        df = df[df.index.hour == hour]

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df[quantity],
                histnorm="percent",
                hovertemplate="<extra></extra>Value: %{x}<br>% Share: %{y}",
                # marker=dict(line=dict(width=0.8, color="black"))
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[point], 
                mode="markers",
                marker_symbol="arrow-up",
                hovertemplate="Realized: %{x} <extra></extra>"
            )
        )
        fig.update_layout(
            title=f"Dist. On Hour {hour}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            yaxis_title="Percent Share",
            showlegend=False,
            margin=dict(l=0, r=0, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)
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
                ],              
            },
            margin=dict(l=0, r=0, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)  
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


# Class to plot choice analytics 
class PlotSchedVsReg:     

    @classmethod
    def plot_sched_vs_reg(cls, df: pd.DataFrame) -> go.Figure():

        df = df[["sch_centsPerHr", "reg_centsPerHr", "choice"]].value_counts().to_frame("counts").reset_index()

        fig = px.scatter(data_frame=df, 
                         y="sch_centsPerHr", 
                         x="reg_centsPerHr", 
                         color="choice", 
                         size="counts", 
                         size_max=100,
                         labels={"choice": "Choice"}
                         )
        fig.update_traces(hovertemplate="Scheduled ¢/Hr: %{x}<br>Regular ¢/Hr: %{y}<br>Count: %{marker.size:,}<br>Choice: %{text}<extra></extra>", text=df['choice'])
        fig.update_layout(
            title=f"Choice On Different Price / Charge Offerings",
            xaxis_title="REGULAR PRICE (cents/hour)",
            yaxis_title="SCHEDULED PRICE (cents/hour)",
            showlegend=True,
            margin=dict(l=15, r=15, pad=0),
            title_pad=dict(l=0, r=0, t=0, b=0)
        ) 
        
        return fig
