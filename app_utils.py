import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


def empty_session_figure():
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


def get_last_days_datetime(n=7):
    """
    """
    current_time = pd.to_datetime("today") - timedelta(days=n)
    current_time = current_time.strftime("%m/%d/%Y")
    return current_time


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
            "other_cols": ["day"]
        },
        'hourlydemand': {
            "other_cols": ["day"]
        },
        'dailydemand': {
            "other_cols": ["day"]
        },
        'monthlydemand': {
            "other_cols": ["month"]
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

    @classmethod
    def plot_main_time_series(cls, df, granularity, quantity, start_date, end_date) -> go.Figure:

        # prepare df for plotting
        df = cls.__query_df(df, granularity, quantity, start_date, end_date)

        plot_layout = cls.plot_layout_key[quantity]
        hover_column = cls.other_columns[granularity].get("other_cols")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[plot_layout["column_name"]],
                name=plot_layout["cleaned_quantity"] +
                " " + plot_layout["units_measurement"],
                hovertext=df[hover_column].stack(),
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
    def __query_df(cls, df, granularity, quantity, start_date, end_date) -> pd.DataFrame:
        # get relevant columns
        other_cols = cls.other_columns.get(granularity).get("other_cols")
        df = df[[quantity] + other_cols]
        # query df by date
        df = cls.__query_date_df(df, start_date, end_date)
        return df

    @staticmethod
    def __query_date_df(df, start_date, end_date) -> pd.DataFrame:
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

    def plot_daily_time_series(df) -> go.Figure:

        if len(df) == 0:
            return empty_session_figure()

        fig = go.Figure()

        for dcosId in df["dcosId"].unique():
            fig.add_trace(
                go.Bar(
                    x=df[df["dcosId"] == dcosId]["Time"],
                    y=df[df["dcosId"] == dcosId]["Power (W)"],
                    hovertext=df[df["dcosId"] == dcosId]["vehicle_model"],
                    name="User ID: " + df[df["dcosId"]
                                          == dcosId]["userId"].iloc[0]
                )
            )
        fig.update_layout(
            {
                "xaxis_range": [datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")],
            }
        )
        return fig


# Class to plot vehicle donut chart
class PlotDailySessionEnergyBreakdown:

    def plot_daily_energy_breakdown(df) -> go.Figure:

        if len(df) == 0:
            return empty_session_figure()

        df = df[["dcosId", "cumEnergy_Wh", "vehicle_model"]
                ].groupby("dcosId").first().copy()
        df["percentage_energy"] = df["cumEnergy_Wh"] / \
            df["cumEnergy_Wh"].sum(axis=0)

        fig = go.Figure(data=[go.Pie(labels=df["vehicle_model"],
                        values=df["percentage_energy"], hole=0.6)])

        fig.update_layout(
            title_text=f'Total Energy Delivered Today: {df["cumEnergy_Wh"].sum(axis=0)} kWh',
        )
        return fig
