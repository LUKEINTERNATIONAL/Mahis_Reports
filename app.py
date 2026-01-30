import dash
from dash import html, dcc, page_container, page_registry, Output, Input, State, callback
import os
import json
import datetime
from datetime import datetime as dt
from isoweek import Week
from reports_class import ReportTableBuilder
import urllib.parse
import plotly.express as px
import pandas as pd
from flask import request, jsonify
from dash.exceptions import PreventUpdate
from config import PREFIX_NAME
import os

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css']

# print(list(load_stored_data())) # Load the data to ensure it's available
# Initialize the Dash app
# pathname_prefix = '/reports/' # Adjust this if your app is served from a subpath
pathname_prefix = PREFIX_NAME if PREFIX_NAME else '/'
app = dash.Dash(
                __name__,
                use_pages=True,
                suppress_callback_exceptions=True,
                requests_pathname_prefix=pathname_prefix
                )
server = app.server

# Define the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='url-params-store', storage_type='session'),
    html.Nav([
        dcc.Store(id='nav-store', data={}),
        html.Ul([
            html.Li(html.A("Dashboard", href=f"{pathname_prefix}home", className="nav-link",id="home-link")),
            html.Li(html.A("HMIS DataSet Reports", href=f"{pathname_prefix}hmis_reports", className="nav-link",id="hmis-reports-link")),
            html.Li(html.A("Program Reports", href=f"{pathname_prefix}program_reports", className="nav-link",id="programs-link")),
            html.Li(html.A("Configure Reports", href="#", className="nav-link",id="admin-link",
                          style={'visibility': 'hidden', 'pointer-events': 'none', 'cursor': 'default'}),
                 style={'visibility': 'hidden'}),
            html.Div("Last updated: Today", style={"color":"grey","font-size":"0.9rem","margin-top":"5px","font-style":"italic"}, id='last_updated')
        ], className="nav-list")
    ], className="navbar"),
    page_container,
    
], style={ 'margin': '20px', 'fontFamily': 'Arial, sans-serif'})
@callback(
    Output('url-params-store', 'data'),
    Input('url', 'href')
)
def store_url_params(href):
    if not href:
        raise PreventUpdate
    parsed_url = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed_url.query)
    
    # location = location_param.get('Location', [None])[0]
    return params

@app.callback(
    Output('url', 'pathname'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def redirect_to_home(pathname):
    if pathname == "/":
        return "/home"
    return pathname

@app.callback(
    [Output('home-link', 'href'),
     Output('hmis-reports-link', 'href'),
     Output('programs-link', 'href'),
     Output('admin-link', 'href'),
     Output('last_updated','children')
    ],
    Input('url-params-store', 'data')
)
def update_nav_links(url_params):
    location = url_params.get('Location', [None])[0] if url_params else None
    uuid = url_params.get('uuid', [None])[0] if url_params else None
    query = f"?Location={location}&uuid={uuid}" if location and uuid else f"?Location={location}" if location else f"?uuid={uuid}" if uuid else ""
    path = os.getcwd()
    json_path = os.path.join(path, 'data','TimeStamp.csv')
    last_updated = pd.read_csv(json_path)['saving_time'].to_list()[0]

    return (
        f"{pathname_prefix}home{query}",
        f"{pathname_prefix}hmis_reports{query}",
        f"{pathname_prefix}program_reports{query}",
        f"{pathname_prefix}reports_config{query}",
        f"Last updated on: {last_updated}"
    )


# Helper functions for date ranges (replicated from pages/reports.py)
relative_month = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December']
relative_quarter = ["Q1Jan-Mar", "Q2Apr-June", "Q3Jul-Sep", "Q4Oct-Dec"]

def get_week_start_end(week_num, year):
    week = Week(int(year), int(week_num))
    start_date = week.monday()
    end_date = start_date + datetime.timedelta(days=6)
    return start_date, end_date

def get_month_start_end(month, year):
    month_index = relative_month.index(month) + 1
    start_date = datetime.date(int(year), month_index, 1)
    if month_index == 12:
        end_date = datetime.date(int(year) + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(int(year), month_index + 1, 1) - datetime.timedelta(days=1)
    return start_date, end_date

def get_quarter_start_end(quarter, year):
    quarter_map = {
        "Q1Jan-Mar": (1, 3), "Q2Apr-June": (4, 6), "Q3Jul-Sep": (7, 9), "Q4Oct-Dec": (10, 12)
    }
    start_month, end_month = quarter_map[quarter]
    start_date = datetime.date(int(year), start_month, 1)
    if end_month == 12:
        end_date = datetime.date(int(year), 12, 31)
    else:
        end_date = datetime.date(int(year), end_month + 1, 1) - datetime.timedelta(days=1)
    return start_date, end_date

@server.route(f'/api/', methods=['GET'])
# this /api/route should return the following in json: /api/datasets, /api/reports, /api/indicators
def api_root():
    uuid_param = request.args.get('uuid')
    # allow certain uuids only
    allowed_uuids = ["m3his@dhd"]  # Example list of allowed UUIDs
    if uuid_param not in allowed_uuids:
        return jsonify({"error": "Unauthorized, Please supply id"}), 403
    else:
        return jsonify({
            "endpoints": {
                "datasets": "/api/datasets",
                "reports": "/api/reports",
                "indicators": "/api/indicators",
                "data_elements": "/api/dataElements"
            }
        })
    
@server.route(f'/api/reports', methods=['GET'])
def get_reports_list():
    uuid_param = request.args.get('uuid')
    # allow certain uuids only
    allowed_uuids = ["m3his@dhd"]  # Example list of allowed UUIDs
    if uuid_param not in allowed_uuids:
        return jsonify({"error": "Unauthorized, Please supply id"}), 403

    try:
        path = os.getcwd()
        reports_json = os.path.join(path, 'data', 'hmis_reports.json')
        with open(reports_json, "r") as f:
            json_data = json.load(f)

        reports = [
            {
                "report_id": r["page_name"],
                "report_name": r["report_name"],
                "date_updated": r["date_updated"]
            }
            for r in json_data.get("reports", []) 
            if r.get("archived", "").lower() == "false"
        ]

        return jsonify({"reports": reports})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@server.route(f'/api/datasets', methods=['GET'])
# example: http://localhost:8050/api/datasets?uuid=1&period=Monthly:January:2025&hf_code=SA091312&report_name=idsr_monthly
def get_report_dataset():
    # Parameters: UUID, Period (Format: "Type:Value:Year"), Health Facility ID, Report Name
    uuid_param = request.args.get('uuid')
    period_param = request.args.get('period') #Expected "Monthly:January:2025" or similar
    facility_id = request.args.get('hf_code') #MHFR
    report_name_id = request.args.get('report_name')

    if not all([period_param, facility_id, report_name_id]):
        return jsonify({"error": "Missing required parameters: Period, Health Facility ID, Report Name"}), 400

    try:
        # Parse Period
        period_parts = period_param.split(':')
        if len(period_parts) != 3:
            return jsonify({"error": "Invalid Period format. Expected 'Type:Value:Year' (e.g., 'Monthly:January:2025')"}), 400
        
        period_type, period_value, period_year = period_parts
        
        if period_type == 'Weekly':
            start_date, end_date = get_week_start_end(period_value, period_year)
        elif period_type == 'Monthly':
            start_date, end_date = get_month_start_end(period_value, period_year)
        elif period_type == 'Quarterly':
            start_date, end_date = get_quarter_start_end(period_value, period_year)
        else:
            return jsonify({"error": f"Invalid period type: {period_type}"}), 400
        
        # allow certain uuids only
        allowed_uuids = ["m3his@dhd"]  # Example list of allowed UUIDs
        if uuid_param not in allowed_uuids:
            return jsonify({"error": "Unauthorized, Please supply id"}), 403

        # Load Report Specs
        path = os.getcwd()
        reports_json = os.path.join(path, 'data', 'hmis_reports.json')
        with open(reports_json, "r") as f:
            json_data = json.load(f)
        
        
        report = next((r for r in json_data["reports"] if r['page_name'] == report_name_id and r["archived"].lower() == "false"), None)
        if not report:
            return jsonify({"error": "Report Not Found"}), 404

        # Load Data
        parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
        if not os.path.exists(parquet_path):
            return jsonify({"error": "Data file not found"}), 500
        
        data_opd = pd.read_parquet(parquet_path)
        data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
        data_opd['Gender'] = data_opd['Gender'].replace({"M":"Male","F":"Female"})
        data_opd["DateValue"] = pd.to_datetime(data_opd["Date"]).dt.date
        today = dt.today().date()
        data_opd["months"] = data_opd["DateValue"].apply(lambda d: (today - d).days // 30)

        # Filter by Facility
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == facility_id.lower()]
        # Filter by Date
        filtered = search_url[
            (pd.to_datetime(search_url['Date']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(search_url['Date']) <= pd.to_datetime(end_date))
        ]
        
        original_data = data_opd[data_opd['Date'] <= pd.to_datetime(end_date)].copy()
        original_data["days_before"] = original_data["DateValue"].apply(lambda d: (start_date - d).days)
        # Build Report
        spec_path = os.path.join(path, "data", "uploads", f"{report['page_name']}.xlsx")
        if not os.path.exists(spec_path):
            return jsonify({"error": "Report template not found"}), 500

        builder = ReportTableBuilder(spec_path, filtered, original_data)
        builder.load_spec()
        sections = builder.build_section_tables()

        # Prepare Response
        response_data = []
        for section_name, df in sections:
            response_data.append({
                "section_name": section_name,
                "data": df.to_dict(orient='records')
            })

        return jsonify({
            "report_id": report_name_id,
            "report_name": report['report_name'],
            "facility_id": facility_id,
            "period": period_param,
            "sections": response_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True,)