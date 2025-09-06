import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_count_sets

dash.register_page(__name__, path="/ncd_report_pen_plus")

from data_storage import mahis_programs, mahis_facilities, age_groups


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
            html.H3("Non Communicable Disease (NCDs) Report"),
            
            # Hypertension Section
            html.H4("HYPERTENSION", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with BP <140/90",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "font-family":"serif",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Asthma Section
            html.H4("ASTHMA", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with severity recorded",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "font-family":"serif",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
               # COPD Section
            html.H4("COPD", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "font-family":"serif",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),

            # Mental Health Section
            html.H4("MENTAL HEALTH", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients hospitalized in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with medication side effects",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients reported stable",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "font-family":"serif",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Chronic Kidney Disease Section
            html.H4("CHRONIC KIDNEY DISEASE", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with urinalysis recorded",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients hospitalized in last month",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Diabetes Type 1 Section
            html.H4("DIABETES TYPE 1", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with complications",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
                # Diabetes Type 2 Section
            html.H4("DIABETES TYPE 2", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with complications",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients on insulin therapy",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Epilepsy Section
            html.H4("EPILEPSY", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with controlled seizures",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients hospitalized in last month",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Chronic Heart Failure Section
            html.H4("CHRONIC HEART FAILURE (CHF)", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with rheumatic heart disease",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with congenital heart disease",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients hospitalized in last month",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),
            
            html.Br(),
            
            # Sickle Cell Disease Section
            html.H4("SICKLE CELL DISEASE (SCD)", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": ["Category"], "id": "category"},
                    {"name": ["Cases", "Male"], "id": "male"},
                    {"name": ["Cases", "Female"], "id": "female"},
                    {"name": ["Cases", "Total"], "id": "total"},
                ],
                data=[
                    {
                        "category": "Patients enrolled in active care",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients newly registered",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who defaulted",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients who died",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients with visit in last month",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients on hydroxyurea therapy",
                        "male":0,"female":0,"total":0
                    },
                    {
                        "category": "Patients hospitalized in last month",
                        "male":0,"female":0,"total":0
                    },
                ],
                merge_duplicate_headers=True,
                style_table={"width": "200%", "overflowX": "auto"},
                style_header={
                    "backgroundColor": "#ccc",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "border": "1px solid black"
                },
                style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "font-family":"serif",
                            "border": "1px solid #ccc"
                        },
                style_data_conditional=[
                        {
                            'if': {'column_id': ['male', 'female', 'total']},
                            'textAlign': 'center'
                        }
                    ]
            ),

        ])
    )

layout = html.Div(className="container", children=[
    html.H1("MONTHLY NCD PEN PLUS REPORT", className="header"),

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
                    value="June",
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

    html.Div(id='ncd_pen_plus-table-container'),        
])


@callback(
    Output('ncd_pen_plus-table-container', 'children'),
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