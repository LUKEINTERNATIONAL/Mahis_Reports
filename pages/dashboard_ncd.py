import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import os
import numpy as np
from dash.exceptions import PreventUpdate
import os
from visualizations import (create_column_chart, 
                          create_count,
                          create_pie_chart,
                          create_line_chart,
                          create_age_gender_histogram,
                          create_horizontal_bar_chart,
                          create_pivot_table)
from datetime import datetime, timedelta

from data_storage import mahis_programs, mahis_facilities, age_groups, new_revisit

STATIC_DATE_FILTER = 0
RELATIVE_DAYS=7

dash.register_page(__name__, path="/dashboard_ncd")

# Load data once to get date range
min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
max_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

path = os.getcwd()
last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]

def build_charts(filtered, data_opd, delta_days):
    filtered['Residence'] = filtered['Home_district'] + ', TA-' + filtered['TA'] + ', ' + filtered['Village']
    filtered = filtered.replace(np.nan,'')
    new_patient_ids = filtered.loc[filtered['obs_value_coded'] == 'New patient', 'person_id'].unique()
    new_patients = filtered[filtered['person_id'].isin(new_patient_ids)]
    not_diabetes_hypertension = new_patients[(new_patients['Encounter'].isin(['OUTPATIENT DIAGNOSIS','DIAGNOSIS']))&
                                             (~new_patients['obs_value_coded'].isin(['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus','Hypertension']))]
    delta_days = 7 if delta_days <=0 else delta_days
    return html.Div([

        html.Div(
        className="card-container-5",
        children=[
            html.Div(
                html.Div([
                    html.H2(create_count(filtered,'person_id'), className="metric-value"),
                    html.H4("NCD Attendance", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(filtered,'person_id','Gender', 'M'), className="metric-value"),
                    html.H4("Attendance Male", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(filtered,'person_id','Gender', 'F'), className="metric-value"),
                    html.H4("Attendance Female", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(filtered,'encounter_id', 'Age_Group', 'Over 5'), className="metric-value"),
                    html.H4("Attendance Over5", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(filtered,'encounter_id', 'Age_Group', 'Under 5'), className="metric-value"),
                    html.H4("Attendance Under5", className="metric-title"),
                ], className="card")
            ),
        ],
    ), 
        html.Div(
        className="card-container-5",
        children=[
            html.Div(
                html.Div([
                    html.H2(create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Diabetes','Type 1 diabetes','Type 2 diabetes','Diabetes mellitus']), className="metric-value"),
                    html.H4("Diabetes New Cases", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 1 diabetes']), className="metric-value"),
                    html.H4("Diabetes Type 1 New Cases", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Type 2 diabetes']), className="metric-value"),
                    html.H4("Diabetes Type 2 New Cases", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(new_patients, 'encounter_id', 'Encounter', ['OUTPATIENT DIAGNOSIS','DIAGNOSIS'],
                                'Program', 'NCD PROGRAM', 'obs_value_coded',['Hypertension']), className="metric-value"),
                    html.H4("Hypertension New Cases", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(create_count(not_diabetes_hypertension,'encounter_id'), className="metric-value"),
                    html.H4("Other New NCDs", className="metric-title"),
                ], className="card")
            ),
        ],
    ),
        # NCD Attendance Section
        html.Div([
            html.H2("General",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='daily-opd-attendance',
                        figure=create_line_chart(df=data_opd[data_opd['Date']>=str(datetime.now()- pd.Timedelta(days=delta_days))], date_col='Date', y_col='encounter_id',
                                          title='Daily NCD Attendance - Last 7 days', x_title='Date', y_title='Number of Patients',legend_title="Legend",
                                          ),
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='residency',
                        figure=create_pivot_table(filtered.replace('OPD Program', 'Number of Patients'),['Residence'],'Program','person_id','Home Locations','person_id','count'),
                        className="card-2"
                    ),
                    
                ]
            ),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='daily-opd-attendance',
                        figure=create_age_gender_histogram(df=filtered, age_col='Age', gender_col='Gender',
                                                title='Age Distribution', xtitle='Age', ytitle='Number of patients', bin_size=5),
                        className="card-2"
                    ),
                ]
            )
            
        ]),

        # NCD Attendance Section
        html.Div([
            html.H2("NCD Risk Factors",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='ncd_cases',
                        figure=create_pie_chart(filtered,names_col='obs_value_coded',values_col='encounter_id',unique_column='encounter_id',
                                                filter_col1='concept_name',filter_value1='Does the patient drink alcohol?',title='Alcohol Risk'), 
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='ncd_cases',
                        figure=create_pie_chart(filtered,names_col='obs_value_coded',values_col='encounter_id',unique_column='encounter_id',
                                                filter_col1='concept_name',filter_value1='Smoking history',title='Smoking Risk'), 
                        className="card-2"
                    ),
                ]
            ),
            
        ]),
        
        # NCD Section
        html.Div([
            html.H2("Diagnoses, Complications and Treatment",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='ncd_cases',
                        figure=create_column_chart(new_patients[new_patients['obs_value_coded']!=''],x_col='obs_value_coded',y_col='encounter_id',title='New NCD Patients',
                                                   unique_column='obs_value_coded',x_title='NCD Type',y_title='Number of Patients',filter_col1='Encounter',
                                                   filter_value1=['OUTPATIENT DIAGNOSIS','DIAGNOSIS']), 
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='all-cases',
                        figure=create_column_chart(filtered[filtered['obs_value_coded']!=''],x_col='obs_value_coded',y_col='encounter_id',title='All NCD Patients Registered at the Facility',
                                                   unique_column='obs_value_coded',x_title='NCD Type',y_title='Number of Patients',filter_col1='Encounter',
                                                   filter_value1=['OUTPATIENT DIAGNOSIS','DIAGNOSIS']),
                        className="card-2"
                    ),
                ]
            ),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='ncd_complications',
                        figure=create_pie_chart(filtered,names_col='concept_name',values_col='encounter_id',unique_column='encounter_id',
                                                filter_col1='concept_name',filter_value1=['Peripheral neuropathy','Deformity','Ulcers'],
                                                filter_col2='obs_value_coded', filter_value2='Yes', title='NCD Complications Foot'), 
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='meds',
                        figure=create_pivot_table(df=filtered, index_col1='DrugName',columns_col1='Program',
                                              values_col='ValueN',title='Aggregate NCD Drugs Dispensed',
                                              filter_col1='Encounter', filter_value1='DISPENSING',
                                              aggfunc='sum'),
                        className="card-2"
                    ),
                ]
            )
        ]),
        
    ])

layout = html.Div(className="container", children=[
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Visit Type"),
                dcc.Dropdown(
                    id='ncd-visit-type-filter',
                    options=[
                        {'label': item, 'value': item}
                        for item in new_revisit()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='ncd-date-range-picker',
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
                    id='ncd-hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in mahis_facilities()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Age Group"),
                dcc.Dropdown(
                    id='ncd-age-filter',
                    options=[
                        {'label': age, 'value': age}
                        for age in age_groups()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),
        ]),

]),
    html.Div(id='ncd-dashboard-container'),   
    dcc.Interval(
        id='ncd-interval-update-today',
        interval=10*60*1000,  # in milliseconds
        n_intervals=0
    ),     
])

# Callback to update all components based on date range
@callback(
    [Output('ncd-dashboard-container', 'children'),
     Output('ncd-hf-filter', 'options')],
    [
        Input('url-params-store', 'data'),
        Input('ncd-date-range-picker', 'start_date'),
        Input('ncd-date-range-picker', 'end_date'),
        Input('ncd-visit-type-filter', 'value'),
        Input('ncd-hf-filter', 'value'),
        Input('ncd-age-filter', 'value')
    ]
)
def update_dashboard(urlparams, start_date, end_date, visit_type, hf, age):
    start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59, microsecond=0)
    delta_days = (end_date - start_date).days
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')    
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd = data_opd[data_opd['Program']=='NCD PROGRAM']
    data_opd.to_excel('./data/archive/hmis.xlsx')
    

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
    
    return build_charts(filtered_data_date, filtered_data, delta_days), filtered_data['Facility'].sort_values().unique().tolist()

@callback(
    [Output('ncd-date-range-picker', 'start_date'),
     Output('ncd-date-range-picker', 'end_date')],
    Input('ncd-interval-update-today', 'n_intervals')
)
def update_date_range(n):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end