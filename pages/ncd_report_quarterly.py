import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/ncd_report_quarterly")

relative_quarter = ["Q1 Jan-Mar", "Q2 Apr-June", "Q3 Jul-Sep", "Q4 Oct-Dec"]
relative_year = [str(year) for year in range(2020, 2051)]

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

def build_table(filtered):
    return html.Table(
        html.Div([
            html.H3("NON COMMUNICABLE DISEASES QUARTERLY REPORTING FORM", style={'textAlign': 'center', 'fontSize': '14px'}),
            
            html.Div([
                # First Column
                html.Div([
                    # Hypertension Section
                    html.H4("HYPERTENSION", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Patients enrolled and active in care", "count": ""},
                            {"category": "Patients newly registered during reporting period", "count": ""},
                            {"category": "Patients who have defaulted during the reporting period", "count": ""},
                            {"category": "Patients with a visit in last 3 months", "count": ""},
                            {"category": "Currently enrolled patients that have ever experienced a complication", "count": ""},
                            {"category": "Patients with BP below 140/90 (last 3 months, excluding new patients)", "count": ""}
                        ],
                        style_table={"width": "100%"},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
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
                    
                    html.Br(),
                    
                    # Asthma Section
                    html.H4("ASTHMA", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Patients enrolled and active in care", "count": ""},
                            {"category": "Patients newly registered during reporting period", "count": ""},
                            {"category": "Patients who have defaulted during the reporting period", "count": ""},
                            {"category": "Patients with a visit in last 3 months", "count": ""},
                            {"category": "Patients with disease severity recorded at most recent visit", "count": ""},
                            {"category": "Patients with disease controlled (intermittent/mild persistent)", "count": ""},
                            {"category": "Patients hospitalized for the condition since last visit", "count": ""}
                        ],
                        style_table={"width": "100%"},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'count'},
                                'textAlign': 'center'
                            }
                        ]
                    ),
                    
                    html.Br(),
                    
                    # Epilepsy Section
                    html.H4("EPILEPSY", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Patients enrolled and active in care", "count": ""},
                            {"category": "Patients newly registered during reporting period", "count": ""},
                            {"category": "Patients who have defaulted during the reporting period", "count": ""},
                            {"category": "Patients with a visit in last 3 months", "count": ""},
                            {"category": "Patients with no seizures since last visit", "count": ""},
                            {"category": "Patients hospitalized since last visit", "count": ""}
                        ],
                        style_table={"width": "100%"},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'count'},
                                'textAlign': 'center'
                            }
                        ]
                    ),
                    
                    html.Br(),
                    
                    # Mental Health Section
                    html.H4("MENTAL HEALTH", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Patients enrolled and active in care", "count": ""},
                            {"category": "Patients newly registered during reporting period", "count": ""},
                            {"category": "Patients who have defaulted during the reporting period", "count": ""},
                            {"category": "Patients with a visit in last 3 months", "count": ""},
                            {"category": "Patients hospitalized since last visit", "count": ""},
                            {"category": "Patients with medication side effects at last visit", "count": ""},
                            {"category": "Patients reported as stable at last visit", "count": ""}
                        ],
                        style_table={"width": "100%"},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'count'},
                                'textAlign': 'center'
                            }
                        ]
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                
                # Second Column
                html.Div([
                    # Diabetes Section
                    html.H4("DIABETES", style={'backgroundColor': '#006401', 'padding': '5px','color':'white','marginLeft':'100px'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Currently enrolled patients with complications", "count": ""},
                            {"category": "Type 1 patients enrolled and active in care", "count": ""},
                            {"category": "Type 1 patients newly registered", "count": ""},
                            {"category": "Type 1 patients who have defaulted", "count": ""},
                            {"category": "Type 2 patients enrolled and active in care", "count": ""},
                            {"category": "Type 2 patients newly registered", "count": ""},
                            {"category": "Type 2 patients who have defaulted", "count": ""},
                            {"category": "Type 1 patients with visit in last 3 months", "count": ""},
                            {"category": "Type 2 patients with visit in last 3 months", "count": ""},
                            {"category": "Type 1 patients with FBS <=7mmol/l or <=126 mg/dL", "count": 238},
                            {"category": "Type 2 patients with FBS <=7mmol/l or <=126 mg/dL", "count": ""},
                            {"category": "Type 2 patients on Insulin", "count": ""}
                        ],
                        style_table={"width": "100%",'marginLeft':'100px'},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'count'},
                                'textAlign': 'center'
                            }
                        ]
                    ),
                    
                    html.Br(),
                    
                    # COPD Section
                    html.H4("COPD", style={'backgroundColor': '#006401', 'padding': '5px','color':'white','marginLeft':'100px'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Category", "id": "category"},
                            {"name": "Count", "id": "count"}
                        ],
                        data=[
                            {"category": "Patients newly registered during reporting period", "count": ""},
                            {"category": "Patients enrolled and active in care", "count": ""},
                            {"category": "Patients who have defaulted", "count": ""},
                            {"category": "Patients with a visit in last 3 months", "count": ""}
                        ],
                        style_table={"width": "100%",'marginLeft':'100px'},
                        style_header={
                            "backgroundColor": "#f7f7f7",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "5px",
                            "border": "1px solid #ccc"
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'count'},
                                'textAlign': 'center'
                            }
                        ]
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'width': '100%', 'display': 'flex'})
        ]),
    )

layout = html.Div(className="container", children=[
    html.H1("NON COMMUNICABLE DISEASES QUARTERLY REPORTING FORM", className="header"),

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
                html.Label("Quarter"),
                dcc.Dropdown(
                    id='quarter-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_quarter
                    ],
                    value="Q1 Jan-Mar",
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

    html.Div(id='ncd_quarterly-table-container'),        
])


@callback(
    Output('ncd_quarterly-table-container', 'children'),
    Input('year-filter', 'value'),
    Input('quarter-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(year_filter, quarter_filter, hf_filter):
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
        
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    try:
        start_date, end_date = get_quarter_start_end(quarter_filter, year_filter)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    filtered = data_opd[
        (pd.to_datetime(data_opd['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(data_opd['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]
    
    return build_table(filtered)