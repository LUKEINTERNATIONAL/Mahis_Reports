import dash
from dash import html, dcc, Input, Output, callback, State, no_update, ALL, callback_context
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np
from dash.exceptions import PreventUpdate
import os
from helpers import build_charts_section, build_metrics_section
from datetime import datetime

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
    filtered['Residence'] = filtered['Home_district'] + ', TA-' + filtered['TA'] + ', ' + filtered['Village']
    delta_days = 7 if delta_days <= 0 else delta_days
    
    # Build metrics from counts section
    metrics = build_metrics_section(filtered, config["visualization_types"]["counts"])
    
    # Build charts from sections
    charts = build_charts_section(filtered, data_opd, delta_days, config["visualization_types"]["charts"]["sections"])
    
    return html.Div([
        html.Div(className="card-container-5", children=metrics),
        charts
    ])

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
                html.Label("Visit Type"),
                dcc.Dropdown(
                    id='dashboard-visit-type-filter',
                    options=[
                        {'label': item, 'value': item}
                        for item in ['New', 'Revisit']
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
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

def update_menu(menu_items, color):
    
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




# Callback to update all components based on date range
@callback(
    [Output('dashboard-container', 'children'),
     Output('dashboard-hf-filter', 'options'),
     Output('active-button-store', 'data')],
    [
        Input('url-params-store', 'data'),
        Input('dashboard-date-range-picker', 'start_date'),
        Input('dashboard-date-range-picker', 'end_date'),
        Input('dashboard-visit-type-filter', 'value'),
        Input('dashboard-hf-filter', 'value'),
        Input('dashboard-age-filter', 'value'),
        Input({"type": "menu-button", "name": ALL}, "n_clicks"),
        State({"type": "menu-button", "name": ALL}, "id")
    ]
)
def update_dashboard(urlparams, start_date, end_date, visit_type, hf, age,n_clicks_list, id_list):
    
    start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59, microsecond=0)
    delta_days = (end_date - start_date).days
    
    with open(json_path, 'r') as f:
        menu_json = json.load(f)
    name_to_title = {d["report_id"]: d["report_name"] for d in menu_json}

    triggered = callback_context.triggered
    clicked_name = 'Summary'
    
    if triggered and "menu-button" in triggered[0]["prop_id"]:
            # Extract the name from the triggered input
            triggered_id = eval(triggered[0]["prop_id"].split(".")[0])  # converts string back to dict
            clicked_name = triggered_id["name"]

    clicked_title = name_to_title.get(clicked_name, clicked_name)
    for dashboard in menu_json:
        if dashboard['report_name'] == clicked_name:
            dashboard_json = dashboard
 
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Dashboard not found: {clicked_title}")
    
    
    data_opd = pd.read_parquet(parquet_path)
    # print(sorted(list(data_opd)))
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd['Gender'] = data_opd['Gender'].replace({"M":"Male","F":"Female"})
    # data_opd = data_opd[data_opd['Program']=='OPD Program']
    # data_opd.to_excel('data/archive/hmis.xlsx')
    

    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
    else:
        PreventUpdate
        
        
    mask = pd.Series(True, index=search_url.index)
    if hf:
        mask &= (search_url['Facility'] == hf)
    if age:
        mask &= (search_url['Age_Group'] == age)

        
    filtered_data = search_url[mask].copy()

    filtered_data_date = filtered_data[
        (pd.to_datetime(filtered_data['Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(filtered_data['Date']) <= pd.to_datetime(end_date))
    ]
    
    return build_charts_from_json(filtered_data_date, filtered_data, delta_days, dashboard_json), filtered_data['Facility'].sort_values().unique().tolist(), clicked_name

@callback(
    [Output('dashboard-date-range-picker', 'start_date'),
     Output('dashboard-date-range-picker', 'end_date')],
    Input('dashboard-interval-update-today', 'n_intervals')
)
def update_date_range(n):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end
