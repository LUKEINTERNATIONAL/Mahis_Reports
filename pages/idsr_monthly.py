import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from dash.exceptions import PreventUpdate
from visualizations import create_count, create_sum, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/idsr_monthly")


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
    underweight = filtered[(filtered['Age']==0)&(filtered['concept_name']=='Weight')&(filtered['ValueN']<2.5)][['person_id']]
    underweight = filtered.merge(underweight, on = 'person_id', how='inner')


    list_of_sti = [
                    'Syphilis', 
                   'Syphilis RPR/VDRL',
                   'Syphilis with genital ulcers',
                   'Syphilis in pregnancy',
                   'Gonorrhea',
                   'Chancroid',
                   'Chlamydia',
                   'Vaginitis'
                   ]
    return html.Table(className="data-table", children=[
    html.Thead([
        html.Tr([
            html.Th("ID", rowSpan=3),
            html.Th("Diseases/Events/Conditions", rowSpan=3),
            html.Th("Out-Patient Cases", colSpan=3),
            html.Th("In-Patient Cases", colSpan=3),
            html.Th("In-Patient Deaths", colSpan=3),
            html.Th("Laboratory Findings", colSpan=6)
        ]),
        html.Tr([
            # Out-Patient Cases subheaders
            html.Th(""),
            html.Th(""),
            html.Th(""),
            
            # In-Patient Cases subheaders
            html.Th(""),
            html.Th(""),
            html.Th(""),
            
            # In-Patient Deaths subheaders
            html.Th(""),
            html.Th(""),
            html.Th(""),
            
            # Laboratory Findings subheaders
            html.Th("No. of Tested Cases", colSpan=2),
            html.Th("No. of Positive Cases", colSpan=2),
            html.Th("Total", colSpan=2)
        ]),
        html.Tr([
            # Empty cell for disease name column
            
            # Out-Patient Cases (repeated for alignment)
            html.Th("<5yrs"),
            html.Th("≥5yrs"),
            html.Th("Total"),
            
            # In-Patient Cases (repeated for alignment)
            html.Th("<5yrs"),
            html.Th("≥5yrs"),
            html.Th("Total"),
            
            # In-Patient Deaths (repeated for alignment)
            html.Th("<5yrs"),
            html.Th("≥5yrs"),
            html.Th("Total"),
            
            # Laboratory Findings detailed subheaders
            html.Th("<5yrs"),
            html.Th("≥5yrs"),
            html.Th("<5yrs"),
            html.Th("≥5yrs"),
            html.Th("<5yrs"),
            html.Th("≥5yrs")
        ])
    ]),
    html.Tbody([
        # Maternal Services
        html.Tr(
            [html.Td(html.Strong("1")), 
             html.Td("Diarrhea"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhea','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhea','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Diarrhea','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Diarrhea','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(0, className="center"),
             html.Td("", className="center highlight"),
             html.Td(0, className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("2")), 
             html.Td("Food Borne Illness"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("3")), 
             html.Td("HIV (New Positives)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','iPD Program','obs_value_coded','HIV','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("4")), 
             html.Td("Injuries (Road Traffic Accidents)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("5")), 
             html.Td("Malaria In Pregnancy"), 
             html.Td("", className="center highlight"),
             html.Td(create_count_sets(df=filtered, filter_col1="Encounter",filter_value1=["PREGNANCY STATUS","DIAGNOSIS"],filter_col2="obs_value_coded",filter_value2=["Yes","Malaria"],
                                     filter_col3="Age_Group", filter_value3="Over 5", filter_col4='Program',filter_value4='OPD Program', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(df=filtered, filter_col1="Encounter",filter_value1=["PREGNANCY STATUS","DIAGNOSIS"],filter_col2="obs_value_coded",filter_value2=["Yes","Malaria"],
                                     filter_col3="Age_Group", filter_value3="Over 5", filter_col4='Program',filter_value4='OPD Program', unique_column='person_id'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count_sets(df=filtered, filter_col1="Encounter",filter_value1=["PREGNANCY STATUS","DIAGNOSIS"],filter_col2="obs_value_coded",filter_value2=["Yes","Malaria"],
                                     filter_col3="Age_Group", filter_value3="Over 5", filter_col4='Program',filter_value4='IPD Program', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(df=filtered, filter_col1="Encounter",filter_value1=["PREGNANCY STATUS","DIAGNOSIS"],filter_col2="obs_value_coded",filter_value2=["Yes","Malaria"],
                                     filter_col3="Age_Group", filter_value3="Over 5", filter_col4='Program',filter_value4='IPD Program', unique_column='person_id'), className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("6")), 
             html.Td("Malnutrition"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight")]),
        html.Tr(
            [html.Td(html.Strong("7")), 
             html.Td("Chronic Malnutrition"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Chronic Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Chronic Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Chronic Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Chronic Malnutrition','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("8")), 
             html.Td("Perinatal Deaths"), 
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("9")), 
             html.Td("Sexually Transimitted Infections"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',list_of_sti,'Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("10")), 
             html.Td("Leprosy"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','iPD Program','obs_value_coded','Leprosy','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("11")), 
             html.Td("Underweight Newborns < 2500 g"), 
             html.Td(create_count(underweight,'encounter_id','Program','OPD Program','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(underweight,'encounter_id','Program','OPD Program','Age_Group','Under 5'), className="center"),
             html.Td(create_count(underweight,'encounter_id','Program','IPD Program','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(underweight,'encounter_id','Program','IPD Program','Age_Group','Under 5'), className="center"),
             html.Td(create_count(underweight,'encounter_id','Program','IPD Program','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(underweight,'encounter_id','Program','IPD Program','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("12")), 
             html.Td("Viral Hepatitis"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("13")), 
             html.Td("Dog Bites"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS'],'Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter',['DIAGNOSIS','OUTPATIENT DIAGNOSIS']), className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
    ]),

    ])

layout = html.Div(className="container", children=[
    html.H1("MONTHLY DISEASE SURVEILLANCE REPORTING FORM", className="header"),

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

    html.Div(id='idsr-monthly-table-container'),        
])


@callback(
    Output('idsr-monthly-table-container', 'children'),
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
        # print(search_url['Facility_CODE'].unique())
    else:
        PreventUpdate
    try:
        start_date, end_date = get_month_start_end(month_filter, year_filter)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    filtered = search_url
    [
        (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]

    # filtered = data_opd #for debugging
    
    return build_table(filtered)

