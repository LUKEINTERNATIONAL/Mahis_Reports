import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_sum

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/malaria_report")


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
    return html.Table(className="data-table", children=[
        html.Thead([
            html.Tr([
                html.Th("", style={"width": "40%"}),
                html.Th("Out Patient Numbers", colSpan=2, className="center")
            ]),
            html.Tr([
                html.Th(""),
                html.Th("<5 Yrs", className="center"),
                html.Th("≥5 Yrs", className="center")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(html.Strong("A: Confirmed (Co) Malaria Cases")),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                     filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria", 
                                     filter_col4="Age_Group", filter_value4="Under 5"), className="center"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                     filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria", 
                                     filter_col4="Age_Group", filter_value4="Over 5"), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("B: Presumed (Pr) Malaria Cases (Clinically Diagnosed)")),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                     filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Under 5"), className="center"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                     filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Over 5"), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("C: Confirmed malaria in pregnant women (c)")),
                html.Td(className="center highlight"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                     filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Over 5"), className="center red")
            ]),
            html.Tr([
                html.Td(html.Strong("D: Presumed (clinically diagnosed) malaria in pregnant women (d)")),
                html.Td(className="center highlight"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                     filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Over 5"), className="center red")
            ]),
            html.Tr([
                html.Td(html.Strong("Total OPD Malaria Cases (A+B+C+D)")),
                html.Td(
                    str(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria", filter_col4="Age_Group", filter_value4="Under 5")) + 
                    int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Under 5"))),
                    className="center"  
                ),
                html.Td(
                    str(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria", filter_col4="Age_Group", filter_value4="Over 5")) + 
                    int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Over 5"))+
                    int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Over 5")) +
                    int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Over 5"))),
                    className="center"
                )
            ]),
            html.Tr([
                html.Td(html.Strong("F: Total OPD Attendance: All causes (Including malaria cases)")),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="REGISTRATION", filter_col4="Age_Group", filter_value4="Under 5"), className="center"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="REGISTRATION", filter_col4="Age_Group", filter_value4="Over 5"), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("G: Confirmed malaria treatment failure (tf)")),
                html.Td(0, className="center"),
                html.Td(0, className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("TREATMENT IN OPD"),className="highlight"),
                html.Td(className="center"),
                html.Td(className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("H: Confirmed cases receiving first-line anti malarial medication (LA)")),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="DISPENSING", 
                                     filter_col4="Age_Group", filter_value4="Under 5", filter_col6='DrugName',filter_value6=['Lumefantrine + Arthemether 1 x 6',
                                                                                                                             'Lumefantrine + Arthemether 2 x 6',
                                                                                                                             'Lumefantrine + Arthemether 3 x 6',
                                                                                                                             'Lumefantrine + Arthemether 4 x 6'])), className="center"),

                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="DISPENSING", 
                                     filter_col4="Age_Group", filter_value4="Over 5", filter_col6='DrugName',filter_value6=['Lumefantrine + Arthemether 1 x 6',
                                                                                                                             'Lumefantrine + Arthemether 2 x 6',
                                                                                                                             'Lumefantrine + Arthemether 3 x 6',
                                                                                                                             'Lumefantrine + Arthemether 4 x 6'])), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("I: Presumed malaria cases receiving first-line anti malarial medication(LA)")),
                html.Td(0, className="center"),
                html.Td(0, className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("J: Confirmed cases receiving second-line anti malarial medication (ASAQ)")),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="DISPENSING", 
                                     filter_col4="Age_Group", filter_value4="Under 5", filter_col6='DrugName',filter_value6=['ASAQ 100mg/270mg (3 tablets)',
                                                                                                                             'ASAQ 100mg/270mg (6 tablets)',
                                                                                                                             'ASAQ 25mg/67.5mg (3 tablets)',
                                                                                                                             'ASAQ 50mg/135mg (3 tablets)'])), className="center"),
                                     
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="DISPENSING", 
                                     filter_col4="Age_Group", filter_value4="Over 5", filter_col6='DrugName',filter_value6=['ASAQ 100mg/270mg (3 tablets)',
                                                                                                                             'ASAQ 100mg/270mg (6 tablets)',
                                                                                                                             'ASAQ 25mg/67.5mg (3 tablets)',
                                                                                                                             'ASAQ 50mg/135mg (3 tablets)'])), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("K: Presumed malaria cases receiving second-line anti malarial medication(ASAQ)")),
                html.Td(0, className="center"),
                html.Td(0, className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("LAB/mRDT IN OPD"),className="highlight"),
                html.Td(className="center"),
                html.Td(className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("L: Suspected malaria cases tested (mRDT)")),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col4="Age_Group", filter_value4="Under 5",), className="center"),
                                     
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col4="Age_Group", filter_value4="Over 5",), className="center"),
            ]),
            html.Tr([
                html.Td(html.Strong("M: Positive malaria cases (mRDT)")),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col3="Value",filter_value3="Positive", filter_col4="Age_Group", filter_value4="Under 5",), className="center"),
                html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col3="Value",filter_value3="Positive", filter_col4="Age_Group", filter_value4="Over 5",), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("N: Suspected malaria cases tested (microscopy)")),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col4="Age_Group", filter_value4="Under 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col4="Age_Group", filter_value4="Under 5",)), className="center"),
                                     
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col4="Age_Group", filter_value4="Over 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col4="Age_Group", filter_value4="Over 5",)), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("O: Positive malaria cases (microscopy)")),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col3="Value",filter_value3="Positive",filter_col4="Age_Group", filter_value4="Under 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col3="Value",filter_value3="Positive",filter_col4="Age_Group", filter_value4="Under 5",)), className="center"),
                                     
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col3="Value",filter_value3="Positive",filter_col4="Age_Group", filter_value4="Over 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col3="Value",filter_value3="Positive",filter_col4="Age_Group", filter_value4="Over 5",)), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong(" Total suspected malaria cases (B+D+L+N)")),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                         filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Under 5"))+
                                         int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",
                                                          filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Under 5"))+
                                                          int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col4="Age_Group", filter_value4="Under 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col4="Age_Group", filter_value4="Under 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col4="Age_Group", filter_value4="Under 5",))
                                     , className="center"),
                html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",filter_value2="Primary diagnosis",
                                         filter_col3="obs_value_coded",filter_value3="Malaria, presumed", filter_col4="Age_Group", filter_value4="Over 5"))+
                                         int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",filter_col2="concept_name",
                                                          filter_value2="Primary diagnosis",filter_col3="obs_value_coded",filter_value3="Malaria in pregnancy", filter_col4="Age_Group", filter_value4="Over 5"))+
                                                          int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="MRDT",filter_col4="Age_Group", filter_value4="Over 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria Species",filter_col4="Age_Group", filter_value4="Over 5",))+
                                     int(create_count(df=filtered, filter_col1="Encounter",filter_value1="LAB RESULTS",
                                     filter_col2="concept_name",filter_value2="Malaria film",filter_col4="Age_Group", filter_value4="Over 5",)), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("COMMODITIES USED"),className="highlight"),
                html.Td(className="center"),
                html.Td(className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("ITEM")),
                html.Td("UNIT OF ISSUE", className="center"),
                html.Td("QUANTITY DISPENSED", className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("LA 1X6 ")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Lumefantrine + Arthemether 1 x 6'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("LA 2X6 ")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered, 'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Lumefantrine + Arthemether 2 x 6'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("LA 3X6 ")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Lumefantrine + Arthemether 3 x 6'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("LA 4X6 ")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Lumefantrine + Arthemether 4 x 6'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("ITN Distributed to Pregnant women")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Insecticide treated net'), className="center red")
            ]),
            html.Tr([
                html.Td(html.Strong("ITN Distributed to Newborn babies")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Insecticide treated net'), className="center red")
            ]),
            html.Tr([
                html.Td(html.Strong("SP")),
                html.Td("tab", className="center"),
                html.Td(int(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','SP (1 tablet)'))+
                        int(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','SP (2 tablets)'))+
                        int(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','SP (3 tablets)'))+
                        int(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','SP (525mg tablet)')), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("RDTs")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','Lumefantrine + Arthemether 1 x 6'), className="center red")
            ]),
            html.Tr([
                html.Td(html.Strong("ASAQ 25mg/67.5mg (3 tablets)")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','ASAQ 25mg/67.5mg (3 tablets)'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("ASAQ 50mg/135mg (3 tablets)")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','ASAQ 50mg/135mg (3 tablets)'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("ASAQ 100mg/270mg (3 tablets)")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','ASAQ 100mg/270mg (3 tablets)'), className="center")
            ]),
            html.Tr([
                html.Td(html.Strong("ASAQ 100mg/270mg (6 tablets)")),
                html.Td("tab", className="center"),
                html.Td(create_sum(filtered,'ValueN', 'Encounter', 'DISPENSING', 'DrugName','ASAQ 100mg/270mg (6 tablets)'), className="center")
            ]),
        ])
    ])

layout = html.Div(className="container", children=[
    html.H1("Malaria Report", className="header"),

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
                        for hf in mahis_facilities()
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

        ]),
        
    ]),

    html.Div(id='malaria-table-container'),        
])

@callback(
    Output('malaria-table-container', 'children'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value'),
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
    filtered = filtered[filtered['Program']=='OPD Program']
    
    return build_table(filtered)

