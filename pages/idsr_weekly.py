import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db_services import load_stored_data
from visualizations import create_count, create_sum

dash.register_page(__name__, path="/idsr_weekly")

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
             html.Td("Adverse Events Following Immunization (AEFI)"), 
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
            [html.Td(html.Strong("2")), 
             html.Td("Acute Flaccid Paralysis (AFP)"), 
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
             html.Td("Acute Haemorrhagic Fever Syndrome (AHFS)"), 
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
            [html.Td(html.Strong("4")), 
             html.Td("Anthrax"), 
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
            [html.Td(html.Strong("5")), 
             html.Td("Cholera"), 
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
            [html.Td(html.Strong("6")), 
             html.Td("Covid-19"), 
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
            [html.Td(html.Strong("7")), 
             html.Td("Diarrhoea With Blood (Bacterial)"), 
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
            [html.Td(html.Strong("8")), 
             html.Td("Malaria"), 
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
            [html.Td(html.Strong("9")), 
             html.Td("Maternal Death"), 
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center"),
             html.Td("", className="center"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),
             html.Td("", className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("10")), 
             html.Td("Measles"), 
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
             html.Td("Meningococcal Meningitis"), 
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
            [html.Td(html.Strong("12")), 
             html.Td("Neonatal Tetanus"), 
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
            [html.Td(html.Strong("13")), 
             html.Td("Plague"), 
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
             html.Td("Rabies (Human)"), 
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
            [html.Td(html.Strong("14")), 
             html.Td("	Severe Acute Respiratory Infections (SARI)"), 
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
            [html.Td(html.Strong("15")), 
             html.Td("Small Pox"), 
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
            [html.Td(html.Strong("16")), 
             html.Td("Typhoid Fever"), 
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
            [html.Td(html.Strong("17")), 
             html.Td("Yellow Fever"), 
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
        
        ]),

    ])

layout = html.Div(className="container", children=[
    html.H1("WEEKLY DISEASE SURVEILLANCE REPORTING FORM", className="header"),

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

    html.Div(id='idsr-weekly-table-container'),        
])

@callback(
    Output('idsr-weekly-table-container', 'children'),
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

