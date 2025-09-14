import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from dash.exceptions import PreventUpdate
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

def build_table(filtered, all_data):
    filtered = filtered.replace(np.nan,'')
    new_patient_ids = filtered.loc[filtered['obs_value_coded'] == 'New patient', 'person_id'].unique()
    new_patients = filtered[filtered['person_id'].isin(new_patient_ids)]
    existing_patients = filtered[~filtered['person_id'].isin(new_patient_ids)]

    deaths_ids = filtered.loc[filtered['concept_name'] == 'Died', 'person_id'].unique()
    dead_patients = filtered[filtered['person_id'].isin(deaths_ids)]

    two_months_ago = pd.to_datetime(datetime.date.today() -relativedelta(month=datetime.date.today().month-2))
    old_ids = list(filtered.loc[filtered['Date'] < two_months_ago, 'person_id'].unique())
    new_ids = list(filtered.loc[filtered['Date'] >= two_months_ago, 'person_id'].unique())
    defaulted_ids = [x for x in old_ids if x not in new_ids]
    defaulted_patients = all_data[all_data['person_id'].isin(defaulted_ids)]

    first_of_month = filtered['Date'].max().replace(day=1)
    last_month_start = first_of_month - relativedelta(months=1)
    last_month_end = first_of_month - pd.Timedelta(days=1)
    last_month = filtered[(filtered['Date']>=last_month_start)&(filtered['Date']<=last_month_end)]
    last_month_ids = last_month['person_id'].unique()
    last_month_patients = all_data[all_data['person_id'].isin(last_month_ids)]
    filtered['ValueN'] = pd.to_numeric(filtered['ValueN'], errors='coerce')
    LBP_ids = filtered[(filtered['concept_name']=='SBP')&(filtered['ValueN']<140)]['person_id'].unique()
    LBP = filtered[filtered['person_id'].isin(LBP_ids)]

    diabetes_comp_ids = filtered.loc[filtered['concept_name'].isin(['Peripheral neuropathy','Deformity','Ulcers']), 'person_id'].unique()
    diabetes_comp = filtered[filtered['person_id'].isin(diabetes_comp_ids)]

    insulin_ids = filtered.loc[filtered['obs_value_coded'].isin(['Insulin']), 'person_id'].unique()
    insulin_patients = filtered[filtered['person_id'].isin(insulin_ids)]

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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
                    },
                    {
                        "category": "Patients with BP <140/90",
                            "male":create_count(LBP, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'M'),
                            "female":create_count(LBP, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension'], 'Gender', 'F'),
                            "total":create_count(LBP, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Asthma']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['COPD']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Mental Retardation',
                                                            'Drug Use Metal Disorder','Peurperal Mental Disorder',
                                                            'Alcohol Use Mental Disorder','Psychological Mental Disorder',
                                                            'Acute Organic Mental Disorder','Chronic Organic Mental Disorder']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Kidney failure']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
                    },
                    {
                        "category": "Patients with complications",
                            "male":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'M'),
                            "female":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes'], 'Gender', 'F'),
                            "total":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients with complications",
                            "male":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(diabetes_comp, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
                    },
                    {
                        "category": "Patients on insulin therapy",
                            "male":create_count(insulin_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'M'),
                            "female":create_count(insulin_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes'], 'Gender', 'F'),
                            "total":create_count(insulin_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Epilepsy']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Heart failure']),
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
                            "male":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'M'),
                            "female":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'F'),
                            "total":create_count(filtered, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease']),
                    },
                    {
                        "category": "Patients newly registered",
                            "male":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'M'),
                            "female":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'F'),
                            "total":create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease']),
                    },
                    {
                        "category": "Patients who defaulted",
                            "male":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'M'),
                            "female":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'F'),
                            "total":create_count(defaulted_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease']),
                    },
                    {
                        "category": "Patients who died",
                            "male":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'M'),
                            "female":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'F'),
                            "total":create_count(dead_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease']),
                    },
                    {
                        "category": "Patients with visit in last month",
                            "male":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'M'),
                            "female":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease'], 'Gender', 'F'),
                            "total":create_count(last_month_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Sickle cell disease']),
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
    Input('url-params-store', 'data'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(urlparams,year_filter, month_filter, hf_filter):
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')    
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')

    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
        print(search_url['Facility_CODE'].unique())
    else:
        PreventUpdate
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

    filtered = data_opd
    all_data = data_opd #for debugging
    
    return build_table(filtered, all_data)