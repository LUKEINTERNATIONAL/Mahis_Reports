# import dash
from dash import html, dcc, Input, Output, State, callback, ctx, dash
import json
import pandas as pd
from datetime import datetime
import uuid
import os

# DASHBOARDS

# dashboards_list sample
"""
{"dashboards":[
    {
        "id":1,
        "name":"home",
        "title":"Summary"
    },
    {
        "id":2,
        "name":"opd",
        "title":"OutPatient (OPD)"
    },]}
    """
# dashboard structure sample
"""
{
  "report_id": "master",
  "report_name": "master",
  "date_created": "2025-11-26",
  "visualization_types": {
    "counts": [
      {
        "id": "attendance",
        "name": "OPD Attendance",
        "filters": {
          "measure": "count",
          "unique": "person_id"
        }
      },
      {
        "id": "attendance_m",
        "name": "Attendance Male",
        "filters": {
          "measure": "count",
          "unique": "person_id",
          "variable1":"Gender",
          "value1":"Male"
        }
      }
    ],
    "charts": {
      "sections": [
        {
          "section_name": "OPD Attendance",
          "items": [
            {
              "id": "chart1",
              "name": "Daily OPD Attendance - Last 7 Days",
              "type": "Line",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "7days",
                "date_col": "Date",
                "y_col": "encounter_id",
                "title":"Daily OPD Attendance - Last 7 Days",
                "x_title": "Date",
                "y_title": "Number of Patients",
                "unique_column":"person_id",
                "legend_title":"Legend",
                "color":"",
                "filter_col1": "",
                "filter_val1": "",
                "filter_col2": "",
                "filter_val2": ""
                }
            },
            {
              "id": "chart2",
              "name": "Patient Visit Type",
              "type": "Pie",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "any",
                "names_col": "new_revisit",
                "values_col": "encounter_id",
                "title":"Patient Visit Type",
                "unique_column": "person_id",
                "filter_col1": "",
                "filter_val1": "",
                "filter_col2": "",
                "filter_val2": "",
                "colormap": {
                                "New": "#292D79",
                                "Revisit": "#FE1AD0"
                            }
                }
            },
            {
              "id": "chart1",
              "name": "Enrollment Type",
              "type": "Column",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "any",
                "x_col": "Program",
                "y_col": "encounter_id",
                "title":"Enrollment Type",
                "x_title": "Program",
                "y_title": "Number of Patients",
                "unique_column":"person_id",
                "legend_title":"Legend",
                "color":"",
                "filter_col1": "",
                "filter_val1": "",
                "filter_col2": "",
                "filter_val2": ""
                }
            },
            {
              "id": "chart1",
              "name": "Age Gender Disaggregation",
              "type": "Histogram",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "any",
                "age_col": "Age",
                "gender_col": "Gender",
                "title":"Age Gender Disaggregation",
                "x_title": "Program",
                "y_title": "Number of Patients",
                "bin_size": 5,
                "filter_col1": "",
                "filter_val1": "",
                "filter_col2": "",
                "filter_val2": ""
                }
            }
          ]
        },
        {
          "section_name": "Pivoted",
          "items": [
            {
              "id": "chart1",
              "name": "Medications dispensed",
              "type": "PivotTable",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "any",
                "index_col1": "DrugName",
                "columns": "Program",
                "values_col":"ValueN",
                "title": "Medications dispensed",
                "unique_column":"person_id",
                "aggfunc":"sum",
                "filter_col1": "Encounter",
                "filter_val1": "DISPENSING",
                "filter_col2": "",
                "filter_val2": "",
                "x_title": "",
                "y_title": ""
                }
            },
            {
              "id": "chart1",
              "name": "Alcohol Behaviour",
              "type": "Bar",
              "filters": {
                "measure": "chart",
                "unique": "any",
                "duration_default": "any",
                "label_col": "DrugName",
                "value_col": "Program",
                "title": "Medications dispensed",
                "x_title": "",
                "y_title": "",
                "top_n":10,
                "filter_col1": "Encounter",
                "filter_val1": "DISPENSING",
                "filter_col2": "",
                "filter_val2": ""
                }
            }
          ]
        }
      ]
    }
  }
}
"""

try:
    with open('dashboards.json', 'r') as f:
        dashboards_data = json.load(f)
        # Ensure it's always a list
        if isinstance(dashboards_data, dict):
            dashboards_data = [dashboards_data]
        elif not isinstance(dashboards_data, list):
            dashboards_data = []
except (FileNotFoundError, json.JSONDecodeError):
    dashboards_data = []

# Define chart elements for each chart type
CHART_ELEMENTS = {
    "Line": ["date_col", "y_col", "title", "x_title", "y_title", "unique_column", "legend_title", "color", "filter_col1", "filter_val1", "filter_col2", "filter_val2"],
    "Bar": ["label_col", "value_col", "title", "x_title", "y_title", "top_n", "filter_col1", "filter_val1", "filter_col2", "filter_val2"],
    "Pie": ["names_col", "values_col", "title", "unique_column", "filter_col1", "filter_val1", "filter_col2", "filter_val2"],
    "Column": ["x_col", "y_col", "title", "x_title", "y_title", "unique_column", "legend_title", "color", "filter_col1", "filter_val1", "filter_col2", "filter_val2"],
    "Histogram": ["age_col", "gender_col", "title", "x_title", "y_title", "bin_size", "filter_col1", "filter_val1", "filter_col2", "filter_val2"],
    "PivotTable": ["index_col1", "columns", "values_col", "title", "unique_column", "aggfunc", "filter_col1", "filter_val1", "filter_col2", "filter_val2", "x_title", "y_title"]
}

def create_chart_fields(chart_type, chart_data=None, section_index=None, chart_index=None):
    """Create dynamic input fields based on chart type"""
    chart_data = chart_data or {}
    filters = chart_data.get('filters', {})
    
    if chart_type not in CHART_ELEMENTS:
        return html.Div("Invalid chart type")
    
    fields = []
    elements = CHART_ELEMENTS[chart_type]
    
    # Create two columns layout
    left_col = []
    right_col = []
    
    for i, element in enumerate(elements):
        field_component = html.Div(className="chart-col", children=[
            html.Label(element.replace('_', ' ').title(), className="form-label"),
            dcc.Input(
                id={"type": f"chart-{element}", "section": section_index, "index": chart_index},
                value=filters.get(element, ''),
                placeholder=f"Enter {element.replace('_', ' ')}",
                className="form-input"
            ),
        ])
        
        # Distribute fields between two columns
        if i % 2 == 0:
            left_col.append(field_component)
        else:
            right_col.append(field_component)
    
    return html.Div(className="chart-fields-row", children=[
        html.Div(className="chart-fields-col", children=left_col),
        html.Div(className="chart-fields-col", children=right_col),
    ])

def create_count_item(count_data=None, index=None):
    count_data = count_data or {}
    return html.Div(className="count-item", children=[
        html.Div(className="count-row", children=[
            html.Div(className="count-col", children=[
                html.Label("Count ID *", className="form-label"),
                dcc.Input(
                    id={"type": "count-id", "index": index},
                    value=count_data.get('id', f'count_{uuid.uuid4().hex[:8]}'),
                    placeholder="unique_id",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Metric Name *", className="form-label"),
                dcc.Input(
                    id={"type": "count-name", "index": index},
                    value=count_data.get('name', ''),
                    placeholder="e.g. Total Registrations",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Unique Column", className="form-label"),
                dcc.Input(
                    id={"type": "count-unique", "index": index},
                    value=count_data.get('filters', {}).get('unique', 'person_id'),
                    placeholder="e.g person_id",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Actions", className="form-label"),
                html.Button("🗑️", 
                          id={"type": "remove-count", "index": index},
                          n_clicks=0,
                          className="btn-danger btn-small")
            ]),
        ]),
        html.Div(className="count-row", children=[
            html.Div(className="count-col", children=[
                html.Label("Filter Variable 1", className="form-label"),
                dcc.Input(
                    id={"type": "count-var1", "index": index},
                    value=count_data.get('filters', {}).get('variable1', ''),
                    placeholder="e.g Gender",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Filter Value 1", className="form-label"),
                dcc.Input(
                    id={"type": "count-val1", "index": index},
                    value=count_data.get('filters', {}).get('value1', ''),
                    placeholder="e.g. Male",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Filter Variable 2", className="form-label"),
                dcc.Input(
                    id={"type": "count-var2", "index": index},
                    value=count_data.get('filters', {}).get('variable2', ''),
                    placeholder="e.g. Age_Group",
                    className="form-input"
                ),
            ]),
            html.Div(className="count-col", children=[
                html.Label("Filter Value 2", className="form-label"),
                dcc.Input(
                    id={"type": "count-val2", "index": index},
                    value=count_data.get('filters', {}).get('value2', ''),
                    placeholder="e.g. Over 5",
                    className="form-input"
                ),
            ])
        ]),
    ])

def create_chart_item(chart_data=None, section_index=None, chart_index=None):
    chart_data = chart_data or {}
    chart_type = chart_data.get('type', 'Bar')
    
    return html.Div(className="chart-item", children=[
        html.Div(className="chart-row", children=[
            html.Div(className="chart-col", children=[
                html.Label("Chart ID *", className="form-label"),
                dcc.Input(
                    id={"type": "chart-id", "section": section_index, "index": chart_index},
                    value=chart_data.get('id', f'chart_{uuid.uuid4().hex[:8]}'),
                    placeholder="chart_id",
                    className="form-input"
                ),
            ]),
            html.Div(className="chart-col", children=[
                html.Label("Chart Name *", className="form-label"),
                dcc.Input(
                    id={"type": "chart-name", "section": section_index, "index": chart_index},
                    value=chart_data.get('name', ''),
                    placeholder="Chart Display Name",
                    className="form-input"
                ),
            ]),
            html.Div(className="chart-col", children=[
                html.Label("Chart Type *", className="form-label"),
                dcc.Dropdown(
                    id={"type": "chart-type", "section": section_index, "index": chart_index},
                    options=[{'label': t, 'value': t} for t in CHART_ELEMENTS.keys()],
                    value=chart_type,
                    className="dropdown"
                ),
            ]),
            html.Div(className="chart-col", children=[
                html.Label("Actions", className="form-label"),
                html.Button("🗑️", 
                          id={"type": "remove-chart", "section": section_index, "index": chart_index},
                          n_clicks=0,
                          className="btn-danger btn-small")
            ]),
        ]),
        html.Div(id={"type": "chart-fields", "section": section_index, "index": chart_index},
                children=create_chart_fields(chart_type, chart_data, section_index, chart_index)),
    ])

def create_section(section_data=None, index=None):
    section_data = section_data or {}
    
    # Create initial charts for this section
    initial_charts = []
    if section_data.get('items'):
        for i, chart_data in enumerate(section_data['items']):
            initial_charts.append(create_chart_item(chart_data, index, i))
    
    return html.Div(className="section-item", children=[
        html.Div(className="card-header", children=[
            html.Div(className="section-header", children=[
                html.Div(className="section-col", children=[
                    html.Label("Section Name *", className="form-label"),
                    dcc.Input(
                        id={"type": "section-name", "index": index},
                        value=section_data.get('section_name', ''),
                        placeholder="e.g Attendance",
                        className="form-input"
                    ),
                ]),
                html.Div(className="section-col", children=[
                    html.Label("Actions", className="form-label"),
                    html.Button("🗑️ Remove Section", 
                              id={"type": "remove-section", "index": index},
                              n_clicks=0,
                              className="btn-danger")
                ]),
            ]),
        ]),
        html.Div(className="card-body", children=[
            html.Button("+ Add Chart", 
                      id={"type": "add-chart-btn", "index": index},
                      n_clicks=0,
                      className="btn-primary"),
            html.Div(id={"type": "charts-container", "index": index}, 
                    className="charts-container",
                    children=initial_charts),
        ]),
    ])

# FOR DASHBOARDS
def create_edit_modal():
    return html.Div([
        # Modal backdrop
        html.Div(
            id="modal-backdrop",
            className="modal-backdrop"
        ),
        # Modal content
        html.Div(
            id="modal-content",
            className="modal-content",
            children=[
                html.Div([
                    html.H3("Dashboard Configuration", className="modal-title"),
                    
                    # Dashboard Selection/Creation
                    html.Div(className="card", children=[
                        html.Div(className="card-header", children=[
                            html.H4("Dashboard Title", className="card-header-title")
                        ]),
                        html.Div(className="card-body-flex", children=[
                            html.Div(className="card-col", children=[
                                html.Label("Select dashboard:", className="form-label"),
                                dcc.Dropdown(
                                    id="dashboard-selector",
                                    options=[{"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
                                             "value": i} for i, d in enumerate(dashboards_data)] + 
                                            [{"label": "➕ Create New Dashboard", "value": "new"}],
                                    value="new" if not dashboards_data else 0,
                                    className="dropdown"
                                ),
                            ]),
                            html.Div(className="card-col", children=[
                                html.Label("Report ID:", className="form-label"),
                                dcc.Input(
                                    id="report-id-input",
                                    type="text",
                                    placeholder="auto-generated",
                                    disabled=True,
                                    className="form-input"
                                ),
                            ]),
                        ]),
                        html.Div(className="card-body-flex", children=[
                            html.Div(className="card-col", children=[
                                html.Label("Report Name *", className="form-label"),
                                dcc.Input(
                                    id="report-name-input",
                                    type="text",
                                    placeholder="Enter report name...",
                                    className="form-input"
                                ),
                            ]),
                            html.Div(className="card-col", children=[
                                html.Label("Date Created", className="form-label"),
                                dcc.Input(
                                    id="date-created-input",
                                    type="text",
                                    disabled=True,
                                    className="form-input"
                                ),
                            ]),
                        ]),

                    ]),
                    
                    # Counts Section
                    html.Div(className="card", children=[
                        html.Div(className="card-header", children=[
                            html.Div(className="card-header-flex", children=[
                                html.H4("🔢 Metrics (Counts)", className="card-header-title"),
                                html.Button("➕ Add Count", id="add-count-btn", n_clicks=0, className="btn-primary")
                            ])
                        ]),
                        html.Div(id="counts-container", className="card-body"),
                    ]),
                    
                    # Charts Section
                    html.Div(className="card", children=[
                        html.Div(className="card-header", children=[
                            html.Div(className="card-header-flex", children=[
                                html.H4("📈 Charts & Sections", className="card-header-title"),
                                html.Button("➕ Add Section", id="add-section-btn", n_clicks=0, className="btn-primary")
                            ])
                        ]),
                        html.Div(id="sections-container", className="card-body"),
                    ]),
                    
                    # Action Buttons
                    html.Div(className="action-buttons", children=[
                        html.Button("Save Dashboard", id="save-btn", n_clicks=0, className="btn-success"),
                        html.Button("Cancel", id="cancel-btn", n_clicks=0, className="btn-secondary"),
                        html.Button("Delete Dashboard", id="delete-btn", n_clicks=0, className="btn-danger"),
                    ]),
                ])
            ]
        )
])

layout = html.Div([
    create_edit_modal(),
    dcc.Store(id='current-dashboard-data', data={}),
    dcc.Store(id='current-dashboard-index', data=-1)
])

# DASHBOARD
@callback(
    [Output("modal-backdrop", "style"),
     Output("modal-content", "style")],
    [Input("add-dashboard", "n_clicks"),
     Input("cancel-btn", "n_clicks"),
     Input("save-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, cancel_clicks, save_clicks):
    trigger = ctx.triggered_id
    
    if trigger == "add-dashboard" and open_clicks > 0:
        return {"display": "block"}, {"display": "block"}
    elif trigger in ["cancel-btn", "save-btn"]:
        return {"display": "none"}, {"display": "none"}
    
    return dash.no_update, dash.no_update

@callback(
    [Output("current-dashboard-data", "data"),
     Output("current-dashboard-index", "data"),
     Output("report-id-input", "value"),
     Output("report-name-input", "value"),
     Output("date-created-input", "value"),
     Output("counts-container", "children"),
     Output("sections-container", "children")],
    [Input("dashboard-selector", "value"),
     Input("add-count-btn", "n_clicks"),
     Input("add-section-btn", "n_clicks"),
     Input({"type": "remove-count", "index": dash.ALL}, "n_clicks"),
     Input({"type": "remove-section", "index": dash.ALL}, "n_clicks")],
    [State("current-dashboard-data", "data"),
     State("current-dashboard-index", "data"),
     State("counts-container", "children"),
     State("sections-container", "children")]
)
def update_dashboard_form(selector_value, add_count_clicks, add_section_clicks, remove_count_clicks, remove_section_clicks, current_data, current_index, counts_children, sections_children):
    ctx_triggered = ctx.triggered_id
    
    # Handle dashboard selection
    if ctx_triggered == "dashboard-selector":
        if selector_value == "new":
            # Create new dashboard template
            new_dashboard = {
                "report_id": f"report_{uuid.uuid4().hex[:8]}",
                "report_name": "New Dashboard",
                "date_created": datetime.now().strftime("%Y-%m-%d"),
                "visualization_types": {
                    "counts": [],
                    "charts": {"sections": []}
                }
            }
            return new_dashboard, -1, new_dashboard["report_id"], new_dashboard["report_name"], new_dashboard["date_created"], [], []
        
        elif isinstance(selector_value, int) and 0 <= selector_value < len(dashboards_data):
            dashboard = dashboards_data[selector_value]
            counts = dashboard.get('visualization_types', {}).get('counts', [])
            sections = dashboard.get('visualization_types', {}).get('charts', {}).get('sections', [])
            
            counts_children = [create_count_item(count, i) for i, count in enumerate(counts)]
            sections_children = [create_section(section, i) for i, section in enumerate(sections)]
            
            return dashboard, selector_value, dashboard["report_id"], dashboard["report_name"], dashboard["date_created"], counts_children, sections_children
    
    # Handle adding counts
    elif ctx_triggered == "add-count-btn" and add_count_clicks > 0:
        new_count_index = len(counts_children) if counts_children else 0
        new_count = create_count_item(index=new_count_index)
        if counts_children is None:
            counts_children = [new_count]
        else:
            counts_children = counts_children + [new_count]
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, counts_children, dash.no_update
    
    # Handle adding sections
    elif ctx_triggered == "add-section-btn" and add_section_clicks > 0:
        new_section_index = len(sections_children) if sections_children else 0
        new_section = create_section(index=new_section_index)
        if sections_children is None:
            sections_children = [new_section]
        else:
            sections_children = sections_children + [new_section]
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, sections_children
    
    # Handle removing counts
    elif ctx_triggered and ctx_triggered['type'] == 'remove-count':
        if counts_children and len(counts_children) > 0:
            # Remove the count at the specified index
            index_to_remove = ctx_triggered['index']
            counts_children = [count for i, count in enumerate(counts_children) if i != index_to_remove]
            # Re-index remaining counts
            for i, count in enumerate(counts_children):
                count['props']['id']['index'] = i
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, counts_children, dash.no_update
    
    # Handle removing sections
    elif ctx_triggered and ctx_triggered['type'] == 'remove-section':
        if sections_children and len(sections_children) > 0:
            # Remove the section at the specified index
            index_to_remove = ctx_triggered['index']
            sections_children = [section for i, section in enumerate(sections_children) if i != index_to_remove]
            # Re-index remaining sections
            for i, section in enumerate(sections_children):
                section['props']['id']['index'] = i
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, sections_children
    
    return current_data or {}, current_index or -1, "", "", "", counts_children or [], sections_children or []

@callback(
    [Output({"type": "charts-container", "index": dash.MATCH}, "children")],
    [Input({"type": "add-chart-btn", "index": dash.MATCH}, "n_clicks"),
     Input({"type": "remove-chart", "section": dash.MATCH, "index": dash.MATCH}, "n_clicks")],
    [State({"type": "charts-container", "index": dash.MATCH}, "children"),
     State({"type": "add-chart-btn", "index": dash.MATCH}, "id"),
     State({"type": "remove-chart", "section": dash.MATCH, "index": dash.MATCH}, "id")],
    prevent_initial_call=True
)
def manage_charts_in_section(add_clicks, remove_clicks, current_charts, add_button_id, remove_button_id):
    ctx_triggered = ctx.triggered_id
    
    if not ctx_triggered:
        return [dash.no_update]
    
    # Handle adding charts
    if ctx_triggered['type'] == 'add-chart-btn':
        if not add_clicks or add_clicks == 0:
            return [dash.no_update]
            
        section_index = add_button_id['index']
        
        # Create new chart
        new_chart_index = len(current_charts) if current_charts else 0
        new_chart = create_chart_item(section_index=section_index, chart_index=new_chart_index)
        
        if current_charts is None:
            updated_charts = [new_chart]
        else:
            updated_charts = current_charts + [new_chart]
            
        return [updated_charts]
    
    # Handle removing charts
    elif ctx_triggered['type'] == 'remove-chart':
        if not remove_clicks or remove_clicks == 0:
            return [dash.no_update]
            
        chart_index_to_remove = ctx_triggered['index']
        
        if current_charts and len(current_charts) > 0:
            # Remove the chart at the specified index
            updated_charts = [chart for i, chart in enumerate(current_charts) 
                            if chart['props']['id']['index'] != chart_index_to_remove]
            
            # Re-index remaining charts
            for i, chart in enumerate(updated_charts):
                chart['props']['id']['index'] = i
            
            return [updated_charts]
    
    return [dash.no_update]

@callback(
    Output({"type": "chart-fields", "section": dash.MATCH, "index": dash.MATCH}, "children"),
    [Input({"type": "chart-type", "section": dash.MATCH, "index": dash.MATCH}, "value")],
    prevent_initial_call=True
)
def update_chart_fields(chart_type):
    if not chart_type:
        return dash.no_update
    
    triggered_id = ctx.triggered_id
    section_index = triggered_id['section']
    chart_index = triggered_id['index']
    
    return create_chart_fields(chart_type, None, section_index, chart_index)

@callback(
    [Output("dashboard-selector", "options"),
     Output("modal-backdrop", "style"),
     Output("modal-content", "style")],
    [Input("save-btn", "n_clicks")],
    [State("current-dashboard-data", "data"),
     State("current-dashboard-index", "data"),
     State("report-name-input", "value"),
     State("report-id-input", "value"),
     State("date-created-input", "value"),
     State("counts-container", "children"),
     State("sections-container", "children"),
     State({"type": "count-id", "index": dash.ALL}, "value"),
     State({"type": "count-name", "index": dash.ALL}, "value"),
     State({"type": "count-unique", "index": dash.ALL}, "value"),
     State({"type": "count-var1", "index": dash.ALL}, "value"),
     State({"type": "count-val1", "index": dash.ALL}, "value"),
     State({"type": "count-var2", "index": dash.ALL}, "value"),
     State({"type": "count-val2", "index": dash.ALL}, "value"),
     State({"type": "section-name", "index": dash.ALL}, "value")],
    prevent_initial_call=True
)
def save_dashboard(save_clicks, current_data, current_index, report_name, report_id, date_created, 
                  counts_children, sections_children, count_ids, count_names, count_uniques,
                  count_vars1, count_vals1, count_vars2, count_vals2, section_names):
    
    if save_clicks and save_clicks > 0:
        if not report_name:
            return dash.no_update, dash.no_update, dash.no_update
        
        # Collect counts data
        counts_data = []
        if count_ids:
            for i, count_id in enumerate(count_ids):
                if count_id and count_names[i]:  # Only add if we have ID and name
                    count_data = {
                        "id": count_id,
                        "name": count_names[i],
                        "filters": {
                            "measure": "count",
                            "unique": count_uniques[i] if count_uniques[i] else "person_id"
                        }
                    }
                    
                    # Add filters if provided
                    if count_vars1[i] and count_vals1[i]:
                        count_data["filters"]["variable1"] = count_vars1[i]
                        count_data["filters"]["value1"] = count_vals1[i]
                    
                    if count_vars2[i] and count_vals2[i]:
                        count_data["filters"]["variable2"] = count_vars2[i]
                        count_data["filters"]["value2"] = count_vals2[i]
                    
                    counts_data.append(count_data)
        
        # Collect sections data
        sections_data = []
        if section_names:
            for section_index, section_name in enumerate(section_names):
                if not section_name:  # Skip empty sections
                    continue
                    
                section_data = {
                    "section_name": section_name,
                    "items": []
                }
                
                # Get charts for this section - in a real implementation, you would extract chart data
                # For now, we'll create placeholder chart data
                if sections_children and section_index < len(sections_children):
                    section_div = sections_children[section_index]
                    # Extract chart data from the section - this would need more complex parsing
                    # For demonstration, we'll add a placeholder chart
                    if section_data["items"] is None:
                        section_data["items"] = []
                
                sections_data.append(section_data)
        
        # Create complete dashboard structure
        dashboard_structure = {
            "report_id": report_id or f"report_{uuid.uuid4().hex[:8]}",
            "report_name": report_name,
            "date_created": date_created or datetime.now().strftime("%Y-%m-%d"),
            "visualization_types": {
                "counts": counts_data,
                "charts": {
                    "sections": sections_data
                }
            }
        }
        
        # Update or add to dashboards data - ensure it's a single object in a list
        if current_index == -1:  # New dashboard
            dashboards_data.append(dashboard_structure)
        elif 0 <= current_index < len(dashboards_data):  # Existing dashboard
            dashboards_data[current_index] = dashboard_structure
        else:  # Invalid index, add as new
            dashboards_data.append(dashboard_structure)
        
        # Save the complete list to file
        try:
            with open('dashboards.json', 'w') as f:
                json.dump(dashboards_data, f, indent=2)
        except Exception as e:
            print(f"Error saving dashboard: {e}")
        
        # Update dropdown options
        options = [{"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
                   "value": i} for i, d in enumerate(dashboards_data)] + \
                  [{"label": "➕ Create New Dashboard", "value": "new"}]
        
        return options, {"display": "none"}, {"display": "none"}
    
    return dash.no_update, dash.no_update, dash.no_update