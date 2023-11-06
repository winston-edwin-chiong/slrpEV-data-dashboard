import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pytz
from datetime import datetime, timedelta
from dash_bootstrap_templates import template_from_url


def add_training_end_vline(self, start_date, end_date):
    """
    Plots a vertical line.
    """

    training_end = "2022-08-15"

    plotly_friendly_date = datetime.strptime(training_end, "%Y-%m-%d").timestamp() * 1000  # this is a known bug

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
    def plot_main_time_series(cls, df: pd.DataFrame, granularity: str, quantity: str, start_date: str, end_date: str, theme=None) -> go.Figure:

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
            margin=dict(pad=10),
            template=template_from_url(theme)        
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

        if start_date is None and end_date is None:
            return df
        elif start_date is not None and end_date is None:
            return df.loc[(df.index >= start_date)]
        elif start_date is None and end_date is not None:
            return df.loc[(df.index <= end_date)]
        else:
            return df.loc[(df.index >= start_date) & (df.index <= end_date)]


# Class to plot daily session time series
class PlotDaily:

    # Plot empty figure if no sessions
    @staticmethod
    def empty_session_figure(theme=None) -> go.Figure:
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
            },
            template=template_from_url(theme)        
        )
        return fig
    

    @classmethod
    def plot_daily_time_series(cls, df: pd.DataFrame, yesterday: bool, fivemindemand: pd.DataFrame, daily_forecasts: pd.DataFrame, forecast: bool, theme=None) -> go.Figure:
        if len(df) == 0:
            return cls.empty_session_figure(theme)
        
        fig = go.Figure()

        for i, dcosId in enumerate(df["dcosId"].unique()):
            fig.add_trace(
                go.Bar(
                    x=df[df["dcosId"] == dcosId]["Time"],
                    y=df[df["dcosId"] == dcosId]["Power (W)"],
                    customdata=df[df["dcosId"] == dcosId][["vehicle_model", "choice", "userId"]],
                    name=f"User #{i+1}", # scrub userId for now
                    # name="User ID: " + str(df[df["dcosId"] == dcosId]["userId"].iloc[0]),
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
                    "xaxis_range": [datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d"), (datetime.now(pytz.timezone('US/Pacific')) + timedelta(days=1)).strftime("%Y-%m-%d")],
                    "xaxis_autorange": True
                },
                template=template_from_url(theme)        
            )

        if yesterday:
            fig = cls.plot_yesterday(fig, fivemindemand)
    
        if forecast:
            fig = cls.plot_today_forecast(fig, daily_forecasts)

        return fig


    @classmethod
    def plot_daily_energy_breakdown(cls, df: pd.DataFrame, theme=None) -> go.Figure:
            if len(df) == 0:
                return cls.empty_session_figure(theme)

            df = df[["dcosId", "cumEnergy_Wh", "vehicle_model"]].groupby("dcosId").first().copy()

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
                template=template_from_url(theme)        
            )
            return fig


    @classmethod
    def plot_yesterday(cls, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        # query dataframe
        start_date = datetime.strftime(datetime.now(pytz.timezone('US/Pacific')) - timedelta(1), "%Y-%m-%d")
        end_date = datetime.strftime(datetime.now(pytz.timezone('US/Pacific')), "%Y-%m-%d")
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
        if not df.loc[df.index == datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d")].empty:
            peak = df.loc[df.index == datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d")]["peak_power_W_predictions"].iloc[0]

            # add horizontal line to figure 
            fig.add_hline(
                y=peak,
                line_dash="dot",
                annotation_text=f"Peak Power Forecast: {round(peak, 1)} W"
            )
        return fig


    @staticmethod
    def __query_date_df(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:

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
    def plot_cumulative_energy_delivered(cls, df: pd.DataFrame, start_date: str, end_date: str, theme=None) -> go.Figure:
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
            margin=dict(pad=10),
            template=template_from_url(theme)        
        )

        return fig     


    @classmethod
    def plot_cumulative_num_users(cls, df: pd.DataFrame, start_date: str, end_date: str, theme=None) -> go.Figure:
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
            margin=dict(pad=10),
            template=template_from_url(theme)        
        )
        return fig


    @classmethod
    def plot_cumulative_vehicle_model_energy(cls, df: pd.DataFrame, start_date: str, end_date: str, theme=None) -> go.Figure:
        # group by vehicle model 
        df = df[["vehicle_model", "cumEnergy_Wh"]].groupby("vehicle_model").sum()
        df = df.sort_values("cumEnergy_Wh", ascending=False).head(20)
        df["cumEnergy_kWh"] = round(df["cumEnergy_Wh"] / 1000, 1)

        fig = px.bar(df, x=df.index, y='cumEnergy_kWh', template=template_from_url(theme))
        fig.update_traces(hovertemplate="Vehicle Model: %{x}<br>Energy Consumed: %{y} kWh<extra></extra>")
        fig.update_layout(
            title="Top 20 Vehicle Models by Energy Consumption",
            xaxis_title="Vehicle Model",
            yaxis_title="Cumulative Energy Consumption (kWh)",
            margin=dict(pad=10),
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
            "col_name": "Energy Demand<br>(kWh)"
        },
        "avg_power_demand_W": {
            "col_name": "Avg. Power Demand<br>(W)"
        },
        "peak_power_W": {
            "col_name": "Peak Power<br>(W)"
        },
    }

    @staticmethod
    def default(theme=None):
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
            margin=dict(pad=3),
            template=template_from_url(theme)        
        )
        return fig


    @classmethod 
    def plot_day_hover_histogram(cls, hoverData, df, quantity, granularity, theme=None):

        # non-prediction curve
        if hoverData["points"][0]["curveNumber"] == 0:
            day_name = hoverData["points"][0]["customdata"][0]
            # get point to hover on (if it exists in dailydemand)    
            point = df.loc[df.index == pd.to_datetime(hoverData["points"][0]["x"]).strftime("%Y-%m-%d")][quantity].iloc[0] \
                if pd.to_datetime(hoverData["points"][0]["x"]) < pd.to_datetime((datetime.now(pytz.timezone('US/Pacific')) + timedelta(days=1)).strftime("%Y-%m-%d")) \
                else None

        # prediction curve
        elif hoverData["points"][0]["curveNumber"] == 1:
            day_name = pd.to_datetime(hoverData["points"][0]["x"]).day_name()

            if granularity == "dailydemand":
                point = hoverData["points"][0]["y"]

            elif granularity == "hourlydemand":
                point = None


        # filter df 
        df = df.loc[df["day"] == day_name]

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df[quantity],
                histnorm="percent",
                hovertemplate="<extra></extra>Value: %{x}<br>% Share: %{y}",
            )
        )
        if point is not None: 
            fig.add_trace(
                go.Scatter(
                    x=[point], 
                    mode="markers",
                    marker_symbol="arrow-up",
                    hovertemplate=("Realized: " if hoverData["points"][0]["curveNumber"] == 0 else "Predicted: ") + "%{x} <extra></extra>"
                )
            )
        fig.update_layout(
            title=f"Dist. On {day_name}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            xaxis_title_font=dict(size=12),
            yaxis_title="Percent Share",
            showlegend=False,
            margin=dict(pad=0),
            template=template_from_url(theme)        
        )          

        return fig 
    

    @classmethod 
    def plot_hour_hover_histogram(cls, hoverData, df, quantity, theme=None):

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
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[point], 
                mode="markers",
                marker_symbol="arrow-up",
                hovertemplate=("Realized: " if hoverData["points"][0]["curveNumber"] == 0 else "Predicted: ") + "%{x} <extra></extra>"
            )
        )
        fig.update_layout(
            title=f"Dist. On Hour {hour}",
            xaxis_title=cls.cleaned_column_names[quantity]["col_name"],
            xaxis_title_font=dict(size=12),
            yaxis_title="Percent Share",
            showlegend=False,
            margin=dict(pad=0),
            template=template_from_url(theme)        
        )         

        return fig 
    

    @staticmethod
    def empty_histogram_figure(theme=None) -> go.Figure:
        '''
        Some granularities don't have day / hour distributions. 
        This functions returns an empty histogram stating there is no distribution available. 
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
                            "size": 10
                        }
                    }
                ],              
            },
            margin=dict(pad=3),
            template=template_from_url(theme)        
        )
        return fig


# Class to update user hover data
class GetUserHoverData:

    @classmethod
    def get_user_hover_data(cls, df: pd.DataFrame, userId: int) -> tuple:
        """
        Returns `num_sessions`, `average_duration`, `freq_connect_time`, `total_nrg_consumed`, `pref_charging_choice`, `pref_charging_choice_percent`.
        """

        subset = df[df["userId"] == userId].copy()

        num_sessions = subset.shape[0]
        average_duration = round(subset["trueDurationHrs"].mean(), 2)
         
        subset["connectTime"] = pd.to_datetime(subset["connectTime"])
        freq_connect_time = subset["connectTime"].dt.hour.apply(cls.__get_connect).value_counts().index[0]

        total_nrg_consumed = subset["cumEnergy_Wh"].sum() / 1000

        pref_charging_choice = subset["choice"].mode()[0]
        pref_charging_choice_percent = subset[subset["choice"] == pref_charging_choice].shape[0] / subset.shape[0]

        return num_sessions, average_duration, freq_connect_time, total_nrg_consumed, pref_charging_choice, pref_charging_choice_percent
        
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
    def plot_sched_vs_reg(cls, df: pd.DataFrame, theme=None) -> go.Figure():

        df = df[["sch_centsPerHr", "reg_centsPerHr", "choice"]].value_counts().to_frame("counts").reset_index()

        fig = px.scatter(data_frame=df, 
                         y="sch_centsPerHr", 
                         x="reg_centsPerHr", 
                         color="choice", 
                         size="counts", 
                         size_max=100,
                         custom_data=["choice"],
                         template=template_from_url(theme)  
                         )
        fig.update_traces(hovertemplate="Scheduled ¢/Hr: %{x}<br>Regular ¢/Hr: %{y}<br>Count: %{marker.size:,}<br>Choice: %{customdata}<extra></extra>")
        fig.update_layout(
            title="Choice On Different Price & Charge Offerings",
            xaxis_title="REGULAR PRICE (cents/hour)",
            yaxis_title="SCHEDULED PRICE (cents/hour)",
            showlegend=True,
        ) 
        return fig


# Class to plot chargers 

class PlotChargers:

    @classmethod
    def plot_charger_usage_bar_chart(cls, df: pd.DataFrame, theme=None) -> go.Figure():

        fig = go.Figure(
            data=[
                go.Bar(name='Cumulative', x=df["stationId"], y=df["cumEnergy_Wh"]/1000, yaxis='y', offsetgroup=1, hovertemplate="Station %{x}<br>Energy Delivered: %{y} kWh"),
                go.Bar(name='Today', x=df["stationId"], y=df["todayEnergy_Wh"]/1000, yaxis='y2', offsetgroup=2, hovertemplate="Station %{x}<br>Energy Delivered: %{y} kWh")
            ],
            layout={
                'yaxis': {'title': 'Cumulative Energy Delivered (kWh)'},
                'yaxis2': {'title': 'Energy Delivered Today (kWh)', 'overlaying': 'y', 'side': 'right'}
            },
        )

        fig.update_layout(
            barmode='group',
            title=f"Cumulative & Today's Energy Delivered by Charger",
            xaxis_title="Station ID",
            margin=dict(pad=0),
            legend={"x":1.05, "y":1}, 
            template=template_from_url(theme),
            hovermode="x" 
            )
        
        return fig 