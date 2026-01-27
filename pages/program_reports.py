import dash
from dash import html, dcc, Input, Output, callback, State, no_update, ALL, callback_context
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np
from dash.exceptions import PreventUpdate
import os
from helpers import build_single_chart
from datetime import datetime, timedelta

dash.register_page(__name__, path="/program_reports")
data = pd.read_parquet('data/latest_data_opd.parquet')

from datetime import datetime, timedelta
from dash import html, dcc

path = os.getcwd()
path_program_reports = os.path.join(path, 'data','visualizations','validated_prog_reports.json') 

# Helper for today's bounds
_today = datetime.now()
_start_of_today = _today.replace(hour=0, minute=0, second=0, microsecond=0)
_end_of_today = _today.replace(hour=23, minute=59, second=59, microsecond=0)

report_config_panel = html.Div(
    children=[
        dcc.Store(id="report-config-store"),
        html.Div(
            children=[
                html.Div(className="card-header", children=[
                    html.Div(
                        children="Choose program, report, and filters, then generate below", style={"color":"#006401","textAlign":"center"})
                ]),

                # Grid of controls
                html.Div(className="filter-container", children=[
                    # Program
                    html.Div(className="card-col", children=[
                        html.Label("Select Program", className="form-label"),
                        dcc.Dropdown(
                            id="program-selector",
                            options=[{"label": p, "value": p} for p in []],
                            placeholder="Choose a program…",
                            value="OPD Program",
                            clearable=True,
                            className="dropdown"
                        ),
                    ]),

                    # Report
                    html.Div(className="card-col", children=[
                        html.Label("Select Report", className="form-label"),
                        dcc.Dropdown(
                            id="report-selector",
                            options=[{"label": r, "value": r} for r in []],
                            placeholder="Choose a report…",
                            value=None,
                            clearable=True,
                            className="dropdown"
                        ),
                    ]),

                    # Date Range
                    html.Div(className="card-col", children=[
                        html.Label("Date Range (Default 30 days ago)", className="form-label"),
                        dcc.DatePickerRange(
                            id="prog-date-range-picker",
                            # Adjust to your data’s earliest date if you have it
                            min_date_allowed=datetime(2023, 1, 1),
                            max_date_allowed=_end_of_today,
                            initial_visible_month=_today,
                            start_date=_start_of_today,
                            end_date=_end_of_today - pd.Timedelta(days=1),
                            display_format="YYYY-MM-DD",
                            minimum_nights=0,
                        ),
                    ]),

                    # Health Facility
                    html.Div(className="card-col", children=[
                        html.Label("Health Facility", className="form-label"),
                        dcc.Dropdown(
                            id="prog-hf-filter",
                            options=[],  # Fill from your data in a callback
                            placeholder="All facilities",
                            value=None,
                            clearable=True,
                            multi=True,  # Often useful to pick multiple HFs
                            className="dropdown"
                        ),
                    ]),
                ], style={"display": "flex", "gap": "14px", "alignItems": "flex-start", "flexWrap": "wrap"}),

                # Actions row
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    children=[
                        
                        # LEFT BUTTONS
                        html.Div(
                            children=[
                                html.Button("Generate Report", id="btn-generate-report", n_clicks=0, className="btn btn-primary"),
                                html.Button("Reset", id="btn-reset-report", n_clicks=0, className="btn btn-secondary"),
                            ],
                            style={"display": "flex", "gap": "10px"}
                        ),

                        # RIGHT BUTTONS + STATUS
                        html.Div(
                            children=[
                                html.Button("CSV", id="btn-csv", n_clicks=0, className="btn btn-outline-secondary"),
                                html.Button("XLSX", id="btn-excel", n_clicks=0, className="btn btn-outline-secondary"),
                                html.Button("PNG", id="btn-png", n_clicks=0, className="btn btn-outline-secondary"),
                                html.Span(id="report-run-status", className="run-status", style={"marginLeft": "10px"})
                            ],
                            style={"display": "flex", "gap": "10px"}
                        ),
                    ]
                )
            ],
        ),
        dcc.Loading(
            id="reports-loading",
            type="circle",
            color="#006401",
            children=html.Div(id="reports-output", className="reports-output")
        ),
    ],
    style={"marginTop": "0px"}
)

def programs_report(data, programs_report_list):
    if len(programs_report_list) == 0:
        return html.Div('')
    else:
        json_data = programs_report_list[0]
        return html.Div(
                    build_single_chart(data, data, 10, json_data, style="")
            )


layout = html.Div(
    html.Div(children=[
            report_config_panel,
            html.Div(id='program-reports-container'),
            dcc.Interval(
                    id='prog-interval-update-today',
                    interval=60*60*1000,  # in milliseconds
                    n_intervals=0,
                ),
    ],style={"marginTop":"30px","backgroundColor":"white","border-radius":"4px","border":"1px","border-color":"black"})
        
)

@callback(
         Output("report-selector", "options"),
         Input("program-selector","value")
)

def update_filters(selected_program):
    with open(path_program_reports) as x:
        program_reports_data = json.load(x)
    filtered_reports_list = [r for r in program_reports_data["reports"] if r.get("program") == selected_program]
    filtered_object = {"reports":filtered_reports_list}
    program_reports = [x['report_name'] for x in filtered_object['reports']]
    return program_reports 

@callback(
    [Output('program-reports-container','children'),
     Output('prog-hf-filter', 'options'),
     Output("program-selector","options")],
    [Input('url-params-store', 'data'),
     Input("btn-generate-report", "n_clicks"),
     Input("report-selector", "value"),
     Input('prog-date-range-picker', 'start_date'),
     Input('prog-date-range-picker', 'end_date'),
     Input('prog-hf-filter', 'value'),
     ]
)
def generate_chart(urlparams, n_clicks, report_name, start_date, end_date, hf):
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
    try:
        data = pd.read_parquet(parquet_path)
        with open(path_program_reports) as x:
            program_reports_data = json.load(x)
        
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data['Gender'] = data['Gender'].replace({"M": "Male", "F": "Female"})

        if urlparams:
            data = data[data['Facility_CODE'].str.lower() == urlparams.lower()]
        else:
            return html.Div("Missing Parameters"),facilities_options, all_programs

        facilities = sorted(data['Facility'].dropna().unique().tolist())
        all_facility_item = "*All health facilities" if len(facilities) > 1 else None
        facilities_options = facilities + ([all_facility_item] if all_facility_item else [])

        all_programs = data['Program'].dropna().value_counts().index.tolist() + ["+ Create a Report"]

        # Check if we should show the error message or generate the chart
        # Only show error when button is clicked (n_clicks > 0) but required fields are missing
        if n_clicks and n_clicks > 0 and (not report_name or not hf):
            return (
                html.Div([
                    html.H4("Action Required", style={'color': '#e74c3c'}),
                    html.P("Please select a report and health facility, then click the generate button.",
                          style={'font-size': '16px', 'margin-top': '10px'})
                ], style={
                    'text-align': 'center',
                    'padding': '20px',
                    'background-color': '#f8f9fa',
                    'border': '1px solid #dee2e6',
                    'border-radius': '5px',
                    'margin': '20px 0'
                }),
                facilities_options,
                all_programs
            )
        
        # If no report selected or no button clicked yet, just return empty chart with options
        if not report_name or n_clicks == 0:
            return (
                programs_report(pd.DataFrame(), {}),
                facilities_options,
                all_programs
            )

        # Get the report configuration
        filtered_report_list = [
            r for r in program_reports_data.get("reports", [])
            if r.get("report_name") == report_name
        ]

        # Initialize base_df from the loaded data
        base_df = data.copy()
        
        # Handle hf parameter - check if it's valid
        hf_list = []
        if isinstance(hf, (list, tuple)):
            hf_list = [h for h in hf if h and h != "*All health facilities"]
        elif hf and hf != "*All health facilities":
            hf_list = [hf]
        
        # Filter base_df based on selected facilities
        if hf_list:
            base_df = base_df[base_df['Facility'].isin(hf_list)]
        else:
            # If no facility selected or "*All health facilities" is selected, use all data
            base_df = data.copy()
        
        # Check if filtering resulted in empty data
        if base_df.empty:
            return (
                html.Div([
                    html.H4("No Data Available", style={'color': '#e67e22'}),
                    html.P(f"No data found for the selected health facility(ies): {', '.join(hf_list)}",
                          style={'font-size': '16px', 'margin-top': '10px'})
                ], style={
                    'text-align': 'center',
                    'padding': '20px',
                    'background-color': '#fff3cd',
                    'border': '1px solid #ffeaa7',
                    'border-radius': '5px',
                    'margin': '20px 0'
                }),
                facilities_options,
                all_programs
            )

        filtered_data = base_df.copy()
        
        if start_date and end_date:
            try:
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                filtered_data_date = filtered_data[
                    (filtered_data['Date'] >= start) & (filtered_data['Date'] <= end)
                ]
            except Exception as e:
                filtered_data_date = filtered_data
        else:
            filtered_data_date = filtered_data

        # Generate the report
        return (
            programs_report(filtered_data_date, filtered_report_list),
            facilities_options,
            all_programs
        )
    
    except FileNotFoundError as e:
        return (
            html.Div([
                html.H4("Report error", style={'color': '#c0392b'}),
                html.P(f"Unable to find the report: Please ensure the report configuration file exists.",
                      style={'font-size': '16px', 'margin-top': '10px'})
            ], style={
                'text-align': 'center',
                'padding': '20px',
                'background-color': '#fddede',
                'border': '1px solid #f5c6cb',
                'border-radius': '5px',
                'margin': '20px 0'
            }),
            [],
            []
        )
    except Exception as e:
        return (
            html.Div([
                html.H4("Error Generating Chart", style={'color': '#c0392b'}),
                html.P(f"An unexpected error occurred: {str(e)}",
                      style={'font-size': '16px', 'margin-top': '10px'})
            ], style={
                'text-align': 'center',
                'padding': '20px',
                'background-color': '#fddede',
                'border': '1px solid #f5c6cb',
                'border-radius': '5px',
                'margin': '20px 0'
            }),
            [],
            []
        )
    
@callback(
    [Output('prog-date-range-picker', 'start_date'),
     Output('prog-date-range-picker', 'end_date')],
    Input('prog-interval-update-today', 'n_intervals')
)
def update_date_range(n):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0) - pd.Timedelta(days=30)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)  - pd.Timedelta(days=0)
    return start, end