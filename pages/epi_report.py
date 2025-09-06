import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import os
from visualizations import create_count, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/epi_report")

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
    return html.Table(
        html.Div([
            html.H4("Target Population", style={'backgroundColor': '#006401', 'padding': '5px','color':'white',"width": "50%"}),

            dash_table.DataTable(
                columns=[
                    {"name": "Indicator", "id": "indicator"},
                    {"name": "Value", "id": "value"}
                ],
                data=[
                    {"indicator": "Annual Population", "value": ""},
                    {"indicator": "Live Births", "value": ""},
                    {"indicator": "Surviving Infants", "value": ""},
                    {"indicator": "Pregnant Women", "value": ""},
                    {"indicator": "9 Years Old Girls", "value": ""}
                ],
                style_table={"width": "50%"},
                style_header={
                    "backgroundColor": "rgb(206, 206, 204)",
                    "fontWeight": "bold",
                    "textAlign": "center"
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "5px",
                    "border": "1px solid rgba(77, 75, 75, 0.521)"
                },
                style_data_conditional=[
                    {
                        'if': {'column_id': 'value'},
                        'textAlign': 'center'
                    }
                ]
            ),
            html.H4("A. Immunisation Sessions", style={'backgroundColor': '#006401', 'padding': '5px','color':'white'}),
            dash_table.DataTable(
                columns=[
                    {"name": "Indicator", "id": "session_type"},
                    {"name": "Number", "id": "number"},
                    {"name": "%", "id": "percent"},
                    {"name": "Reasons for cancellation", "id": "cancellation_reasons"}
                ],
                data=[
                    {"session_type": "Planned immunization sessions (Static)", "number": "", "percent": "", "cancellation_reasons": ""},
                    {"session_type": "Canceled immunization sessions (Static)", "number": "", "percent": "", "cancellation_reasons": ""},
                    {"session_type": "Planned immunization sessions (Outreach)", "number": "", "percent": "", "cancellation_reasons": ""},
                    {"session_type": "Canceled immunization sessions (Outreach)", "number": "", "percent": "", "cancellation_reasons": ""}
                ],
                style_table={"width": "60%"},
                style_header={
                    "backgroundColor": "rgb(206, 206, 204)",
                    "fontWeight": "bold",
                    "textAlign": "center"
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "5px",
                    "border": "1px solid rgba(77, 75, 75, 0.521)"
                },
                style_data_conditional=[
                    {
                        'if': {'column_id': ['number', 'percent']},
                        'textAlign': 'center'
                    },
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(214, 214, 211)'
                    }
                ]
            ),
            html.H4("B. Vaccinations", style={'backgroundColor': '#006401', 'padding': '5px','color':'white',"width": "100%"}),
            # BCG, OPV0 Section
            html.Div([
                html.H5("T1", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly Target/ Live Births"], "id": "monthly_target_lb"},

                        # BCG group
                        {"name": ["BCG", "Static"], "id": "bcg_static"},
                        {"name": ["BCG", "O/reach"], "id": "bcg_outreach"},
                        {"name": ["BCG", "Total"], "id": "bcg_total"},
                        {"name": ["BCG", "Cov"], "id": "bcg_cov"},

                        # OPV 0 group
                        {"name": ["OPV 0", "Static"], "id": "opv_static"},
                        {"name": ["OPV 0", "O/reach"], "id": "opv_outreach"},
                        {"name": ["OPV 0", "Total"], "id": "opv_total"},
                        {"name": ["OPV 0", "Cov"], "id": "opv_cov"},

                        {"name": ["", "Monthly Target Surviving Infants"], "id": "monthly_target_si"},

                        # MR1 group
                        {"name": ["MR1", "Static"], "id": "mr1_static"},
                        {"name": ["MR1", "O/reach"], "id": "mr1_outreach"},
                        {"name": ["MR1", "Total"], "id": "mr1_total"},
                        {"name": ["MR1", "Cov"], "id": "mr1_cov"},

                        # TCV group
                        {"name": ["TCV", "Static"], "id": "tcv_static"},
                        {"name": ["TCV", "Outreach"], "id": "tcv_outreach"},
                        {"name": ["TCV", "Total"], "id": "tcv_total"},

                        {"name": ["", "Monthly Target Surviving Infants"], "id": "monthly_target_si2"},

                        # MR2 group
                        {"name": ["MR2", "Static"], "id": "mr2_static"},
                        {"name": ["MR2", "O/reach"], "id": "mr2_outreach"},
                        {"name": ["MR2", "Total"], "id": "mr2_total"},
                        {"name": ["MR2", "Cov"], "id": "mr2_cov"},

                        {"name": ["", "Dropout Rate"], "id": "dropout_rate"},
                    ],
                    data = [
                        {"age": "Under 1", "monthly_target_lb": "", "bcg_static": "", "bcg_outreach": "", "bcg_total": "", "bcg_cov": ""},
                        {"age": "Over 1", "monthly_target_lb": "", "bcg_static": "", "bcg_outreach": "", "bcg_total": "", "bcg_cov": ""},
                        {"age": "Total", "monthly_target_lb": "", "bcg_static": "", "bcg_outreach": "", "bcg_total": "", "bcg_cov": ""},
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),
            
            # MR1 Vaccinations Section
            html.Div([
                html.H5("T2", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly Target Surviving Infants"], "id": "monthly_target_si"},

                        # OPV1 group
                        {"name": ["OPV1", "Static"], "id": "opv1_static"},
                        {"name": ["OPV1", "O/reach"], "id": "opv1_outreach"},
                        {"name": ["OPV1", "Total"], "id": "opv1_total"},

                        # OPV2 group
                        {"name": ["OPV2", "Static"], "id": "opv2_static"},
                        {"name": ["OPV2", "O/reach"], "id": "opv2_outreach"},
                        {"name": ["OPV2", "Total"], "id": "opv2_total"},

                        # OPV3 group
                        {"name": ["OPV3", "Static"], "id": "opv3_static"},
                        {"name": ["OPV3", "O/reach"], "id": "opv3_outreach"},
                        {"name": ["OPV3", "Total"], "id": "opv3_total"},
                        {"name": ["OPV3", "Cov"], "id": "opv3_cov"},

                        {"name": ["", "Dropout rate"], "id": "dropout_rate"},

                        # IPV1 group
                        {"name": ["IPV1", "Static"], "id": "ipv1_static"},
                        {"name": ["IPV1", "O/reach"], "id": "ipv1_outreach"},
                        {"name": ["IPV1", "Total"], "id": "ipv1_total"},

                        # IPV2 group
                        {"name": ["IPV2", "Static"], "id": "ipv2_static"},
                        {"name": ["IPV2", "Outreach"], "id": "ipv2_outreach"},
                        {"name": ["IPV2", "Total"], "id": "ipv2_total"},
                        {"name": ["IPV2", "Cov"], "id": "ipv2_cov"},
                        {"name": ["IPV2", "Dropout rate"], "id": "ipv2_dropout_rate"},
                    ],
                    data = [
                        {"id": "under1", "age": "Under 1", "monthly_target_si": "", "opv1_static": "", "opv1_outreach": "", "opv1_total": "", "opv2_static": "", "opv2_outreach": "", "opv2_total": "", "opv3_static": "", "opv3_outreach": "", "opv3_total": "", "opv3_cov": "", "dropout_rate": "", "ipv1_static": "", "ipv1_outreach": "", "ipv1_total": "", "ipv2_static": "", "ipv2_outreach": "", "ipv2_total": "", "ipv2_cov": "", "ipv2_dropout_rate": ""},
                        {"id": "over1", "age": "Over 1", "monthly_target_si": "", "opv1_static": "", "opv1_outreach": "", "opv1_total": "", "opv2_static": "", "opv2_outreach": "", "opv2_total": "", "opv3_static": "", "opv3_outreach": "", "opv3_total": "", "opv3_cov": "", "dropout_rate": "", "ipv1_static": "", "ipv1_outreach": "", "ipv1_total": "", "ipv2_static": "", "ipv2_outreach": "", "ipv2_total": "", "ipv2_cov": "", "ipv2_dropout_rate": ""},
                        {"id": "total", "age": "Total", "monthly_target_si": "", "opv1_static": "", "opv1_outreach": "", "opv1_total": "", "opv2_static": "", "opv2_outreach": "", "opv2_total": "", "opv3_static": "", "opv3_outreach": "", "opv3_total": "", "opv3_cov": "", "dropout_rate": "", "ipv1_static": "", "ipv1_outreach": "", "ipv1_total": "", "ipv2_static": "", "ipv2_outreach": "", "ipv2_total": "", "ipv2_cov": "", "ipv2_dropout_rate": ""}
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T3", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly Target Surviving Infants"], "id": "monthly_target_si"},

                        # DPT-HepB-Hib1 group
                        {"name": ["DPT-HepB-Hib1", "Static"], "id": "dpt1_static"},
                        {"name": ["DPT-HepB-Hib1", "O/reach"], "id": "dpt1_outreach"},
                        {"name": ["DPT-HepB-Hib1", "Total"], "id": "dpt1_total"},

                        # DPT-HepB-Hib2 group
                        {"name": ["DPT-HepB-Hib2", "Static"], "id": "dpt2_static"},
                        {"name": ["DPT-HepB-Hib2", "O/reach"], "id": "dpt2_outreach"},
                        {"name": ["DPT-HepB-Hib2", "Total"], "id": "dpt2_total"},

                        # DPT-HepB-Hib3 group
                        {"name": ["DPT-HepB-Hib3", "Static"], "id": "dpt3_static"},
                        {"name": ["DPT-HepB-Hib3", "O/reach"], "id": "dpt3_outreach"},
                        {"name": ["DPT-HepB-Hib3", "Total"], "id": "dpt3_total"},
                        {"name": ["DPT-HepB-Hib3", "cov"], "id": "dpt3_cov"},

                        {"name": ["", "Dropout rate"], "id": "dropout_rate"},
                    ],

                    # Example flattened data
                    data = [
                        {
                            "age": "Under 1",
                            "monthly_target_si": "",
                            "dpt1_static": "", "dpt1_outreach": "", "dpt1_total": "",
                            "dpt2_static": "", "dpt2_outreach": "", "dpt2_total": "",
                            "dpt3_static": "", "dpt3_outreach": "", "dpt3_total": "", "dpt3_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Over 1",
                            "monthly_target_si": "",
                            "dpt1_static": "", "dpt1_outreach": "", "dpt1_total": "",
                            "dpt2_static": "", "dpt2_outreach": "", "dpt2_total": "",
                            "dpt3_static": "", "dpt3_outreach": "", "dpt3_total": "", "dpt3_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Total",
                            "monthly_target_si": "",
                            "dpt1_static": "", "dpt1_outreach": "", "dpt1_total": "",
                            "dpt2_static": "", "dpt2_outreach": "", "dpt2_total": "",
                            "dpt3_static": "", "dpt3_outreach": "", "dpt3_total": "", "dpt3_cov": "",
                            "dropout_rate": ""
                        }
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.H5("T4", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly Target Surviving Infants"], "id": "monthly_target_si"},

                        # PCV1 group
                        {"name": ["PCV1", "Static"], "id": "pcv1_static"},
                        {"name": ["PCV1", "O/reach"], "id": "pcv1_outreach"},
                        {"name": ["PCV1", "Total"], "id": "pcv1_total"},

                        # PCV2 group
                        {"name": ["PCV2", "Static"], "id": "pcv2_static"},
                        {"name": ["PCV2", "O/reach"], "id": "pcv2_outreach"},
                        {"name": ["PCV2", "Total"], "id": "pcv2_total"},

                        # PCV3 group
                        {"name": ["PCV3", "Static"], "id": "pcv3_static"},
                        {"name": ["PCV3", "O/reach"], "id": "pcv3_outreach"},
                        {"name": ["PCV3", "Total"], "id": "pcv3_total"},
                        {"name": ["PCV3", "cov"], "id": "pcv3_cov"},

                        {"name": ["", "Dropout rate"], "id": "dropout_rate"},
                    ],

                    # Example flattened data
                    data = [
                        {
                            "age": "Under 1",
                            "monthly_target_si": "",
                            "pcv1_static": "", "pcv1_outreach": "", "pcv1_total": "",
                            "pcv2_static": "", "pcv2_outreach": "", "pcv2_total": "",
                            "pcv3_static": "", "pcv3_outreach": "", "pcv3_total": "", "pcv3_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Over 1",
                            "monthly_target_si": "",
                            "pcv1_static": "", "pcv1_outreach": "", "pcv1_total": "",
                            "pcv2_static": "", "pcv2_outreach": "", "pcv2_total": "",
                            "pcv3_static": "", "pcv3_outreach": "", "pcv3_total": "", "pcv3_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Total",
                            "monthly_target_si": "",
                            "pcv1_static": "", "pcv1_outreach": "", "pcv1_total": "",
                            "pcv2_static": "", "pcv2_outreach": "", "pcv2_total": "",
                            "pcv3_static": "", "pcv3_outreach": "", "pcv3_total": "", "pcv3_cov": "",
                            "dropout_rate": ""
                        }
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T5", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly Target"], "id": "monthly_target"},

                        # ROTA 1 group
                        {"name": ["ROTA 1", "Static"], "id": "rota1_static"},
                        {"name": ["ROTA 1", "O/reach"], "id": "rota1_outreach"},
                        {"name": ["ROTA 1", "Total"], "id": "rota1_total"},

                        # ROTA 2 group
                        {"name": ["ROTA 2", "Static"], "id": "rota2_static"},
                        {"name": ["ROTA 2", "O/reach"], "id": "rota2_outreach"},
                        {"name": ["ROTA 2", "Total"], "id": "rota2_total"},
                        {"name": ["ROTA 2", "Cov"], "id": "rota2_cov"},

                        {"name": ["", "Dropout rate"], "id": "dropout_rate"},
                    ],

                    # Example flattened data
                    data = [
                        {
                            "age": "Under 1",
                            "monthly_target": "",
                            "rota1_static": "", "rota1_outreach": "", "rota1_total": "",
                            "rota2_static": "", "rota2_outreach": "", "rota2_total": "", "rota2_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Total",
                            "monthly_target": "",
                            "rota1_static": "", "rota1_outreach": "", "rota1_total": "",
                            "rota2_static": "", "rota2_outreach": "", "rota2_total": "", "rota2_cov": "",
                            "dropout_rate": ""
                        }
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T6", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Age"], "id": "age"},
                        {"name": ["", "Monthly target"], "id": "monthly_target"},

                        # Malaria Vaccine 1 group
                        {"name": ["Malaria Vaccine 1", "Static"], "id": "mv1_static"},
                        {"name": ["Malaria Vaccine 1", "O/Reach"], "id": "mv1_outreach"},
                        {"name": ["Malaria Vaccine 1", "Total"], "id": "mv1_total"},

                        # Malaria Vaccine 2 group
                        {"name": ["Malaria Vaccine 2", "Static"], "id": "mv2_static"},
                        {"name": ["Malaria Vaccine 2", "O/Reach"], "id": "mv2_outreach"},
                        {"name": ["Malaria Vaccine 2", "Total"], "id": "mv2_total"},

                        # Malaria Vaccine 3 group
                        {"name": ["Malaria Vaccine 3", "Static"], "id": "mv3_static"},
                        {"name": ["Malaria Vaccine 3", "O/Reach"], "id": "mv3_outreach"},
                        {"name": ["Malaria Vaccine 3", "Total"], "id": "mv3_total"},
                        {"name": ["Malaria Vaccine 3", "Cov"], "id": "mv3_cov"},

                        # Malaria Vaccine 4 group
                        {"name": ["Malaria Vaccine 4", "Static"], "id": "mv4_static"},
                        {"name": ["Malaria Vaccine 4", "O/Reach"], "id": "mv4_outreach"},
                        {"name": ["Malaria Vaccine 4", "Total"], "id": "mv4_total"},
                        {"name": ["Malaria Vaccine 4", "Cov"], "id": "mv4_cov"},

                        {"name": ["", "Dropout Rate"], "id": "dropout_rate"},
                    ],

                    # Example flattened data
                    data = [
                        {
                            "age": "Under 1",
                            "monthly_target": "",
                            "mv1_static": "", "mv1_outreach": "", "mv1_total": "",
                            "mv2_static": "", "mv2_outreach": "", "mv2_total": "",
                            "mv3_static": "", "mv3_outreach": "", "mv3_total": "", "mv3_cov": "",
                            "mv4_static": "", "mv4_outreach": "", "mv4_total": "", "mv4_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "22 - 36 months",
                            "monthly_target": "",
                            "mv1_static": "", "mv1_outreach": "", "mv1_total": "",
                            "mv2_static": "", "mv2_outreach": "", "mv2_total": "",
                            "mv3_static": "", "mv3_outreach": "", "mv3_total": "", "mv3_cov": "",
                            "mv4_static": "", "mv4_outreach": "", "mv4_total": "", "mv4_cov": "",
                            "dropout_rate": ""
                        },
                        {
                            "age": "Total",
                            "monthly_target": "",
                            "mv1_static": "", "mv1_outreach": "", "mv1_total": "",
                            "mv2_static": "", "mv2_outreach": "", "mv2_total": "",
                            "mv3_static": "", "mv3_outreach": "", "mv3_total": "", "mv3_cov": "",
                            "mv4_static": "", "mv4_outreach": "", "mv4_total": "", "mv4_cov": "",
                            "dropout_rate": ""
                        },
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T7", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        # Left table: Number children protected at birth
                        {"name": ["Number children protected at birth", "Age"], "id": "nc_age"},
                        {"name": ["Number children protected at birth", "Monthly Target"], "id": "nc_monthly_target"},
                        {"name": ["Number children protected at birth", "Static"], "id": "nc_static"},
                        {"name": ["Number children protected at birth", "O/reach"], "id": "nc_outreach"},
                        {"name": ["Number children protected at birth", "Total"], "id": "nc_total"},
                        {"name": ["Number children protected at birth", "Cov"], "id": "nc_cov"},

                        # Right table: HPV
                        {"name": ["HPV", "Age"], "id": "hpv_age"},
                        {"name": ["HPV", "Monthly Target"], "id": "hpv_monthly_target"},

                        # HPV 1 group
                        {"name": ["HPV 1", "Static"], "id": "hpv1_static"},
                        {"name": ["HPV 1", "Out Reach"], "id": "hpv1_outreach"},
                        {"name": ["HPV 1", "School"], "id": "hpv1_school"},
                        {"name": ["HPV 1", "Total"], "id": "hpv1_total"},
                        {"name": ["HPV 1", "Cov"], "id": "hpv1_cov"},

                        # HPV 2 group
                        {"name": ["HPV 2", "Static"], "id": "hpv2_static"},
                        {"name": ["HPV 2", "Out Reach"], "id": "hpv2_outreach"},
                        {"name": ["HPV 2", "School"], "id": "hpv2_school"},
                        {"name": ["HPV 2", "Total"], "id": "hpv2_total"},
                        {"name": ["HPV 2", "Cov"], "id": "hpv2_cov"},

                        {"name": ["HPV", "Drop Out Rate"], "id": "hpv_dropout_rate"},
                    ],

                    # Example flattened data
                data = [
                    {
                        # Left table
                        "nc_age": "Under 1",
                        "nc_monthly_target": "",
                        "nc_static": "",
                        "nc_outreach": "",
                        "nc_total": "",
                        "nc_cov": "",

                        # Right table
                        "hpv_age": "9 Yrs girls",
                        "hpv_monthly_target": "",
                        "hpv1_static": "", "hpv1_outreach": "", "hpv1_school": "", "hpv1_total": "", "hpv1_cov": "",
                        "hpv2_static": "", "hpv2_outreach": "", "hpv2_school": "", "hpv2_total": "", "hpv2_cov": "",
                        "hpv_dropout_rate": ""
                    },
                    {
                        # Left table
                        "nc_age": "Total",
                        "nc_monthly_target": "",
                        "nc_static": "",
                        "nc_outreach": "",
                        "nc_total": "",
                        "nc_cov": "",

                        # Right table
                        "hpv_age": "Total",
                        "hpv_monthly_target": "",
                        "hpv1_static": "", "hpv1_outreach": "", "hpv1_school": "", "hpv1_total": "", "hpv1_cov": "",
                        "hpv2_static": "", "hpv2_outreach": "", "hpv2_school": "", "hpv2_total": "", "hpv2_cov": "",
                        "hpv_dropout_rate": ""
                    },
                ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.H4("C. Fully Immunized", style={'backgroundColor': '#006401', 'padding': '5px','color':'white',"width": "100%"}),
            dash_table.DataTable(
                columns = [
                    {"name": ["", "Td"], "id": "td"},
                    
                    # Td for pregnant women
                    {"name": ["Td for pregnant women", "Monthly Target"], "id": "preg_monthly_target"},
                    {"name": ["Td for pregnant women", "Static"], "id": "preg_static"},
                    {"name": ["Td for pregnant women", "O/reach"], "id": "preg_outreach"},
                    {"name": ["Td for pregnant women", "Total"], "id": "preg_total"},
                    {"name": ["Td for pregnant women", "Cov"], "id": "preg_cov"},
                    
                    # Td for non-pregnant women
                    {"name": ["Td for non-pregnant women", "Monthly Target"], "id": "nonpreg_monthly_target"},
                    {"name": ["Td for non-pregnant women", "Static"], "id": "nonpreg_static"},
                    {"name": ["Td for non-pregnant women", "O/reach"], "id": "nonpreg_outreach"},
                    {"name": ["Td for non-pregnant women", "Total"], "id": "nonpreg_total"},
                    {"name": ["Td for non-pregnant women", "Cov"], "id": "nonpreg_cov"},
                    
                    # Td for women of child bearing age (CBA)
                    {"name": ["Td for CBA women", "Monthly Target"], "id": "cba_monthly_target"},
                    {"name": ["Td for CBA women", "Static"], "id": "cba_static"},
                    {"name": ["Td for CBA women", "O/reach"], "id": "cba_outreach"},
                    {"name": ["Td for CBA women", "Total"], "id": "cba_total"},
                    {"name": ["Td for CBA women", "Cov"], "id": "cba_cov"},
                ],
                data = [
                    {
                        "td": "Td1",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Td2",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Td3",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Td4",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Td5",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Total doses",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                    {
                        "td": "Td2+",
                        "preg_monthly_target": "", "preg_static": "", "preg_outreach": "", "preg_total": "", "preg_cov": "",
                        "nonpreg_monthly_target": "", "nonpreg_static": "", "nonpreg_outreach": "", "nonpreg_total": "", "nonpreg_cov": "",
                        "cba_monthly_target": "", "cba_static": "", "cba_outreach": "", "cba_total": "", "cba_cov": "",
                    },
                ],
                style_table={"width": "100%"},
                style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                style_data_conditional=[
                    {
                        'if': {'row_index': 1},
                        'backgroundColor': 'rgb(214, 214, 211)'
                    }
                ]
            ),
            html.H4("D. Vaccine Wastage", style={'backgroundColor': '#006401', 'padding': '5px','color':'white',"width": "100%"}),
            html.Div([
                html.H5("T1", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Strategy"], "id": "strategy"},
                        
                        # BCG
                        {"name": ["BCG", "Doses Used and Wasted (A)"], "id": "bcg_a"},
                        {"name": ["BCG", "Number of children vaccinated (B)"], "id": "bcg_b"},
                        {"name": ["BCG", "Vaccine wasted (A-B)"], "id": "bcg_wasted"},
                        {"name": ["BCG", "Wastage rate (A-B)/A*100"], "id": "bcg_wastage_rate"},
                        
                        # OPV
                        {"name": ["OPV", "Doses Used and Wasted (A)"], "id": "opv_a"},
                        {"name": ["OPV", "Number of children vaccinated (B)"], "id": "opv_b"},
                        {"name": ["OPV", "Vaccine wasted (A-B)"], "id": "opv_wasted"},
                        {"name": ["OPV", "Wastage rate (A-B)/A*100"], "id": "opv_wastage_rate"},
                        
                        # MR
                        {"name": ["MR", "Doses Used and Wasted (A)"], "id": "mr_a"},
                        {"name": ["MR", "Number of children vaccinated (B)"], "id": "mr_b"},
                        {"name": ["MR", "Vaccine wasted (A-B)"], "id": "mr_wasted"},
                        {"name": ["MR", "Wastage rate (A-B)/A*100"], "id": "mr_wastage_rate"},
                    ],

                    # Example flattened data
                data = [
                        {
                            "strategy": "Static",
                            "bcg_a": "", "bcg_b": "", "bcg_wasted": "", "bcg_wastage_rate": "",
                            "opv_a": "", "opv_b": "", "opv_wasted": "", "opv_wastage_rate": "",
                            "mr_a": "", "mr_b": "", "mr_wasted": "", "mr_wastage_rate": "",
                        },
                        {
                            "strategy": "Outreach",
                            "bcg_a": "", "bcg_b": "", "bcg_wasted": "", "bcg_wastage_rate": "",
                            "opv_a": "", "opv_b": "", "opv_wasted": "", "opv_wastage_rate": "",
                            "mr_a": "", "mr_b": "", "mr_wasted": "", "mr_wastage_rate": "",
                        },
                        {
                            "strategy": "Total",
                            "bcg_a": "", "bcg_b": "", "bcg_wasted": "", "bcg_wastage_rate": "",
                            "opv_a": "", "opv_b": "", "opv_wasted": "", "opv_wastage_rate": "",
                            "mr_a": "", "mr_b": "", "mr_wasted": "", "mr_wastage_rate": "",
                        },
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T2", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                        {"name": ["", "Strategy"], "id": "strategy"},
                        
                        # DPT-HepB-Hib
                        {"name": ["DPT-HepB-Hib", "Doses Used (A)"], "id": "dpt_a"},
                        {"name": ["DPT-HepB-Hib", "Doses Discarded (B)"], "id": "dpt_b"},
                        {"name": ["DPT-HepB-Hib", "Total (A+B)"], "id": "dpt_total"},
                        {"name": ["DPT-HepB-Hib", "Wastage rate"], "id": "dpt_wastage_rate"},
                        
                        # PCV
                        {"name": ["PCV", "Doses Used (A)"], "id": "pcv_a"},
                        {"name": ["PCV", "Doses Discarded (B)"], "id": "pcv_b"},
                        {"name": ["PCV", "Total (A+B)"], "id": "pcv_total"},
                        {"name": ["PCV", "Wastage rate"], "id": "pcv_wastage_rate"},
                        
                        # ROTA
                        {"name": ["ROTA", "Doses Used (A)"], "id": "rota_a"},
                        {"name": ["ROTA", "Doses Discarded (B)"], "id": "rota_b"},
                        {"name": ["ROTA", "Total (A+B)"], "id": "rota_total"},
                        {"name": ["ROTA", "Wastage rate"], "id": "rota_wastage_rate"},
                        
                        # Malaria Vaccine
                        {"name": ["Malaria Vaccine", "Doses Used (A)"], "id": "malaria_a"},
                        {"name": ["Malaria Vaccine", "Doses Discarded (B)"], "id": "malaria_b"},
                        {"name": ["Malaria Vaccine", "Total (A+B)"], "id": "malaria_total"},
                        {"name": ["Malaria Vaccine", "Wastage rate"], "id": "malaria_wastage_rate"},
                    ],

                    # Example flattened data
                data = [
                    {
                        "strategy": "Static",
                        "dpt_a": "", "dpt_b": "", "dpt_total": "", "dpt_wastage_rate": "",
                        "pcv_a": "", "pcv_b": "", "pcv_total": "", "pcv_wastage_rate": "",
                        "rota_a": "", "rota_b": "", "rota_total": "", "rota_wastage_rate": "",
                        "malaria_a": "", "malaria_b": "", "malaria_total": "", "malaria_wastage_rate": "",
                    },
                    {
                        "strategy": "Outreach",
                        "dpt_a": "", "dpt_b": "", "dpt_total": "", "dpt_wastage_rate": "",
                        "pcv_a": "", "pcv_b": "", "pcv_total": "", "pcv_wastage_rate": "",
                        "rota_a": "", "rota_b": "", "rota_total": "", "rota_wastage_rate": "",
                        "malaria_a": "", "malaria_b": "", "malaria_total": "", "malaria_wastage_rate": "",
                    },
                    {
                        "strategy": "Total",
                        "dpt_a": "", "dpt_b": "", "dpt_total": "", "dpt_wastage_rate": "",
                        "pcv_a": "", "pcv_b": "", "pcv_total": "", "pcv_wastage_rate": "",
                        "rota_a": "", "rota_b": "", "rota_total": "", "rota_wastage_rate": "",
                        "malaria_a": "", "malaria_b": "", "malaria_total": "", "malaria_wastage_rate": "",
                    },
                ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H5("T1", style={'backgroundColor': 'rgb(206, 206, 204)', 'padding': '5px', 'textAlign': 'center'}),
                dash_table.DataTable(
                    columns = [
                            {"name": ["", "Strategy"], "id": "strategy"},
                            
                            # Td
                            {"name": ["Td", "Doses Used"], "id": "td_used"},
                            {"name": ["Td", "Doses Discarded"], "id": "td_discarded"},
                            {"name": ["Td", "Total"], "id": "td_total"},
                            {"name": ["Td", "Wastage rate"], "id": "td_wastage"},
                            
                            # HPV
                            {"name": ["HPV", "Doses Used"], "id": "hpv_used"},
                            {"name": ["HPV", "Doses Discarded"], "id": "hpv_discarded"},
                            {"name": ["HPV", "Total"], "id": "hpv_total"},
                            {"name": ["HPV", "Wastage"], "id": "hpv_wastage"},
                        ],

                    # Example flattened data
                data = [
                        {
                            "strategy": "Static",
                            "td_used": "", "td_discarded": "", "td_total": "", "td_wastage": "",
                            "hpv_used": "", "hpv_discarded": "", "hpv_total": "", "hpv_wastage": "",
                        },
                        {
                            "strategy": "Outreach",
                            "td_used": "", "td_discarded": "", "td_total": "", "td_wastage": "",
                            "hpv_used": "", "hpv_discarded": "", "hpv_total": "", "hpv_wastage": "",
                        },
                        {
                            "strategy": "Total",
                            "td_used": "", "td_discarded": "", "td_total": "", "td_wastage": "",
                            "hpv_used": "", "hpv_discarded": "", "hpv_total": "", "hpv_wastage": "",
                        },
                    ],
                    style_table={"width": "100%", "overflowX": "auto"},
                    style_header={
                        "backgroundColor": "rgb(206, 206, 204)",
                        "whiteSpace": "normal",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "fontSize": "12px"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "5px",
                        "border": "1px solid rgba(77, 75, 75, 0.521)",
                        "minWidth": "40px",
                        "height": "30px"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 1},
                            'backgroundColor': 'rgb(214, 214, 211)'
                        },
                        {
                            'if': {'row_index': 2},
                            'fontWeight': 'bold'
                        }
                    ],
                    merge_duplicate_headers=True
                )
            ], style={'marginBottom': '20px'}),

        html.H4("To be completed. VitA supplementation, AEFI etc")
        ])
    )

layout = html.Div(className="container", children=[
    html.H1("MONTHLY ELECTRONIC IMMUZATION REPORT", className="header"),

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
                    value="June",
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

    html.Div(id='epi-table-container'),        
])


@callback(
    Output('epi-table-container', 'children'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value')
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
    
    return build_table(filtered)