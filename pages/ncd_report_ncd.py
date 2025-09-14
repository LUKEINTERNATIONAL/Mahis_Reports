import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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
    filtered = filtered.replace(np.nan,'')
    new_patient_ids = filtered.loc[filtered['obs_value_coded'] == 'New patient', 'person_id'].unique()
    new_patients = filtered[filtered['person_id'].isin(new_patient_ids)]
    existing_patients = filtered[~filtered['person_id'].isin(new_patient_ids)]

    deaths_ids = filtered.loc[filtered['concept_name'] == 'Died', 'person_id'].unique()
    dead_patients = filtered[filtered['person_id'].isin(deaths_ids)]

    
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
                    {"ncd": "Diabetes", 
                        "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'F')},
                                
                    {"ncd": "Hypertension", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F')},
                    {"ncd": "Stroke", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Stroke'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Stroke'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Stroke'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Stroke'], 'Gender', 'F')},
                    {"ncd": "All suspected cancers", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suspected cancer'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suspected cancer'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suspected cancer'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suspected cancer'], 'Gender', 'F')},
                    {"ncd": "All confirmed cancers", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'F')},
                    {"ncd": "All palliative care clients", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['palliative care'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['palliative care'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['palliative care'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['palliative care'], 'Gender', 'F')},
                    {"ncd": "Asthma", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F')},
                    {"ncd": "Depression", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Depression'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Depression'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Depression'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Depression'], 'Gender', 'F')},
                    {"ncd": "* Acute psychosis", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis acute'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis acute'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis acute'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis acute'], 'Gender', 'F')},
                    {"ncd": "* Chronic psychosis", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis chronic'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis chronic'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis chronic'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Psychosis chronic'], 'Gender', 'F')},
                    {"ncd": "Epilepsy", 
                     "new_m": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'), 
                        "new_f": create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'), 
                        "all_m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'), 
                        "all_f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F')},
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
                    {"ncd": "Diabetes", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus'], 'Gender', 'F')},
                    {"ncd": "Hypertension", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F')},
                    {"ncd": "*Other Cardio Vascula diseases", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure','Other heart diseases', 'Rheumatic heart disease',
                                                                             'Congenital heart disease','Myocarditis','Cardiac failure',
                                                                             'Percardio disease','Infective endocarditis', 'Pericardio effusion,'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure','Other heart diseases', 'Rheumatic heart disease',
                                                                             'Congenital heart disease','Myocarditis','Cardiac failure',
                                                                             'Percardio disease','Infective endocarditis', 'Pericardio effusion,'], 'Gender', 'F')},
                    {"ncd": "Cancer", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kaposis sarcoma','Confirmed cancer','Growth','Tumours or Oral cancers'], 'Gender', 'F')},
                    {"ncd": "Asthma/other CRD", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F')},
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
                    {"injury": "Road traffic injuries", 
                        "m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Road Traffic Accidents, RTA'], 'Gender', 'M'), 
                        "f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Road Traffic Accidents, RTA'], 'Gender', 'F')},
                    {"injury": "General Assault injuries", 
                        "m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Assault'], 'Gender', 'M'), 
                        "f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Assault'], 'Gender', 'F')},
                    {"injury": "*Gender based physical injuries", 
                        "m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Assault'], 'Gender', 'M'), 
                        "f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Assault'], 'Gender', 'F')},
                    {"injury": "Rape", 
                        "m": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Rape'], 'Gender', 'M'), 
                        "f": create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Rape'], 'Gender', 'F')},
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
                    {"injury": "Road traffic accidents", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Road Traffic Accidents, RTA'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Road Traffic Accidents, RTA'], 'Gender', 'F')},
                    {"injury": "Suicide", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suicide'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Suicide'], 'Gender', 'F')},
                    {"injury": "Murder/homicide", 
                        "m": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Murder','Homicide'], 'Gender', 'M'), 
                        "f": create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Murder','Homicide'], 'Gender', 'F')},
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
    filtered = filtered[filtered['Program']=='NCD PROGRAM']
    # filtered = data_opd #for debugging
    
    return build_table(filtered)