import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import os
from dash.exceptions import PreventUpdate
from visualizations import (create_column_chart, 
                          create_count,
                          create_pie_chart,
                          create_line_chart,
                          create_age_gender_histogram,
                          create_horizontal_bar_chart)
from datetime import datetime, timedelta

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/home")

STATIC_DATE_FILTER = 0
RELATIVE_DAYS=7

min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
max_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

timeStamp_path = os.path.join(os.getcwd(), 'data', 'TimeStamp.csv')
last_refreshed = pd.read_csv(timeStamp_path)['saving_time'].to_list()[0]

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    # html.H1("MaHIS Dashboard", style={'textAlign': 'center', 'marginTop': '40px'}, className="header"),
    # html.P("This page displays the visualizations relating to MaHIS OPD, EIR and NCD", style={'textAlign': 'center', 'color': 'gray'}),
    html.P(id='last-refreshed-display', style={'textAlign': 'center', 'color': 'gray'}),
    # html.Div with children that are filters starting with Date Range picker and a filter for program
    html.Div([
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Program"),
                dcc.Dropdown(
                    id='program-filter',
                    options=[
                        {'label': prog, 'value': prog}
                        for prog in mahis_programs()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    min_date_allowed="2023-01-01",
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
                    id='hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in []
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
                        for age in age_groups()
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
                    className="card-2"
                )
            ),
            html.Div(
                dcc.Graph(
                    id='patients-by-date',
                    className="card-2"
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
                    className="card-2"
                )
            ),
            html.Div(
                dcc.Graph(
                    id='patients-statistics-village',
                    className="card-2"
                )
            )
        ]
    ),
    dcc.Interval(id='interval-update-today',interval=10*60*1000, n_intervals=0)  # every 10 minutes

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
     Output('hf-filter', 'options'),
     ],
    [
        Input('url-params-store', 'data'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('program-filter', 'value'),
        Input('hf-filter', 'value'),
        Input('age-filter', 'value')
     ],
     prevent_initial_call=True
)
def update_dashboard(urlparams, start_date, end_date, program, hf, age):
    start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59, microsecond=0)
    delta_days = (end_date - start_date).days
    delta_days = 7 if delta_days <=0 else delta_days
    
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')  
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd['Gender'] = data_opd['Gender'].replace({"M":"Male","F":"Female"})


    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
    else:
        PreventUpdate
        
    # search_url = data_opd    
    mask = pd.Series(True, index=search_url.index)
    if program:
        mask &= (search_url['Program'] == program)
    if hf:
        mask &= (search_url['Facility'] == hf)
    if age:
        mask &= (search_url['Age_Group'] == age)

    filtered_data_no_date = search_url.loc[mask].copy()

    mask &= (
        (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
    )

    filtered_data = search_url.loc[mask].copy()
        
        # Update counts
    total_count = create_count(filtered_data,'encounter_id')
    male_count = create_count(filtered_data,'encounter_id', 'Gender', 'Male')
    female_count = create_count(filtered_data,'encounter_id', 'Gender', 'Female')
    over5_count = create_count(filtered_data,'encounter_id', 'Age_Group', 'Over 5')
    under5_count = create_count(filtered_data,'encounter_id', 'Age_Group', 'Under 5')
        
        # Update charts
    enrollments_fig = create_column_chart(df=filtered_data, x_col='Program', y_col='encounter_id',
                                        title='Enrollment by Program', x_title='Program Name', y_title='Number of Patients')
        
    daily_visits_fig = create_line_chart(df=filtered_data_no_date[filtered_data_no_date['Date']>=min_date- pd.Timedelta(days=delta_days)], date_col='Date', y_col='encounter_id',
                                            title='Daily Patient Visits - Last 7 days', x_title='Date', y_title='Number of Patients')
        
    visit_type_fig = create_pie_chart(df=filtered_data, names_col='new_revisit', values_col='encounter_id',
                                        title='Patient Visit Type',colormap={
                                                                        'New': "#292D79",
                                                                        'Revisit': "#FE1AD0"
                                                                    }
                        )
        
    age_dist_fig = create_age_gender_histogram(df=filtered_data, age_col='Age', gender_col='Gender',
                                                title='Age Distribution', xtitle='Age', ytitle='Number of patients', bin_size=5)
        
    return (total_count, male_count, female_count, over5_count, under5_count,
                enrollments_fig,
                daily_visits_fig, 
                visit_type_fig, age_dist_fig, filtered_data['Facility'].sort_values().unique().tolist()
                )

@callback(
    Output('last-refreshed-display', 'children'),
    Input('url', 'pathname')
)
def update_last_refreshed_on_page_load(pathname):
    path = os.getcwd()
    last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]
    return f"Last Refreshed: {str(last_refreshed)}"

@callback(
    [Output('date-range-picker', 'start_date'),
     Output('date-range-picker', 'end_date')],
    Input('interval-update-today', 'n_intervals')
)
def update_date_range(n):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end