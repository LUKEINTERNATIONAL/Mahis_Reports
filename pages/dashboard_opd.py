import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import os
from dash.exceptions import PreventUpdate
from db_services import load_stored_data
from visualizations import (create_column_chart, 
                          create_count,
                          create_pie_chart,
                          create_line_chart,
                          create_age_gender_histogram,
                          create_horizontal_bar_chart,
                          create_pivot_table)
from datetime import datetime, timedelta

STATIC_DATE_FILTER = 100

dash.register_page(__name__, path="/dashboard_opd")

# Load data once to get date range
data = load_stored_data()
data = data[data['Program']=="OPD Program"]

min_date = pd.to_datetime(data['Date']).min()
max_date = datetime.today()

path = os.getcwd()
last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]

def build_charts(filtered):
    return html.Div([
        # OPD Attendance Section
        html.Div([
            html.H2("OPD Attendance",style={'textAlign': 'left', 'color': 'gray'}),
            html.Div(
                className="card-container-2",
                children=[
                    dcc.Graph(
                        id='daily-opd-attendance',
                        figure=create_line_chart(df=data[data['Date']>=str(max_date- pd.Timedelta(days=STATIC_DATE_FILTER))], date_col='Date', y_col='encounter_id',
                                          title='Daily OPD Attendance - Last 7 days', x_title='Date', y_title='Number of Patients',legend_title="Legend",filter_col1="Encounter",filter_value1="REGISTRATION",
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
                        figure=create_column_chart(df=data[data['Date']>=str(max_date- pd.Timedelta(days=STATIC_DATE_FILTER))], x_col='Date', y_col='encounter_id',
                                          title='Daily Fever and Malaria Cases - Last 7 days', x_title='Date', y_title='Number of Patients',
                                          filter_col1='obs_value_coded',filter_value1=['Fever','Malaria'],color='obs_value_coded',legend_title="Legend"),
                        className="card-2"
                    ),
                    dcc.Graph(
                        id='daily-lab-fever-tests',
                        figure=create_column_chart(df=data[data['Date']>=str(max_date- pd.Timedelta(days=STATIC_DATE_FILTER))], x_col='Date', y_col='encounter_id',
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
                        figure=create_line_chart(df=data[data['Date']>=str(max_date- pd.Timedelta(days=STATIC_DATE_FILTER))], date_col='Date', y_col='encounter_id',
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
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=max_date,
                    start_date=max_date - pd.Timedelta(days=7),
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
    if urlparams['location']:
        search_url = data[data['Facility_CODE'].str.lower() == urlparams['location'].lower()]
    else:
        search_url = data
        
    filtered_data_date = search_url[
        (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
    ]
        
    mask = pd.Series(True, index=filtered_data_date.index)
    if visit_type:
        mask &= (filtered_data_date['new_revisit'] == visit_type)
    if hf:
        mask &= (filtered_data_date['Facility'] == hf)
    if age:
        mask &= (filtered_data_date['Age_Group'] == age)
        
    filtered_data = filtered_data_date[mask].copy()
    
    return build_charts(filtered_data)