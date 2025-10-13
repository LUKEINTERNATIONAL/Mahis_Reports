import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/htc_health_facility_report")

relative_month = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December',]
relative_year = [str(year) for year in range(2020, 2051)]

def get_month_start_end(month, year):
    # Validate inputs
    if month is None or year is None:
        raise ValueError("Enter Year and Month")
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

def build_table(filtered):
    return html.Table(
        html.Div([
            html.H3("HIV Testing and Counselling (HTC) Summary"),

            # --- Sex / Pregnancy ---
            html.H4("Sex / Pregnancy", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Category", "id": "category"},
                    {"name": "Clients Tested", "id": "value"},
                ],
                data=[
                    {"category": "Male", "value": 0},
                    {"category": "Female Non Pregnant", "value": 0},
                    {"category": "Female Pregnant", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- Age Groups ---
            html.H4("Age Groups", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Age Group", "id": "category"},
                    {"name": "Clients Tested", "id": "value"},
                ],
                data=[
                    {"category": "0–11 months", "value": 0},
                    {"category": "1–14 years", "value": 0},
                    {"category": "15–24 years", "value": 0},
                    {"category": "25+ years", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- HTC Access Type ---
            html.H4("HTC Access Type", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Access Type", "id": "category"},
                    {"name": "Clients Tested", "id": "value"},
                ],
                data=[
                    {"category": "PITC", "value": 0},
                    {"category": "FRS", "value": 0},
                    {"category": "Other", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- Last HIV Test ---
            html.H4("Last HIV Test", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Previous Test Result", "id": "category"},
                    {"name": "Clients Tested", "id": "value"},
                ],
                data=[
                    {"category": "Never Tested", "value": 0},
                    {"category": "Previous Negative", "value": 0},
                    {"category": "Previous Positive", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- Partner Present ---
            html.H4("Partner Present", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Partner Status", "id": "category"},
                    {"name": "Clients Tested", "id": "value"},
                ],
                data=[
                    {"category": "Partner Present", "value": 0},
                    {"category": "Partner Not Present", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- Outcome Summary ---
            html.H4("Outcome Summary", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Test Outcome", "id": "category"},
                    {"name": "Clients", "id": "value"},
                ],
                data=[
                    {"category": "Single Negative", "value": 0},
                    {"category": "Test 1 & 2 Positive", "value": 0},
                    {"category": "Discordant", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),

            # --- Result Given to Client ---
            html.H4("Result Given to Client", style={'backgroundColor': '#006401', 'padding': '5px', 'color': 'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Result Category", "id": "category"},
                    {"name": "Clients", "id": "value"},
                ],
                data=[
                    {"category": "New Negative", "value": 0},
                    {"category": "New Positive", "value": 0},
                    {"category": "Inconclusive", "value": 0},
                    {"category": "Total", "value": 0},
                ],
                style_table={"width": "60%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
            ),
        ])
    )

layout = html.Div(className="container", children=[
    html.H1("HTS FACILITY MONTHLY REPORT", className="header"),

    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Year"),
                dcc.Dropdown(
                    id='year-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_year
                    ],
                    value=2025,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Month"),
                dcc.Dropdown(
                    id='month-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_month
                    ],
                    value='June',
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Health Facility"),
                dcc.Dropdown(
                    id='hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in mahis_facilities()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

        ]),
        
    ]),

    html.Div(id='hts_monthly_general-table-container'),        
])


@callback(
    Output('hts_monthly_general-table-container', 'children'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(year_filter, month_filter, hf_filter):
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
        
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    try:
        start_date, end_date = get_month_start_end(month_filter, year_filter)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    filtered = data_opd[
        (pd.to_datetime(data_opd['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(data_opd['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]
    
    return build_table(filtered)