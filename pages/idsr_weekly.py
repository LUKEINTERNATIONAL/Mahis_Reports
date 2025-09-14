import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import datetime
from isoweek import Week
import os
from visualizations import create_count, create_count_sets

from data_storage import mahis_programs, mahis_facilities, age_groups

dash.register_page(__name__, path="/idsr_weekly")

relative_week = [str(week) for week in range(1, 53)]  # Can extend to 53 if needed
relative_year = [str(year) for year in range(2020, 2051)]

def get_week_start_end(week_num, year):
    """Returns (start_date, end_date) for a given week number and year"""
    # Validate inputs
    if week_num is None or year is None:
        raise ValueError("Week and year must be specified")
    
    try:
        week_num = int(week_num)
        year = int(year)
    except (ValueError, TypeError):
        raise ValueError("Week and year must be integers")
    
    if week_num < 1 or week_num > 53:
        raise ValueError(f"Week must be between 1-53 (got {week_num})")
    
    # Get start (Monday) and end (Sunday) of week
    week = Week(year, week_num)
    start_date = week.monday()    # Monday
    end_date = start_date + datetime.timedelta(days=6)  # Sunday
    
    return start_date, end_date

def build_table(filtered):
    filtered = filtered.replace(np.nan, '')
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
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Adverse Events Following Immunization (AEFI)','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)','Outcome'],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Adverse Events Following Immunization (AEFI)',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("2")), 
             html.Td("Acute Flaccid Paralysis (AFP)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Flaccid Paralysis','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis','Outcome'],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Flaccid Paralysis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("3")), 
             html.Td("Acute Haemorrhagic Fever Syndrome (AHFS)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Acute hemorrahgic fever syndrome','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome','Outcome'],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome','Outcome'],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Acute hemorrahgic fever syndrome',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("4")), 
             html.Td("Anthrax"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Anthrax','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Anthrax','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Anthrax','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Anthrax','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Anthrax','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Anthrax','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Anthrax',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("5")), 
             html.Td("Cholera"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Cholera','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Cholera','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Cholera','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Cholera','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Cholera','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Cholera','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Cholera',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("6")), 
             html.Td("COVID-19"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','COVID-19','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','COVID-19','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','COVID-19','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','COVID-19','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','COVID-19','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','COVID-19','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['COVID-19',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("7")), 
             html.Td("Diarrhoea With Blood (Bacterial)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Diarrhoea With Blood','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Diarrhoea With Blood',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("8")), 
             html.Td("Malaria"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malaria','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malaria','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Malaria','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Malaria','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Malaria','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Malaria','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Malaria',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("9")), 
             html.Td("Maternal Death"), 
             html.Td('', className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Maternal Death','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Maternal Death','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
            
             html.Td('', className="center highlight"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Maternal Death',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Maternal Death',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("10")), 
             html.Td("Measles"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Measles','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Measles','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Measles','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Measles','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Measles','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Measles','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Measles',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("11")), 
             html.Td("Meningococcal Meningitis"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Meningococcal Meningitis','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='Lab test result', unique_column='person_id'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Meningococcal Meningitis',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive', unique_column='person_id'), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("12")), 
             html.Td("Neonatal Tetanus"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Neonatal tetanus','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td('', className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Neonatal tetanus','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Neonatal tetanus','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td('', className="center highlight"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Neonatal tetanus','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Neonatal tetanus',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td('', className="center highlight"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Neonatal tetanus',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("13")), 
             html.Td("Plague"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Plague','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Plague','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Plague','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Plague','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Plague','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Plague','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],filter_col3='concept_name',filter_value3='Died', unique_column='person_id'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5', unique_column='person_id'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5', unique_column='person_id'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='Lab test result'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Plague',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("13")), 
             html.Td("Rabies (Human)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Rabies','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Rabies','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Rabies','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Rabies','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Rabies','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Rabies','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Rabies',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Rabies',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Rabies',''],filter_col3='concept_name',filter_value3='Died'), className="center"), #death outcome not available yet
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),
             html.Td('', className="center highlight"),]),
        html.Tr(
            [html.Td(html.Strong("14")), 
             html.Td("Severe Acute Respiratory Infections (SARI)"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Severe acute respiratory infection','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],filter_col3='concept_name',filter_value3='Died'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='Lab test result'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Severe acute respiratory infection',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("15")), 
             html.Td("Small Pox"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Small pox','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Small pox','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Small pox','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Small pox','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Small pox','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Small pox','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],filter_col3='concept_name',filter_value3='Died'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='Lab test result'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Small pox',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("16")), 
             html.Td("Typhoid Fever"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Typhoid fever','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],filter_col3='concept_name',filter_value3='Died'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Typhoid fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',), className="center"),]),
        html.Tr(
            [html.Td(html.Strong("17")), 
             html.Td("Yellow Fever"), 
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Yellow fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Yellow fever','Encounter','DIAGNOSIS','Age_Group','Over 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','OPD Program','obs_value_coded','Yellow fever','Encounter','DIAGNOSIS'), className="center"),
             
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Yellow fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Yellow fever','Encounter','DIAGNOSIS','Age_Group','Under 5'), className="center"),
             html.Td(create_count(filtered,'encounter_id','Program','IPD Program', 'obs_value_coded','Yellow fever','Encounter','DIAGNOSIS'), className="center"),
            
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Under 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],filter_col3='concept_name',filter_value3='Died',filter_col4='Age_Group',filter_value4='Over 5'), className="center"), #death outcome not available yet
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','PATIENT OUTCOME'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],filter_col3='concept_name',filter_value3='Died'), className="center"), #death outcome not available yet
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Under 5'),  className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result',filter_col4='Age_Group',filter_value4='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='Lab test result'), className="center"),
             
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Under 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',filter_col5='Age_Group',filter_value5='Over 5'), className="center"),
             html.Td(create_count_sets(filtered, filter_col1='Encounter',filter_value1=['DIAGNOSIS','LAB RESULTS'], 
                                       filter_col2='obs_value_coded',filter_value2=['Yellow fever',''],
                                       filter_col3='concept_name',filter_value3='AFP',filter_col4='Value',filter_value4='Positive',), className="center"),]),
        
        ]),

    ])

layout = html.Div(className="container", children=[
    html.H1("WEEKLY DISEASE SURVEILLANCE REPORTING FORM", className="header"),

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
                html.Label("Week"),
                dcc.Dropdown(
                    id='week-filter',
                    options=[
                        {'label': period, 'value': period}
                        for period in relative_week
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

    html.Div(id='idsr-weekly-table-container'),        
])

@callback(
    Output('idsr-weekly-table-container', 'children'),
    Input('url-params-store', 'data'),
    Input('week-filter', 'value'),
    Input('year-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(urlparams, week, year, hf_filter):
    path = os.getcwd()
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')    
        # Validate file exists
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    data_opd = pd.read_parquet(parquet_path)
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')

    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
    else:
        PreventUpdate
    try:
        start_date, end_date = get_week_start_end(week, year)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    filtered = search_url[
        (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]
    filtered = filtered[filtered['Program']=='OPD Program']

    # filtered = data_opd #for debugging

    return build_table(filtered) 

