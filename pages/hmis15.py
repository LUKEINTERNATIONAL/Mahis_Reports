import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from db_services import load_stored_data
from visualizations import create_count, create_sum

dash.register_page(__name__, path="/hmis15")

data = load_stored_data()
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
                html.Th("CODE"),
                html.Th("DATA ELEMENT", className="center"),
                html.Th("VALUE", className="center")
            ]),
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Maternal Services", colSpan=2, className="center highlight")
            ]),
        ]),
    html.Tbody([
        # Maternal Services
        html.Tr([html.Td(html.Strong("39")), html.Td("Number of pregnant women starting antenatal care during their first trimester"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("40")), html.Td("Total number of new antenatal attendees"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("40")), html.Td("Total antenatal visits"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("41")), html.Td("Number of deliveries attended by skilled health personnel"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("42")), html.Td("Number of women obstetric complications treated at obstetric care facility"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("43")), html.Td("Number of caesarean sections"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("44")), html.Td("Total number of live births"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("44")), html.Td("Number of babies born with weight less than 2500g"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("45")), html.Td("Number of abortion complications treated"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("46")), html.Td("Number of eclampsia cases treated"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("47")), html.Td("Number of postpartum haemorrhage (PPH) cases treated"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("48")), html.Td("Number of sepsis cases treated"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("49")), html.Td("Number of pregnant women treated for severe anaemia"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("51")), html.Td("Number of newborn treated for complications"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("52")), html.Td("Number of postpartum care within 2 weeks of delivery"), html.Td("", className="center")]),]),
    
    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Family Planning", colSpan=2, className="center highlight")
            ]),
        ]),
    html.Tbody([
        # Family Planning
        html.Tr([html.Td(html.Strong("53a")), html.Td("Number of persons receiving 3 months supply of condoms"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("53b")), html.Td("Number of persons receiving 3 months of oral pills"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("53c")), html.Td("Number of persons receiving Depo-Provera"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("53d")), html.Td("Number of persons receiving Norplant"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("53e")), html.Td("Number of persons receiving IUCD"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("53f")), html.Td("Number of persons receiving sterilisation method of FP"), html.Td("", className="center")]),]),
    
    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Child Health", colSpan=2, className="center highlight")
            ]),
        ]),
    html.Tbody([  
        # Child Health
        html.Tr([html.Td(html.Strong("55")), html.Td("Number of fully immunised under 1 children"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("56")), html.Td("Number of under 1 children given BCG"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("56")), html.Td("Number of under 1 children given pentavalent - III"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("56")), html.Td("Number of under 1 children given polio - III"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("56")), html.Td("Number of under 1 children given measles 1st doses at 9M"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("57")), html.Td("Number of Vitamin A doses given to 6 - 59 M population"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("62")), html.Td("Number of under-weight in under fives attending clinic"), html.Td("", className="center")]),]),
    
    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Attendance", colSpan=2, className="center highlight")
            ]),
        ]),        
    html.Tbody([
        # Attendance
        html.Tr([html.Td(html.Strong("30")), html.Td("Num of 15 - 49 years receiving volunteer & confidential testing and serostatus"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("31")), html.Td("Number of 15 - 49 age group tested HIV positive"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("32")), html.Td("Number of HIV positive persons receiving ARV treatment"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("34")), html.Td("Number of pregnant women receiving VCT and serostatus results"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("35")), html.Td("Number of pregnant women tested HIV positive"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("36")), html.Td("Number of HIV positive women treated for PMTCT"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("62")), html.Td("Total number of children attending under-five clinic"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("108")), html.Td("Number of OPD attendance"), html.Td(create_count(df=filtered, filter_col1="Encounter",filter_value1="REGISTRATION"), className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Tuberculosis", colSpan=2, className="center highlight")
            ]),
        ]),   
    html.Tbody([
        # Tuberculosis
        html.Tr([html.Td(html.Strong("65")), html.Td("Number of confirmed TB new cases"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("66")), html.Td("Num of smear negative and extra-pulmonary cases completed treatment"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("67")), html.Td("Num of new smear sputum positive cases proved smear-ve at the end of treatment"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Supplies", colSpan=2, className="center highlight")
            ]),
        ]),
    html.Tbody([
        html.Tr([html.Td(html.Strong("23")), html.Td("Was there any stock outs of SP for more than a week at a time?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("23")), html.Td("Was there any stock outs of ORS for more than a week at a time?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("23")), html.Td("Was there any stock outs of contrimaxazole for more than a week at a time?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("23")), html.Td("Was there any stock outs of SP, ORS and Contrimaxazole for more than a week?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("24")), html.Td("Number of functioning ambulances"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("76")), html.Td("Number of insecticide treated nets distributed"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Community Health Activities", colSpan=2, className="center highlight")
            ]),
        ]),   
    html.Tbody([
        # Community Health Activities
        html.Tr([html.Td(html.Strong("25")), html.Td("Number of households with access to safe drinking water"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("26")), html.Td("Number of households with atleast a sanplat latrine"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("38")), html.Td("Num of HBC patients follow-up and provided treatment"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Physical Facilities", colSpan=2, className="center highlight")
            ]),
        ]),         
    html.Tbody([
        # Physical Facilities
        html.Tr([html.Td(html.Strong("17")), html.Td("Do you have functioning water supply systems?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("17")), html.Td("Do you have functioning Communication systems?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("17")), html.Td("Do you have functioning Electricity?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("17")), html.Td("Do you have functioning water supply,Electricity and Communication systems?"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Management and Supervision", colSpan=2, className="center highlight")
            ]),
        ]),     
    html.Tbody([
        # Management and Supervision
        html.Tr([html.Td(html.Strong("13")), html.Td("Is the health center committee functional?"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("15")), html.Td("Were you supervised by DHMT members using the integrated supervision checklist?"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("New Cases (OPD plus inpatient)", colSpan=2, className="center highlight")
            ]),
        ]),      
    html.Tbody([
        # New Cases (OPD plus inpatient)
        html.Tr([html.Td(html.Strong("27")), html.Td("Sexually transmitted infections-new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="STI")), className="center")]),
        html.Tr([html.Td(html.Strong("29")), html.Td("Syphilis in pregnancy"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Syphilis in pregnancy")), className="center")]),
        html.Tr([html.Td(html.Strong("31")), html.Td("HIV confirmed positive (15-49 years) new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="HIV")), className="center")]),
        html.Tr([html.Td(html.Strong("37")), html.Td("Opportunistic infection - new cases"), html.Td("0", className="center")]),
        html.Tr([html.Td(html.Strong("58")), html.Td("Acute respiratory infections - new cases (U5)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Acute respiratory infection"))+
                                                                                                        int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Severe acute respiratory infection")), className="center")]),
        html.Tr([html.Td(html.Strong("60")), html.Td("Diarrhoea non-bloody -new cases (under5)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Diarrhea")), className="center")]),
        html.Tr([html.Td(html.Strong("64")), html.Td("Malnutrition - new case (under 5)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Malnutrition")), className="center")]),
        html.Tr([html.Td(html.Strong("69")), html.Td("Malaria - new cases (under 5)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Malaria", filter_col4="Age_Group", filter_value4="Under 5")), className="center")]),
        html.Tr([html.Td(html.Strong("70")), html.Td("Malaria - new cases (5 & over)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Malaria", filter_col4="Age_Group", filter_value4="Over 5")), className="center")]),
        html.Tr([html.Td(html.Strong("78")), html.Td("Neonatal tetanus - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Neonatal Tetanus")), className="center")]),
        html.Tr([html.Td(html.Strong("79")), html.Td("Cholera - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Cholera")), className="center")]),
        html.Tr([html.Td(html.Strong("81")), html.Td("Measles - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Measles")), className="center")]),
        html.Tr([html.Td(html.Strong("82")), html.Td("Acute Flaccid paralysis -confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Acute Flaccid paralysis")), className="center")]),
        html.Tr([html.Td(html.Strong("83")), html.Td("Ebola - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Ebola")), className="center")]),
        html.Tr([html.Td(html.Strong("84")), html.Td("Meningococal meningitis - confimed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Meningococcal meningitis")), className="center")]),
        html.Tr([html.Td(html.Strong("85")), html.Td("Plague - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Plague")), className="center")]),
        html.Tr([html.Td(html.Strong("86")), html.Td("Rabies - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Rabies")), className="center")]),
        html.Tr([html.Td(html.Strong("87")), html.Td("Yellow fever - confirmed new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Yellow Fever")), className="center")]),
        html.Tr([html.Td(html.Strong("88")), html.Td("Dysentery - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Dysentery")), className="center")]),
        html.Tr([html.Td(html.Strong("90")), html.Td("Eye infections - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Eye infection")), className="center")]),
        html.Tr([html.Td(html.Strong("91")), html.Td("Ear infections - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Ear infection nos")), className="center")]),
        html.Tr([html.Td(html.Strong("92")), html.Td("Skin infections - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Skin infections")), className="center")]),
        html.Tr([html.Td(html.Strong("93")), html.Td("Oral conditions"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Ulcer, oral"))+
                                                                                                        int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Other oral conditions"))+
                                                                                                        int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Tumours or Oral cancers"))+
                                                                                                        int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Other and unspecified lesions of oral mucosa")), className="center")]),
        html.Tr([html.Td(html.Strong("94")), html.Td("Schistosomiasis - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Schistosomiasis")), className="center")]),
        html.Tr([html.Td(html.Strong("95")), html.Td("Leprosy - new cases"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Leprosy")), className="center")]),
        html.Tr([html.Td(html.Strong("96")), html.Td("Common injuries and wounds (except RTA)"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Head injury"))+
                                                                                                        int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Soft tissue injury")), className="center")]),
        html.Tr([html.Td(html.Strong("98")), html.Td("Number of road traffic accidents"), html.Td(int(create_count(df=filtered, filter_col1="Encounter",filter_value1="OUTPATIENT DIAGNOSIS",
                                                                                                        filter_col2="concept_name",filter_value2="Primary diagnosis",
                                                                                                        filter_col3="obs_value_coded",filter_value3="Road Traffic Accidents,")), className="center")]),]),
        
    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Admissions", colSpan=2, className="center highlight")
            ]),
        ]),
    html.Tbody([
        # Admissions
        html.Tr([html.Td(html.Strong("20a")), html.Td("Bed capacity"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("20b")), html.Td("Total number of admissions (including maternity)"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("20c")), html.Td("Total number of discharges"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("20d")), html.Td("Total inpatient days"), html.Td("", className="center")]),]),

    html.Thead([
            html.Tr([
                html.Th("", style={"width": "10%"}),
                html.Th("Inpatient Deaths (Including Maternity)", colSpan=2, className="center highlight")
            ]),
        ]),       
    html.Tbody([
        # Inpatient Deaths (Including Maternity)
        html.Tr([html.Td(html.Strong("102")), html.Td("Total number of inpatient deaths from all causes (excluding maternity)"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("50")), html.Td("Number of direct obstetric deaths in facility"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("59")), html.Td("Acute respiratory infections - inpatient deaths (U5)"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("61")), html.Td("Diarrhoea non-bloody (under 5) - inpatient deaths"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("64")), html.Td("Malnutrition - inpatient deaths (under 5)"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("68")), html.Td("TB - inpatient deaths"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("69")), html.Td("Malaria - inpatient deaths under 5"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("74")), html.Td("Malaria - inpatient deaths (5 & over)"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("80")), html.Td("Cholera - inpatients deaths"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("89")), html.Td("Dysentery- inpatients deaths"), html.Td("", className="center")]),
        html.Tr([html.Td(html.Strong("98")), html.Td("No. of road traffic accidents - inpatient deaths"), html.Td("", className="center")]),]),

    ])

layout = html.Div(className="container", children=[
    html.H1("HMIS 15", className="header"),

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

    html.Div(id='hmis-table-container'),        
])

@callback(
    Output('hmis-table-container', 'children'),
    Input('year-filter', 'value'),
    Input('month-filter', 'value'),
    Input('hf-filter', 'value')
)
def update_table(year_filter, month_filter, hf_filter):
    try:
        start_date, end_date = get_month_start_end(month_filter, year_filter)
    except ValueError as e:
        return html.Div(f"{str(e)}")  # Show error in Dash UI
    
    filtered = data[
        (pd.to_datetime(data['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(data['Date']) <= pd.to_datetime(end_date))
    ]
    if hf_filter:
        filtered = filtered[filtered['Facility'] == hf_filter]
    
    return build_table(filtered)

