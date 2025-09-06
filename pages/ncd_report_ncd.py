import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from datetime import datetime as dt
import os
from visualizations import create_count, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/ncd_report_ncd")

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
            html.H3("Non Communicable Disease (NCDs)"),

            html.H4("i) Cases Seen", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["NCD type"], "id": "ncd"},
                    {"name": ["New cases", "M"], "id": "new_m"},
                    {"name": ["New cases", "F"], "id": "new_f"},
                    {"name": ["All cases", "M"], "id": "all_m"},
                    {"name": ["All cases", "F"], "id": "all_f"},
                ],
                data=[
                    {"ncd": "Diabetes", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Hypertension", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Stroke", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "All suspected cancers", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "All confirmed cancers", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Palliative care clients", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Astha", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Depression", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "* Acute psychosis", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "* Chronic psychosis", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                    {"ncd": "Epilepsy", "new_m": 0, "new_f": 0, "all_m": 0, "all_f": 0},
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['new_m', 'new_f', 'all_m','all_f']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            html.P("Note: *psychosis from any cause."),

            html.H4("ii) Deaths by NCD type", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["NCD type"], "id": "ncd"},
                    {"name": ["No. Deaths", "M"], "id": "m"},
                    {"name": ["No. Deaths", "F"], "id": "f"},
                ],
                data=[
                    {"ncd": "Diabetes", "m": 0, "f": 0},
                    {"ncd": "Hypertension", "m": 0, "f": 0},
                    {"ncd": "*Other Cardio Vascula diseases", "m": 0, "f": 0},
                    {"ncd": "Cancer", "m": 0, "f": 0},
                    {"ncd": "Asthma/other CRD", "m": 0, "f": 0},
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['m', 'f']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            html.P("Note: *any other heart or blood related condition"),

            html.H4("iii) Number of injury and violence cases", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Injury type"], "id": "injury"},
                    {"name": ["No. of cases", "M"], "id": "m"},
                    {"name": ["No. of cases", "F"], "id": "f"},
                ],
                data=[
                    {"injury": "Road traffic injuries", "m": 0, "f": 0},
                    {"injury": "General Assault injuries", "m": 0, "f": 0},
                    {"injury": "*Gender based physical injuries", "m": 0, "f": 0},
                    {"injury": "Rape cases", "m": 0, "f": 0},
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['m', 'f']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            html.P("Note: *Any physical effect from Gender-Based Violence from minor to severe"),

            html.H4("iv) Injury related deaths", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Injury type"], "id": "injury"},
                    {"name": ["No. of deaths", "M"], "id": "m"},
                    {"name": ["No. of deaths", "F"], "id": "f"},
                ],
                data=[
                    {"injury": "Road traffic accidents", "m": 0, "f": 0},
                    {"injury": "Suicide", "m": 0, "f": 0},
                    {"injury": "Murder/homicide", "m": 0, "f": 0},
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%"},
                style_header={"backgroundColor": "#ccc", "fontWeight": "bold", "textAlign": "center"},
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['m', 'f']},
                            'textAlign': 'center'
                        }
                    ]
            ),
        ])
    )

layout = html.Div(className="container", children=[
    html.H1("MONTHLY NCD REPORT", className="header"),

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
                    value="2025",
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
                    value=None,
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

    html.Div(id='ncd_ncd-table-container'),        
])


@callback(
    Output('ncd_ncd-table-container', 'children'),
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