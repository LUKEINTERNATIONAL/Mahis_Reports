import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from db_services import load_stored_data
from visualizations import (create_column_chart, 
                          create_count,
                          create_pie_chart,
                          create_line_chart,
                          create_age_gender_histogram,
                          create_horizontal_bar_chart)
from datetime import datetime, timedelta

dash.register_page(__name__, path="/home")

# Load data once to get date range
data = load_stored_data()
min_date = pd.to_datetime(data['Date']).min()
max_date = pd.to_datetime(data['Date']).max()
max_date = datetime.today()

def load_menu(filtered):

    
    return 

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1("MaHIS Dashboard", style={'textAlign': 'center', 'marginTop': '40px'}, className="header"),
    html.P("This page displays the visualizations relating to MaHIS OPD, EIR and NCD", style={'textAlign': 'center', 'color': 'gray'}),
    
    # html.Div with children that are filters starting with Date Range picker and a filter for program
    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Program"),
                dcc.Dropdown(
                    id='program-filter',
                    options=[
                        {'label': prog, 'value': prog}
                        for prog in data['Program'].dropna().unique()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='date-range-picker',
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
                    id='hf-filter',
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
                    id='age-filter',
                    options=[
                        {'label': age, 'value': age}
                        for age in data['Age_Group'].dropna().unique()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),
        ]),


    
    # html.Hr(),  # optional line separator

    # cards and content below...
]),
        
    
    html.Div(
        className="card-container-5",
        children=[
            html.Div(
                html.Div([
                    html.H2(id='total-patients-count', className="metric-value"),
                    html.H4("Total Registered Patients", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(id='male-patients-count', className="metric-value"),
                    html.H4("Total Registered - Male", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(id='female-patients-count', className="metric-value"),
                    html.H4("Total Registered - Female", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(id='over5-patients-count', className="metric-value"),
                    html.H4("Total Registered - Over 5", className="metric-title"),
                ], className="card")
            ),
            html.Div(
                html.Div([
                    html.H2(id='under5-patients-count', className="metric-value"),
                    html.H4("Total Registered - Under 5", className="metric-title"),
                ], className="card")
            ),
        ],
    ),
    
    html.Div(
        className="card-container-2",
        children=[
            html.Div(
                dcc.Graph(
                    id='program-enrollments',
                    className="card"
                )
            ),
            html.Div(
                dcc.Graph(
                    id='patients-by-date',
                    className="card"
                )
            )
        ]
    ),
    
    html.Div(
        className="card-container-2",
        children=[
            html.Div(
                dcc.Graph(
                    id='patients-statistics-visit-type',
                    className="card"
                )
            ),
            html.Div(
                dcc.Graph(
                    id='patients-statistics-village',
                    className="card"
                )
            )
        ]
    ),
    
    html.Div(
        className="card-container-2",
        children=[
            html.Div(
                dcc.Graph(
                    id='patients-statistics-prescomplaint',
                    className="card"
                )
            ),
            html.Div(
                dcc.Graph(
                    id='patients-statistics-diagnoses',
                    className="card"
                )
            )
        ]
    ),
])

# Callback to update all components based on date range
@callback(
    [Output('total-patients-count', 'children'),
     Output('male-patients-count', 'children'),
     Output('female-patients-count', 'children'),
     Output('over5-patients-count', 'children'),
     Output('under5-patients-count', 'children'),
     Output('program-enrollments', 'figure'),
     Output('patients-by-date', 'figure'),
     Output('patients-statistics-visit-type', 'figure'),
     Output('patients-statistics-village', 'figure'),
     Output('patients-statistics-prescomplaint', 'figure'),
     Output('patients-statistics-diagnoses', 'figure')],
    [
        Input('url-params-store', 'data'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('program-filter', 'value'),
        Input('hf-filter', 'value'),
        Input('age-filter', 'value')
     ]
)
def update_dashboard(urlparams, start_date, end_date, program, hf, age):
    # if urlparams['location'] == None:
    #     raise PreventUpdate
    # if urlparams['location'] is None:
    #     html.Div("No URL parameters found", style={'color': 'red'})
    # search_url = data[data['Facility_CODE'].str.lower() == new_flag]
    # print(len(search_url))

    if urlparams['location']:
        print(urlparams['location'])
        print(urlparams)
        search_url = data[data['Facility_CODE'].str.lower() == urlparams['location'].lower()]
    else:
        search_url = data
    # search_url = data
    filtered_data_date = search_url[(pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) & 
                            (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))]
        
    mask = pd.Series(True, index=filtered_data_date.index)
    if program:
        mask &= (filtered_data_date['Program'] == program)
    if hf:
        mask &= (filtered_data_date['Facility'] == hf)
    if age:
        mask &= (filtered_data_date['Age_Group'] == age)
    filtered_data = filtered_data_date[mask].copy()
    print(len(filtered_data))


        
        # Update counts
    total_count = create_count(filtered_data,'encounter_id', 'Encounter', 'REGISTRATION')
    male_count = create_count(filtered_data,'encounter_id', 'Gender', 'M', 'Encounter', 'REGISTRATION')
    female_count = create_count(filtered_data,'encounter_id', 'Gender', 'F', 'Encounter', 'REGISTRATION')
    over5_count = create_count(filtered_data,'encounter_id', 'Age_Group', 'Over 5', 'Encounter', 'REGISTRATION')
    under5_count = create_count(filtered_data,'encounter_id', 'Age_Group', 'Under 5', 'Encounter', 'REGISTRATION')
        
        # Update charts
    enrollments_fig = create_column_chart(df=filtered_data, x_col='Program', y_col='person_id',
                                        title='Program', x_title='Program Name', y_title='Number of Patients')
        
    daily_visits_fig = create_line_chart(df=filtered_data, date_col='Date', y_col='person_id',
                                            title='Daily Patient Visits', x_title='Date', y_title='Number of Patients')
        
    visit_type_fig = create_pie_chart(df=filtered_data, names_col='new_revisit', values_col='person_id',
                                        title='Patient Visit Type')
        
    age_dist_fig = create_age_gender_histogram(df=filtered_data, age_col='Age', gender_col='Gender',
                                                title='Age Distribution', xtitle='Age', ytitle='Number of patients', bin_size=5)
        
    complaints_fig = create_horizontal_bar_chart(df=filtered_data, label_col='obs_value_coded', value_col='person_id',
                                                title='Top 10 Presenting Complaints', x_title='Number of Patients', y_title='Presenting Complaint',
                                                filter_col1='Encounter', filter_value1='PRESENTING COMPLAINTS', filter_col2='concept_name', filter_value2='Presenting complaint')
        
    diagnoses_fig = create_horizontal_bar_chart(df=filtered_data, label_col='obs_value_coded', value_col='person_id',
                                                title='Top 10 Primary Diagnoses', x_title='Number of Patients', y_title='Presenting Complaint',
                                                filter_col1='Encounter', filter_value1='OUTPATIENT DIAGNOSIS', filter_col2='concept_name', filter_value2='Primary diagnosis')
        
    return (total_count, male_count, female_count, over5_count, under5_count,
                enrollments_fig,
                daily_visits_fig, 
                visit_type_fig, age_dist_fig,
                complaints_fig, diagnoses_fig)