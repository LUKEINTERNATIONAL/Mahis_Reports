import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from datetime import datetime as dt
import os
import json
from isoweek import Week
from dash.exceptions import PreventUpdate
from reports_class import ReportTableBuilder
from visualizations import create_count, create_sum, create_count_sets, create_sum_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/reports")

relative_week = [str(week) for week in range(1, 53)]  # Can extend to 53 if needed
relative_month = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December',]
relative_quarter = ["Q1 Jan-Mar", "Q2 Apr-June", "Q3 Jul-Sep", "Q4 Oct-Dec"]
relative_year = [str(year) for year in range(2025, 2051)]

def get_week_start_end(week_num, year):
    """Returns (start_date, end_date) for a given week number and year"""
    # Validate inputs
    if week_num is None or year is None:
        raise ValueError("Week and year must be specified")
    
    try:
        week_num = int(week_num)
        year = int(year)
    except (ValueError, TypeError):
        raise ValueError("Week and year must be integers")
    
    if week_num < 1 or week_num > 53:
        raise ValueError(f"Week must be between 1-53 (got {week_num})")
    
    # Get start (Monday) and end (Sunday) of week
    week = Week(year, week_num)
    start_date = week.monday()    # Monday
    end_date = start_date + datetime.timedelta(days=6)  # Sunday
    
    return start_date, end_date

def get_month_start_end(month, year):
    # Validate inputs
    if month is None or year is None:
        raise ValueError("All parameters are required!")
    if month not in relative_month:
        raise ValueError(f"Invalid month: {month}. Must be one of {relative_month}")
    try:
        year = int(year)  # Ensure year is an integer
    except (ValueError, TypeError):
        raise ValueError(f"Invalid year: {year}. Must be a valid integer (e.g., 2023)")
    
    month_index = relative_month.index(month) + 1  # Convert to 1-based index
    start_date = datetime.date(year, month_index, 1)
    if month_index == 12:  # December
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month_index + 1, 1) - datetime.timedelta(days=1)
    
    return start_date, end_date

def get_quarter_start_end(quarter, year):
    # Validate inputs
    if quarter is None or year is None:
        raise ValueError("Enter Year and Quarter")
    if quarter not in relative_quarter:
        raise ValueError(f"Invalid quarter: {quarter}. Must be one of {relative_quarter}")
    try:
        year = int(year)  # Ensure year is an integer
    except (ValueError, TypeError):
        raise ValueError(f"Invalid year: {year}. Must be a valid integer (e.g., 2023)")
    
    # Map quarters to start and end months
    quarter_map = {
        "Q1 Jan-Mar": (1, 3),   # Jan - Mar
        "Q2 Apr-June": (4, 6),   # Apr - Jun
        "Q3 Jul-Sep": (7, 9),   # Jul - Sep
        "Q4 Oct-Dec": (10, 12)  # Oct - Dec
    }
    start_month, end_month = quarter_map[quarter]
    start_date = datetime.date(year, start_month, 1)
    # Last day of end_month
    if end_month == 12:
        end_date = datetime.date(year, 12, 31)
    else:
        end_date = datetime.date(year, end_month + 1, 1) - datetime.timedelta(days=1)
    
    return start_date, end_date

def load_report_options():
    """Load reports from JSON and return concatenated options for dropdown"""
    try:
        with open('data/reports.json', 'r') as f:
            data = json.load(f)
        
        # Create concatenated options: "ID - Report Name"
        options = [
            {'label': f"{report['report_id']} - {report['report_name']}", 
             'value': report['report_id']}
            for report in data['reports'] 
            if report.get('archived', 'False').lower() == 'false'
        ]
        return options
    except FileNotFoundError:
        print("report.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from report.json")
        return []
    except KeyError as e:
        print(f"Missing key in JSON: {e}")
        return []

def build_table(filtered, page_name):
    preg_patients = filtered[(filtered['concept_name']=='Pregnant woman')&(filtered['obs_value_coded']=='Yes')][['person_id']]
    preg_patients = filtered.merge(preg_patients, on = 'person_id', how='inner')

    spec_path = f"data/uploads/{page_name}.xlsx"
    if not os.path.exists(spec_path):
        error_msg = f"Report not found on Server. Request Admin to add report"
        return html.Div(error_msg)

    builder = ReportTableBuilder(spec_path, filtered)
    builder.load_spec()
    # print(builder.filters_map)
    components = builder.build_dash_components()
    return components

layout = html.Div(className="container", children=[
    html.H4("Select Report Parameters",style={'textAlign': 'center'}),
    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Report Name"),
                dcc.Dropdown(
                    id='report_name',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in mahis_facilities()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),
            html.Div([
                html.Label("Period Type"),
                dcc.Dropdown(
                    id='period_type-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in ['Weekly','Monthly','Quarterly']
                    ],
                    value='Monthly',
                    clearable=True
                )
            ], className="filter-input"),
            html.Div([
                html.Label("Year"),
                dcc.Dropdown(
                    id='year-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_year
                    ],
                    value=dt.now().strftime("%Y"),
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Week/Month/Quarter"),
                dcc.Dropdown(
                    id='month-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_month
                    ],
                    value=dt.now().strftime("%B"),
                    clearable=True
                )
            ], className="filter-input"),
            html.Div([
            html.Button(
                "Generate Report",
                id="generate-btn",
                n_clicks=0,
                style={
                    "backgroundColor": "#297952",
                    "color": "white",
                    "border": "none",
                    "padding": "8px 12px",
                    "borderRadius": "6px",
                    "cursor": "pointer",
                    "fontSize": "16px",
                    "marginTop": "0px",
                    "marginBottom": "10px"
                }
            ),
        ]),

        ]),
        
    ]),

    html.Div(id='standard-reports-table-container'),        
])

@callback(
    Output('month-filter', 'options'),
    Input('period_type-filter', 'value'),
)
def update_month_options(period_type):
    """Update dropdown options based on period type - always active"""
    if period_type == 'Weekly':
        return relative_week
    elif period_type == 'Monthly':
        return relative_month
    else:  # Quarterly
        return relative_quarter
    
@callback(
        Output('report_name', 'options'),
        Input('url-params-store', 'data'),
)
def update_report_dropdown(urlparams):
    return load_report_options()

@callback(
    [Output('standard-reports-table-container', 'children'),
     Output('generate-btn', 'n_clicks')],
    Input('generate-btn', 'n_clicks'),
    Input('url-params-store', 'data'),
    Input('period_type-filter', 'value'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('report_name', 'value'),
    prevent_initial_call=True
)
def update_table(clicks, urlparams, period_type, year_filter, month_filter, report_filter):
    # Only generate table when button is clicked
    if clicks is None or clicks == 0:
        raise PreventUpdate
    
    # Handle missing inputs to prevent errors
    if not urlparams or not period_type or not year_filter or not month_filter or not report_filter:
        return html.Div("Please fill all required filters")
    
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
    reports_json = os.path.join(path, 'data', 'reports.json')
    with open(reports_json, "r") as f:
        json_data = json.load(f)
    target = report_filter
    report = next(
                    (
                        r for r in json_data["reports"]
                        if r['report_id'] == target
                        and r["archived"].lower() == "false"
                    ),
                    None
                )
    if not report:
        return html.Div("Report Not Found")
    # Validate file exists
    if not os.path.exists(parquet_path):
        error_msg = f"PARQUET file not found at {parquet_path}"
        return html.Div(error_msg)
    
    data_opd = pd.read_parquet(parquet_path)
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd["DateValue"] = pd.to_datetime(data_opd["Date"]).dt.date
    today = dt.today().date()
    data_opd["months"] = data_opd["DateValue"].apply(lambda d: (today - d).days // 30)
    data_opd.to_csv('data/archive/hmis.csv')

    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
    else:
        return html.Div("No facility selected")
    
    try:
        if period_type == 'Weekly': 
            start_date, end_date = get_week_start_end(month_filter, year_filter)
            filtered = search_url[
                (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
            ]
            return build_table(filtered, report["page_name"]), 0
            
        elif period_type == 'Monthly': 
            start_date, end_date = get_month_start_end(month_filter, year_filter)
            filtered = search_url[
                (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
            ]
            # print(create_count(filtered, 'encounter_id','Encounter','REGISTRATION'))
            return build_table(filtered, report["page_name"]), 0
            
        else:  # Quarterly
            start_date, end_date = get_quarter_start_end(month_filter, year_filter)
            filtered = search_url[
                (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
            ]
            return build_table(filtered, report["page_name"]), 0
            
    except ValueError as e:
        print(f"Error: {e}")
        return html.Div(f"Error: {str(e)}")