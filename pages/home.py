import dash
from dash import html, dcc, Input, Output, callback, State, no_update, ALL, callback_context
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np
from dash.exceptions import PreventUpdate
import os
from flask import request
from helpers import build_charts_section, build_metrics_section
from datetime import datetime
from datetime import datetime as dt
from data_storage import DataStorage
from config import DATA_FILE_NAME_

# Importing parquet file path and from config

# importing referential columns from config
from config import (actual_keys_in_data, 
                    DATA_FILE_NAME_, 
                    DATE_, PERSON_ID_, ENCOUNTER_ID_,
                    FACILITY_, AGE_GROUP_, AGE_,
                    GENDER_, ENCOUNTER_, PROGRAM_,
                    NEW_REVISIT_, 
                    HOME_DISTRICT_, 
                    TA_, 
                    VILLAGE_, 
                    FACILITY_CODE_,
                    OBS_VALUE_CODED_,
                    CONCEPT_NAME_,
                    VALUE_,
                    VALUE_NUMERIC_,
                    DRUG_NAME_,
                    VALUE_NAME_)

dash.register_page(__name__, path="/home")

path = os.getcwd()
json_path = os.path.join(path, 'data', 'visualizations', 'validated_dashboard.json')

# Load data once to get date range
min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
max_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

path = os.getcwd()
last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]


# BUILD CHARTS
def build_charts_from_json(filtered, data_opd, delta_days, dashboards_json):
    # Load JSON configuration
    config = dashboards_json
    
    filtered = filtered.copy()
    filtered['Residence'] = filtered[HOME_DISTRICT_] + ', TA-' + filtered[TA_] + ', ' + filtered[VILLAGE_]
    delta_days = 7 if delta_days <= 0 else delta_days
    
    # Build metrics from counts section
    metrics = build_metrics_section(filtered, config["visualization_types"]["counts"])
    
    # Build charts from sections
    charts = build_charts_section(filtered, data_opd, delta_days, config["visualization_types"]["charts"]["sections"])
    
    return html.Div([
        html.Div(className="card-container-5", children=metrics),
        charts
    ])

def get_relative_date_range(option):
    from datetime import datetime, timedelta
    today = datetime.today().date()
    
    if option == 'Today':
        return today, today
    elif option == 'Yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif option == 'Last 7 Days':
        start_date = today - timedelta(days=7)
        return start_date, today
    elif option == 'Last 30 Days':
        start_date = today - timedelta(days=30)
        return start_date, today
    elif option == 'This Week':
        start_date = today - timedelta(days=today.weekday())
        return start_date, today
    elif option == 'Last Week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
        return start_date, end_date
    elif option == 'This Month':
        start_date = today.replace(day=1)
        return start_date, today
    elif option == 'Last Month':
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        return start_date, last_day_last_month
    else:
        return None, None

layout = html.Div(className="container", children=[
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='active-button-store', data='home'),
    html.Div([
        html.Div(
            [
                html.Button(item, className="menu-btn")
                for item in []
                ],
                className="horizontal-scroll",
                id="scrolling-menu"
            ),
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Relative Period"),
                dcc.Dropdown(
                    id='dashboard-period-type-filter',
                    options=[
                        {'label': item, 'value': item}
                        for item in ['Today', 'Yesterday', 'Last 7 Days', 'Last 30 Days','This Week','Last Week', 'This Month', 'Last Month']
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Custom Date Range"),
                dcc.DatePickerRange(
                    id='dashboard-date-range-picker',
                    min_date_allowed="2023-01-01",
                    max_date_allowed=datetime.now(),
                    initial_visible_month=datetime.now(),
                    start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    end_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0),
                    display_format='YYYY-MM-DD',
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Health Facility"),
                dcc.Dropdown(
                    id='dashboard-hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in []
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Age Group"),
                dcc.Dropdown(
                    id='dashboard-age-filter',
                    options=[
                        {'label': age, 'value': age}
                        for age in ['Over 5','Under 5']
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div(
                    children=[
                        html.Button("Apply", id="dashboard-btn-generate", n_clicks=0, className="btn btn-primary"),
                        html.Button("Reset", id="dashboard-btn-reset", n_clicks=0, className="btn btn-secondary"),
                    ],
                    style={"display": "flex", "gap": "10px", "margin-bottom": "10px"}
                ),
        ]),

]),
    html.Div(id='dashboard-container'),   
    dcc.Interval(
        id='dashboard-interval-update-today',
        interval=60*60*1000,  # in milliseconds
        n_intervals=0
    ),     
])

@callback(
        Output('scrolling-menu', 'children'),
        [Input('dashboard-interval-update-today', 'n_intervals'),
        Input('active-button-store', 'data')])

def update_menu(interval, color):
    
    with open(json_path, 'r') as f:
        menu_json = json.load(f)

    return [
        html.Button(
            d["report_name"],
            className="menu-btn active" if color == d["report_name"] else "menu-btn",
            id={"type": "menu-button", "name": d["report_name"]}
        )
        for d in menu_json
    ]


@callback(
    [Output('dashboard-container', 'children'),
     Output('dashboard-hf-filter', 'options'),
     Output('dashboard-hf-filter', 'value'),
     Output('active-button-store', 'data')],
    [
        Input('dashboard-btn-generate', 'n_clicks'),
        Input('dashboard-btn-reset', 'n_clicks'),
        Input({"type": "menu-button", "name": ALL}, "n_clicks"),
        Input('dashboard-interval-update-today', 'n_intervals') # For auto-refresh
    ],
    [
        State('url-params-store', 'data'),
        State('dashboard-date-range-picker', 'start_date'),
        State('dashboard-date-range-picker', 'end_date'),
        State('dashboard-period-type-filter', 'value'),
        State('dashboard-hf-filter', 'value'),
        State('dashboard-age-filter', 'value'),
        State({"type": "menu-button", "name": ALL}, "id"),
        State('active-button-store', 'data')
    ]
)
def update_dashboard(gen_clicks,reset_clicks, menu_clicks, interval, urlparams, start_date, end_date, period_type, hf, age, id_list, current_active):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    # Determine which report to show
    clicked_name = current_active
    if triggered_id and "menu-button" in triggered_id:
        prop_dict = json.loads(triggered_id.split('.')[0])
        clicked_name = prop_dict['name']

    if triggered_id == "dashboard-btn-reset.n_clicks":
        start_date = datetime.now()
        end_date = datetime.now()
        period_type = "Today"
        age = None

    # Date Logic
    start_dt = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0)
    end_dt = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)
    last_7_days = end_dt - pd.Timedelta(days=7)


    if period_type:
        s, e = get_relative_date_range(period_type)
        if s and e:
            start_dt, end_dt = pd.to_datetime(s), pd.to_datetime(e)

    # Load Data
    SQL = f"""
        SELECT *
        FROM 'data/{DATA_FILE_NAME_}'
        WHERE Date BETWEEN
        TIMESTAMP '{last_7_days}'
        AND TIMESTAMP '{end_dt.strftime('%Y-%m-%d %H:%M:%S')}'
        """
    data = DataStorage.query_duckdb(SQL)
    data[DATE_] = pd.to_datetime(data[DATE_], format='mixed')
    data[GENDER_] = data[GENDER_].replace({"M":"Male","F":"Female"})
    data["DateValue"] = pd.to_datetime(data[DATE_]).dt.date
    today = dt.today().date()
    data["months"] = data["DateValue"].apply(lambda d: (today - d).days // 30)

    # get user
    user_data_path = os.path.join(path, 'data', 'users_data.csv')
    if not os.path.exists(user_data_path):
        user_data = pd.DataFrame(columns=['user_id', 'role'])
    else:
        user_data = pd.read_csv(os.path.join(path, 'data', 'users_data.csv'))
    test_admin = pd.DataFrame(columns=['user_id', 'role'], data=[['m3his@dhd', 'reports_admin']])
    user_data = pd.concat([user_data, test_admin], ignore_index=True)

    user_info = user_data[user_data['user_id'] == urlparams.get('uuid', [None])[0]]
    if user_info.empty:
        return html.Div("Unauthorized User. Please contact system administrator."), no_update,no_update, clicked_name
    # data_opd = data_opd.dropna(subset = ['obs_value_coded','concept_name', 'Value','ValueN', 'DrugName', 'Value_name'], how='all')
    # data_opd.to_excel("data/archive/hmis.xlsx", index=False)
    
    # Filter by URL params (e.g. Facility Code)
    if urlparams.get('Location', [None])[0]:
        search_url = data[data[FACILITY_CODE_].str.lower() == urlparams.get('Location', [None])[0].lower()]
    else:
        return html.Div("Missing Parameters"), no_update, no_update, clicked_name

    # Apply Dropdown Filters
    mask = pd.Series(True, index=search_url.index)
    if hf:
        mask &= (search_url[FACILITY_] == hf)
    if age:
        mask &= (search_url[AGE_GROUP_] == age)
        
    filtered_data = search_url[mask].copy()

    # Apply Date Mask
    filtered_data_date = filtered_data[
        (filtered_data[DATE_] >= start_dt) & 
        (filtered_data[DATE_] <= end_dt)
    ]

    # Get JSON config for the report
    with open(json_path, 'r') as f:
        menu_json = json.load(f)
    dashboard_json = next((d for d in menu_json if d['report_name'] == clicked_name), menu_json[0])

    delta_days = (end_dt - start_dt).days
    hf_options = filtered_data[FACILITY_].sort_values().unique().tolist()

    return build_charts_from_json(filtered_data_date, filtered_data, delta_days, dashboard_json), hf_options,hf_options[0],  clicked_name

@callback(
    Output('dashboard-date-range-picker', 'start_date'),
    Output('dashboard-date-range-picker', 'end_date'),
    Input('dashboard-interval-update-today', 'n_intervals'),
    State('dashboard-period-type-filter', 'value'),
)
def update_date_range(n, period_type):
    if period_type != "Today":
        raise PreventUpdate

    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end

@callback(
     Output('dashboard-date-range-picker', 'start_date', allow_duplicate=True),
     Output('dashboard-date-range-picker', 'end_date', allow_duplicate=True),
    Output('dashboard-period-type-filter', 'value', allow_duplicate=True),
    Output('dashboard-hf-filter', 'value', allow_duplicate=True),
    Output('dashboard-age-filter', 'value', allow_duplicate=True),
    Input('dashboard-btn-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end, None, None, None

@callback(
    [Output('dashboard-period-type-filter', 'style'),
     Output('dashboard-date-range-picker', 'style', allow_duplicate=True),
     Output('dashboard-hf-filter', 'style'),
     Output('dashboard-age-filter', 'style')],
    [Input('dashboard-btn-reset', 'n_clicks'),
     Input('dashboard-btn-generate', 'n_clicks')],
    prevent_initial_call=True
)
def change_style(generate, reset):
    # Returns bold items on generate to indicate active filters
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None
    if triggered_id == "dashboard-btn-generate.n_clicks":
        style_active = {
                    # "display": "flex",
                    "alignItems": "center",
                    "gap": "5px",
                    "border": "3px solid green",
                    "borderRadius": "8px"
                    }
        return style_active, style_active, style_active, style_active
    else:
        style_default = {}
        return style_default,style_default,style_default, style_default,
