import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import os
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

STATIC_DATE_FILTER = 1
RELATIVE_DAYS=7

dash.register_page(__name__, path="/dashboard_opd")

# Load data once to get date range
path = os.getcwd()
data = pd.read_csv(f'{path}/data/latest_data_opd.csv',dtype={16: str})
data = data[data['Program']=="OPD Program"]
min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
max_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

path = os.getcwd()
last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]

def build_charts(filtered, data_opd):
    return html.Div([
        # OPD Attendance Section
        html.Div([
            html.H2("OPD Attendance",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='daily-opd-attendance',
                        figure=create_line_chart(df=data_opd[data_opd['Date']>=str(datetime.now()- pd.Timedelta(days=RELATIVE_DAYS))], date_col='Date', y_col='encounter_id',
                                          title='Daily OPD Attendance - Last 7 days', x_title='Date', y_title='Number of Patients',legend_title="Legend",
                                          ),
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='new-returning-visits',
                        figure=create_pie_chart(df=filtered, names_col='new_revisit', values_col='encounter_id',
                                        title='Aggregate Patient Visit Type (New or Revisit)'),
                        className="card-2"
                    ),
                ]
            )
        ]),
        
        # Malaria Section
        html.Div([
            html.H2("Malaria",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='daily-fever-malaria-cases',
                        figure=create_column_chart(df=data_opd[data_opd['Date']>=str(datetime.now()- pd.Timedelta(days=RELATIVE_DAYS))], x_col='Date', y_col='encounter_id',
                                          title='Daily Fever and Malaria Cases - Last 7 days', x_title='Date', y_title='Number of Patients',
                                          filter_col1='obs_value_coded',filter_value1=['Fever','Malaria'],color='obs_value_coded',legend_title="Legend"),
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='daily-lab-fever-tests',
                        figure=create_column_chart(df=data_opd[data_opd['Date']>=str(datetime.now()- pd.Timedelta(days=RELATIVE_DAYS))], x_col='Date', y_col='encounter_id',
                                          title='Daily MRDT Tests - Last 7 days', x_title='Date', y_title='Number of Patients',
                                          filter_col1='concept_name',filter_value1=['MRDT'],color='Value',legend_title="Legend"
                                          ),
                        className="card-2"
                    ),
                ]
            )
        ]),
        
        # Other Charts Section
        html.Div(
            className="card-container-2",
            children=[
                dcc.Graph(
                    id='daily-malaria-drugs-dispensed',
                    figure=create_pivot_table(df=filtered, index_col1='DrugName',columns_col1='Age_Group',
                                              values_col='ValueN',title='Aggregate Malaria Drugs Dispensed',
                                              filter_col1='Encounter', filter_value1='DISPENSING',
                                              filter_col2='DrugName',
                                              filter_value2=['Lumefantrine + Arthemether 1 x 6','Lumefantrine + Arthemether 2 x 6','Lumefantrine + Arthemether 3 x 6','Lumefantrine + Arthemether 4 x 6',
                                                             'ASAQ 25mg/67.5mg (3 tablets)','ASAQ 50mg/135mg (3 tablets)','ASAQ 100mg/270mg (3 tablets)','ASAQ 100mg/270mg (6 tablets)',
                                                             'SP (1 tablet)','SP (2 tablets)','SP (3 tablets)','SP (525mg tablet)'],
                                              aggfunc='sum'),
                    className="card-2"
                ),
                dcc.Graph(
                    id='daily-malaria-deaths',
                    figure=create_pivot_table(df=filtered, index_col1='Age_Group',columns_col1='Gender',values_col='encounter_id',
                                              title="Aggregate Malaria Demographics", 
                                              filter_col1='Encounter', filter_value1='OUTPATIENT DIAGNOSIS',
                                              filter_col2='obs_value_coded', filter_value2='Malaria',
                                              aggfunc='nunique'
                                              ),
                    className="card-2"
                ),
            ]
        ),
        html.Div([
            html.H2("IDSR",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='notifiable-cases',
                        figure=create_pivot_table(df=filtered, index_col1='obs_value_coded',columns_col1='Age_Group',
                                              values_col='encounter_id',title='Aggregate Notifiable diseases reported at the facility',
                                              filter_col1='Encounter', filter_value1='OUTPATIENT DIAGNOSIS',
                                              filter_col2='obs_value_coded',
                                              filter_value2=['Malaria','COVID-19','Cholera','Measles','Yellow fever','Plague','Rabies'],
                                              aggfunc='nunique'),
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='daily-fever-complaints',
                        figure=create_line_chart(df=data_opd[data_opd['Date']>=str(datetime.now()- pd.Timedelta(days=RELATIVE_DAYS))], date_col='Date', y_col='encounter_id',
                                          title='Daily Fever Symptoms Reported', x_title='Date', y_title='Number of Patients',legend_title="Legend",filter_col1="Encounter",filter_value1="PRESENTING COMPLAINTS",
                                          filter_col2="obs_value_coded",filter_value2="Fever",
                                          ),
                        className="card-2"
                    ),
                ]
            )
        ]),
        
    ])

layout = html.Div(className="container", children=[
    dcc.Location(id='url', refresh=False),
    html.P(
    [
        html.Span("OPD Dashboard", style={"fontWeight": "bold"}),
        ", Last Refreshed: " + str(last_refreshed)
    ],
    style={'textAlign': 'center', 'color': 'gray'}
),
    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Visit Type"),
                dcc.Dropdown(
                    id='visit-type-filter',
                    options=[
                        {'label': item, 'value': item}
                        for item in data['new_revisit'].dropna().unique()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='opd-date-range-picker',
                    min_date_allowed="2024-01-01",
                    max_date_allowed=max_date,
                    initial_visible_month=datetime.now(),
                    start_date=min_date - pd.Timedelta(days=STATIC_DATE_FILTER),
                    # start_date=min_date,
                    end_date=max_date,
                    display_format='YYYY-MM-DD',
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Health Facility"),
                dcc.Dropdown(
                    id='opd-hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in data['Facility'].dropna().unique()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Age Group"),
                dcc.Dropdown(
                    id='opd-age-filter',
                    options=[
                        {'label': age, 'value': age}
                        for age in data['Age_Group'].dropna().unique()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),
        ]),

]),
    html.Div(id='opd-dashboard-container'),        
])

# Callback to update all components based on date range
@callback(
    Output('opd-dashboard-container', 'children'),
    [
        Input('url-params-store', 'data'),
        Input('opd-date-range-picker', 'start_date'),
        Input('opd-date-range-picker', 'end_date'),
        Input('visit-type-filter', 'value'),
        Input('opd-hf-filter', 'value'),
        Input('opd-age-filter', 'value')
    ]
)
def update_dashboard(urlparams, start_date, end_date, visit_type, hf, age):

    path = os.getcwd()
    data_opd = pd.read_csv(f'{path}/data/latest_data_opd.csv', cache_dates=False,dtype={16: str})
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd = data_opd[data_opd['Program']=="OPD Program"]
    print(len(data_opd))

    if urlparams['location']:
        search_url = data[data['Facility_CODE'].str.lower() == urlparams['location'].lower()]
    else:
        search_url = data_opd
        
        
    mask = pd.Series(True, index=data_opd.index)
    if visit_type:
        mask &= (data_opd['new_revisit'] == visit_type)
    if hf:
        mask &= (data_opd['Facility'] == hf)
    if age:
        mask &= (data_opd['Age_Group'] == age)

        
    filtered_data = data_opd[mask].copy()

    filtered_data_date = filtered_data[
        (pd.to_datetime(filtered_data['Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(filtered_data['Date']) <= pd.to_datetime(end_date))
    ]
    
    return build_charts(filtered_data_date, filtered_data)