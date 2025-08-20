import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_sum

dash.register_page(__name__, path="/idsr_monthly")

path = os.getcwd()
data = pd.read_csv(f'{path}/data/latest_data_opd.csv',dtype={16: str})
min_date = pd.to_datetime(data['Date']).min()
max_date = pd.to_datetime(data['Date']).max()

relative_month = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December',]
relative_year = [str(year) for year in range(max_date.year, min_date.year - 1, -1)]

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
             html.Td("Diarrhoea (Severe, With Dehydration)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhoea (Severe, With Dehydration)','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhoea (Severe, With Dehydration)','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Diarrhoea (Severe, With Dehydration)','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Diarrhoea (Severe, With Dehydration)','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Foodborne illness','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','iPD Program','obs_value_coded','HIV','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Road Traffic Accidents','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malaria in pregnancy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malaria in pregnancy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Malaria in pregnancy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Malaria in pregnancy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
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
             html.Td("Acute Malnutrition"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Acute Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Acute Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Acute Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Acute Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Chronic Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Chronic Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Chronic Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td("", className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Chronic Malnutrition','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded',['list of STIs'],'Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','iPD Program','obs_value_coded','Leprosy','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
             html.Td("0", className="center"),
             html.Td("", className="center highlight"),
             html.Td("0", className="center"),
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
            [html.Td(html.Strong("12")), 
             html.Td("Viral Hepatitis"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Viral Hepatitis','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program','obs_value_coded','Bite, dog','Encounter','OUTPATIENT DIAGNOSIS'), className="center"),
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
                    value=None,
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
                        for hf in data['Facility'].dropna().unique()
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
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(year_filter, month_filter, hf_filter):
    try:
        start_date, end_date = get_month_start_end(month_filter, year_filter)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    path = os.getcwd()
    data_opd = pd.read_csv(f'{path}/data/latest_data_opd.csv', cache_dates=False,dtype={16: str})
    
    filtered = data_opd[
        (pd.to_datetime(data_opd['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(data_opd['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]
    
    return build_table(filtered)

