import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db_services import load_stored_data
from visualizations import create_count, create_sum

dash.register_page(__name__, path="/idsr_monthly")

data = load_stored_data()
min_date = pd.to_datetime(data['Date']).min()
max_date = pd.to_datetime(data['Date']).max()

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
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("2")), 
             html.Td("Food Borne Illness"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("3")), 
             html.Td("HIV (New Positives)"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
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
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
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
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("6")), 
             html.Td("Acute Malnutrition"), 
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight")]),
        html.Tr(
            [html.Td(html.Strong("7")), 
             html.Td("Chronic Malnutrition"), 
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
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
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("9")), 
             html.Td("Sexually Transimitted Infections"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("10")), 
             html.Td("Leprosy"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("11")), 
             html.Td("Underweight Newborns < 2500 g"), 
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("12")), 
             html.Td("Viral Hepatitis"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),]),
        html.Tr(
            [html.Td(html.Strong("13")), 
             html.Td("Dog Bites"), 
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center"),
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
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=max_date,
                    # start_date=max_date - pd.Timedelta(days=1),
                    start_date=min_date,
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

        ]),
        
    ]),

    html.Div(id='idsr-monthly-table-container'),        
])

@callback(
    Output('idsr-monthly-table-container', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hf-filter', 'value')
)
def update_table(start_date, end_date, hf_filter):
    filtered = data[
        (pd.to_datetime(data['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(data['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]

    return build_table(filtered) 

