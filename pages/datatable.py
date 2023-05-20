import dash
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime 
from dash import html, dcc, dash_table, Input, Output, State
import dash_daq as daq
import redis
import pickle
import dash_ag_grid as dag

dash.register_page(__name__, path="/data")

redis_client = redis.Redis(host='localhost', port=6360)

# load data
df = pickle.loads(redis_client.get("raw_data"))
# drop helper columns 
df = df.drop(
        columns=[
            "finishChargeTime",
            "trueDurationHrs",
            "true_peakPower_W",
            "Overstay",
            "Overstay_h"
        ]
    )

grid = dag.AgGrid(
    id="raw-data-grid",
    columnDefs=[{"field": i} for i in df.columns],
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth":125},
    columnSize="sizeToFit",
    rowModelType="infinite",
    dashGridOptions={
        # The number of rows rendered outside the viewable area the grid renders.
        "rowBuffer": 0,
        # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
        "maxBlocksInCache": 1,
        "rowSelection": "multiple",
        "pagination": True
    },
    style={"margin":5}
)

layout = \
        html.Div([
            html.Button("Reset Columns", id="reset-btn"),
            html.Div([
                dcc.Checklist(
                    id='column-checklist',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    value=[option["value"] for option in [{'label': col, 'value': col} for col in df.columns]],
                    labelStyle={'display': 'block'}
                )
            ], style={'height': '300px', 'width': '250px', 'overflow': 'auto'}),
            grid, 
        ])


operators = {
    "greaterThanOrEqual": "ge",
    "lessThanOrEqual": "le",
    "lessThan": "lt",
    "greaterThan": "gt",
    "notEqual": "ne",
    "equals": "eq",
}

# Don't touch this
def filterDf(df, data, col):
    if data["filterType"] == "date":
        crit1 = data["dateFrom"]
        crit1 = pd.Series(crit1).astype(df[col].dtype)[0]
        if "dateTo" in data:
            crit2 = data["dateTo"]
            crit2 = pd.Series(crit2).astype(df[col].dtype)[0]
    else:
        crit1 = data["filter"]
        crit1 = pd.Series(crit1).astype(df[col].dtype)[0]
        if "filterTo" in data:
            crit2 = data["filterTo"]
            crit2 = pd.Series(crit2).astype(df[col].dtype)[0]
    if data["type"] == "contains":
        df = df.loc[df[col].str.contains(crit1)]
    elif data["type"] == "notContains":
        df = df.loc[~df[col].str.contains(crit1)]
    elif data["type"] == "startsWith":
        df = df.loc[df[col].str.startswith(crit1)]
    elif data["type"] == "notStartsWith":
        df = df.loc[~df[col].str.startswith(crit1)]
    elif data["type"] == "endsWith":
        df = df.loc[df[col].str.endswith(crit1)]
    elif data["type"] == "notEndsWith":
        df = df.loc[~df[col].str.endswith(crit1)]
    elif data["type"] == "inRange":
        if data["filterType"] == "date":
            df = df.loc[df[col].astype("datetime64[ns]").between_time(crit1, crit2)]
        else:
            df = df.loc[df[col].between(crit1, crit2)]
    elif data["type"] == "blank":
        df = df.loc[df[col].isnull()]
    elif data["type"] == "notBlank":
        df = df.loc[~df[col].isnull()]
    else:
        df = df.loc[getattr(df[col], operators[data["type"]])(crit1)]
    return df


@dash.callback(
    Output("raw-data-grid", "getRowsResponse"),
    Input("raw-data-grid", "getRowsRequest"),
)
def infinite_scroll(request):
    dff = df.copy()
    if request is None:
        return dash.no_update
    else:
        if request["filterModel"]:
            fils = request["filterModel"]
            for k in fils:
                try:
                    if "operator" in fils[k]:
                        if fils[k]["operator"] == "AND":
                            dff = filterDf(dff, fils[k]["condition1"], k)
                            dff = filterDf(dff, fils[k]["condition2"], k)
                        else:
                            dff1 = filterDf(dff, fils[k]["condition1"], k)
                            dff2 = filterDf(dff, fils[k]["condition2"], k)
                            dff = pd.concat([dff1, dff2])
                    else:
                        dff = filterDf(dff, fils[k], k)
                except:
                    pass
            dff = dff

        if request["sortModel"]:
            sorting = []
            asc = []
            for sort in request["sortModel"]:
                sorting.append(sort["colId"])
                if sort["sort"] == "asc":
                    asc.append(True)
                else:
                    asc.append(False)
            dff = dff.sort_values(by=sorting, ascending=asc)

        lines = len(dff.index)
        if lines == 0:
            lines = 1
    partial = dff.iloc[request["startRow"] : request["endRow"]]
    return {"rowData": partial.to_dict("records"), "rowCount": len(dff.index)}

@dash.callback(
    Output('raw-data-grid', 'columnDefs'),
    Input('column-checklist', 'value')
)
def update_columns(selected_columns):
    return [{"field": i} for i in selected_columns]


@dash.callback(
    Output("column-checklist", "value"),
    Input("reset-btn", "n_clicks"),
    State("column-checklist", 'options'),
    prevent_inital_call=True
)
def reset_columns(n, checklist_options):
    return [option["value"] for option in checklist_options]
