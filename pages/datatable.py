import dash
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag
from dash import html, dcc, Input, Output, State, ctx
from dash_bootstrap_templates import ThemeChangerAIO
from db.utils import db

dash.register_page(__name__, path="/data")

r = db.get_redis_connection()

# load data
df = db.get_df(r, "raw_data")

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

# reverse data (most recent first)
df = df[::-1]

grid = dag.AgGrid(
    id="raw-data-grid",
    columnDefs=[{"field": i} for i in df.columns],
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 125},
    columnSize="sizeToFit",
    rowModelType="infinite",
    rowData = df.to_dict("records"),
    dashGridOptions={
        "rowBuffer": 0,
        "maxBlocksInCache": 1,
        "rowSelection": "multiple",
        "pagination": True,
        "paginationAutoPageSize": True
    },
    style={"height": "70vh"},
    className="ag-theme-balham",
)

layout = \
    html.Div([
        dbc.Container([
            dbc.Row([
                ### --> Left Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1"),
                ### --> <-- ###

                ### --> Main Content <-- ###
                dbc.Col([
                    html.Div([
                        html.Button("Options", className="btn btn-outline-primary btn-lg py-1 px-2 rounded mt-3 mb-1", id="grid-settings-btn"), 
                    ], className="d-inline-block"),
                    dbc.Collapse([
                        html.Div([
                            html.Div(["Select Columns"]),
                            html.Button("Reset Columns", className="btn btn-outline-secondary btn-sm py-1 px-2 ms-2 mt-1 rounded", id="reset-btn"),
                            dcc.Dropdown(
                                id='data-column-dropdown',
                                options=[{'label': col, 'value': col} for col in df.columns],
                                multi=True,
                                value=[option["value"] for option in [{'label': col, 'value': col} for col in df.columns]],
                                className='dbc m-2',
                            )
                        ], className="px-2 py-2 border rounded mx-2 my-2")
                    ], id="grid-settings-collapse", is_open=False),
                    ### --> Grid <-- ###
                    html.Div([
                        grid
                    ], className="m-3 mt-2 shadow-sm"),
                    ### --> <-- ###
                ], className="col-12 col-lg-10"),
                ### --> <-- ###

                ### --> Right Gutter <-- ###
                dbc.Col([
                    html.Div([])
                ], className="col-0 col-lg-1")
                ### --> <-- ###
            ])
        ], fluid=True),
    ])

### --> DON'T TOUCH THIS <-- ###

operators = {
    "greaterThanOrEqual": "ge",
    "lessThanOrEqual": "le",
    "lessThan": "lt",
    "greaterThan": "gt",
    "notEqual": "ne",
    "equals": "eq",
}


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
            df = df.loc[df[col].astype(
                "datetime64[ns]").between_time(crit1, crit2)]
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
    Input("data_refresh_signal", "data")
)
def infinite_scroll(request, signal):
    callback_id = ctx.triggered_id

    if callback_id == "data_refresh_signal":
        dff = pd.read_csv("data/raw_data.csv")
        # drop helper columns
        dff = dff.drop(
            columns=[
                "finishChargeTime",
                "trueDurationHrs",
                "true_peakPower_W",
                "Overstay",
                "Overstay_h"
            ]
        )
        # reverse data (most recent first)
        dff = dff[::-1]

        return {"rowData": dff.to_dict("records")}
    
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
    partial = dff.iloc[request["startRow"]: request["endRow"]]
    return {"rowData": partial.to_dict("records"), "rowCount": len(dff.index)}

### --> <-- ###


# @dash.callback(
#     Output("raw-data-grid", "rowData"),
#     Input("data_refresh_signal", "data")
# )
# def update_rowdata(signal):
#     df = db.get_df(r, "raw_data")
#     df = df.drop(
#         columns=[
#             "finishChargeTime",
#             "trueDurationHrs",
#             "true_peakPower_W",
#             "Overstay",
#             "Overstay_h"
#         ]
#     )
#     # reverse data (most recent first)
#     df = df[::-1]
#     return df.to_dict("records")


@dash.callback(
    Output("data-column-dropdown", "value"),
    Input("reset-btn", "n_clicks"),
    State("data-column-dropdown", 'options'),
    prevent_inital_call=True
)
def reset_columns(n, checklist_options):
    if n is not None and n % 2 != 0:
        return []
    return [option["value"] for option in checklist_options]


@dash.callback(
    Output('raw-data-grid', 'columnDefs'),
    Input('data-column-dropdown', 'value')
)
def update_columns(selected_columns):
    return [{"field": i} for i in selected_columns]


@dash.callback(
    Output("grid-settings-collapse", "is_open"),
    Input("grid-settings-btn", "n_clicks"),
    State("grid-settings-collapse", "is_open"),
)
def toggle_grid_collapse(button_press, is_open):
    if button_press:
        return not is_open
    return is_open


@dash.callback(
    Output("raw-data-grid", "className"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value")
)
def update_grid_theme(theme):
    if theme in [dbc.themes.DARKLY, dbc.themes.CYBORG, dbc.themes.SOLAR, dbc.themes.SUPERHERO, dbc.themes.VAPOR]:
        return "ag-theme-balham-dark"
    return "ag-theme-balham"
