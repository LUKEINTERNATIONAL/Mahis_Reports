import dash
from dash import html, dcc, dash_table, Input, Output, State, callback, ctx
import json
import os
import uuid
import pandas as pd
from datetime import datetime
import base64
import io
from .modal_functions import (validate_excel_file, load_reports_data, save_reports_data, 
                        check_existing_report, get_next_report_id, update_or_create_report,load_excel_file,
                        save_excel_file, update_report_metadata, archive_report, load_preview_data,
                        create_count_item,create_chart_item, create_section,create_chart_fields,CHART_TEMPLATES)

dash.register_page(__name__, path="/admin/configurations", title="Admin Dashboard")

DASHBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "report_id": {"type": "string"},
        "report_name": {"type": "string"},
        "date_created": {"type": "string"},
        "visualization_types": {
            "type": "object",
            "properties": {
                "counts": {"type": "array"},
                "charts": {"type": "object"}
            },
            "required": ["charts"]
        }
    },
    "required": ["report_id", "report_name", "date_created", "visualization_types"]
}

# Load existing dashboards
path = os.getcwd()
dashboards_json_path = os.path.join(path, 'data','visualizations', 'dashboards.json')
try:
    with open(dashboards_json_path, 'r') as f:
        dashboards_data = json.load(f)
        # If it's a single dashboard, convert to list
        if isinstance(dashboards_data, dict):
            dashboards_data = [dashboards_data]
except FileNotFoundError:
    dashboards_data = []


def build_reports_table(data):
    # Filter out archived reports
    active_reports = [item for item in data if item.get("archived", "False") == "False"]
    
    if not active_reports:
        return html.P("No reports available.", style={'textAlign': 'center'})

    table_header = html.Thead(html.Tr([
        html.Th("Report ID"),
        html.Th("Report Name"),
        # html.Th("Date Created"),
        html.Th("Creator"),
        html.Th("Date Updated"),
        html.Th("Report Type"),
        html.Th("Page Name"),
        html.Th("Actions"),
    ]))

    table_rows = []

    for item in active_reports:
        table_rows.append(
            html.Tr([
                html.Td(item.get("report_id")),
                html.Td(item.get("report_name")),
                # html.Td(item.get("date_created")),
                html.Td(item.get("creator")),
                html.Td(item.get("date_updated")),
                html.Td(item.get("kind")),
                html.Td(item.get("page_name")),
                html.Td([
                    html.Button(
                        "Edit",
                        id={"type": "edit-btn", "index": item.get("report_id")},
                        className="report-action-btn edit-btn"
                    ),
                    html.Button(
                        "Archive",
                        id={"type": "archive-btn", "index": item.get("report_id")},
                        className="report-action-btn archive-btn"
                    )
                ])
            ])
        )

    table_body = html.Tbody(table_rows)

    return html.Table(
        [table_header, table_body],
        style={'width': '100%', 'borderCollapse': 'collapse'},
        className="report-table"
    )


def create_editable_table(df, sheet_name):
    """Create an editable Dash DataTable from DataFrame"""
    columns = [{"name": col, "id": col} for col in df.columns]
    
    # Convert DataFrame to dictionary for DataTable
    data = df.to_dict('records')
    
    return html.Div([
        html.H4(f"Sheet: {sheet_name}", style={'marginBottom': '10px'}),
        dash_table.DataTable(
            id={'type': 'editable-table', 'sheet': sheet_name},
            columns=columns,
            data=data,
            editable=True,
            filter_action="native",
            sort_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={
                'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
        )
    ], style={'marginBottom': '20px'})


def create_preview_table(df):
    """Create a Dash DataTable for preview with filters"""
    columns = [{"name": col, "id": col} for col in df.columns]
    
    # Convert DataFrame to dictionary for DataTable
    data = df.to_dict('records')
    
    return dash_table.DataTable(
        id="preview-data-table-component",
        columns=columns,
        data=data,
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'minWidth': '100px', 
            'width': '150px', 
            'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'left'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'textAlign': 'left'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        css=[{
            'selector': '.dash-spreadsheet td div',
            'rule': '''
                line-height: 15px;
                max-height: 30px; min-height: 30px; height: 30px;
                display: block;
                overflow-y: hidden;
            '''
        }]
    )

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

                    html.Div(
                        id="delete-confirmation-modal",
                        style={"display": "none"},  # Initially hidden
                        className="confirmation-modal",
                        children=[
                            html.Div([
                                html.H4("Confirm Delete"),
                                html.P("Are you sure you want to delete this dashboard? This action cannot be undone."),
                                html.Div(className="confirmation-buttons", children=[
                                    html.Button("Cancel", id="cancel-delete-btn", className="btn-secondary"),
                                    html.Button("Delete", id="confirm-delete-btn", className="btn-danger"),
                                ])
                            ])
                        ]
                    )
                ])
            ]
        )
])

# Helper functions for creating form elements

layout = html.Div([
    html.H1("Reports Configuration", style={'textAlign': 'center'}),
    html.P("Step 1: Update an excel template as provided on the menu below. Be sure to fill all worksheets", style={'textAlign': 'center'}),
    html.P("Step 2: Upload the worksheet. Dry run to check if the values are consistent with requirements", style={'textAlign': 'center'}),
    html.P("Step 3: To edit or archive, click on the item end and edit or review. The edit will open a popup editing tool with worksheets", style={'textAlign': 'center'}),

    # --- Top action buttons ---
    html.Div([
        html.Button(
            "Add New Report from Template",
            id="add-from-template-btn",
            n_clicks=0,
            style={
                'backgroundColor': '#0d6efd',
                'color': 'white',
                'border': 'none',
                'padding': '10px 16px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'marginRight': '10px'
            }
        ),
        html.Button(
            "Download Template",
            id="download-sample",
            n_clicks=0,
            style={
                'backgroundColor': '#0d6efd',
                'color': 'white',
                'border': 'none',
                'padding': '10px 16px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'marginRight': '10px'
            }
        ),
        html.Button(
            "Add dashboard",
            id="add-dashboard",
            n_clicks=0,
            style={
                'backgroundColor': "#198754",
                'color': 'white',
                'border': 'none',
                'padding': '10px 16px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'marginRight': '10px'
            }
        ),
        html.Button(
            "Preview Data",
            id="preview-data",
            n_clicks=0,
            style={
                'backgroundColor': "#9F799D",
                'color': 'white',
                'border': 'none',
                'padding': '10px 16px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'marginRight': '10px'
            }
        ),
        html.Button(
            "Logout",
            id="logout-button",
            n_clicks=0,
            style={
                'backgroundColor': '#6c757d',
                'color': 'white',
                'border': 'none',
                'padding': '10px 16px',
                'borderRadius': '6px',
                'cursor': 'pointer'
            }
        ),
    ], style={
        'textAlign': 'center',
        'marginBottom': '20px'
    }),

        # Preview Data Popup Modal
    html.Div([
        html.Div([
            html.H3("Preview Data", style={'marginBottom': '20px'}),
            
            html.Div(id="preview-data-info", style={'marginBottom': '20px'}),
            
            # Data table container
            html.Div(id="preview-data-table", style={'maxHeight': '500px', 'overflowY': 'auto', 'marginBottom': '20px'}),
            
            html.Div([
                html.Button(
                    "Close",
                    id="close-preview-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#6c757d',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'width': '90%',
            'maxWidth': '1400px',
            'maxHeight': '90vh',
            'overflowY': 'auto',
            'margin': 'auto'
        })
    ], id="preview-popup", style={
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(0,0,0,0.5)',
        'display': 'none',
        'justifyContent': 'center',
        'alignItems': 'center',
        'zIndex': '1000'
    }),

    # Upload Popup Modal
    html.Div([
        html.Div([
            html.H3("Upload Template File", style={'marginBottom': '20px'}),
            
            dcc.Upload(
                id='template-file-upload',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'marginBottom': '20px'
                },
                multiple=False,
                accept='.xlsx'
            ),
            
            html.Div(id='upload-validation-result', style={'marginBottom': '20px'}),
            html.Div(id='existing-report-warning', style={'marginBottom': '20px'}),
            
            html.Div([
                html.Button(
                    "Dry Run",
                    id="dry-run-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#ffc107',
                        'color': 'black',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Upload",
                    id="upload-confirm-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#198754',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    },
                    disabled=True
                ),
                html.Button(
                    "Cancel",
                    id="upload-cancel-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#6c757d',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'width': '500px',
            'margin': 'auto'
        })
    ], id="upload-popup", style={
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(0,0,0,0.5)',
        'display': 'none',
        'justifyContent': 'center',
        'alignItems': 'center',
        'zIndex': '1000'
    }),

    # Edit Popup Modal
    html.Div([
        html.Div([
            html.H3("Edit Excel File", id="edit-popup-title", style={'marginBottom': '20px'}),
            
            # Tabs for different sheets
            dcc.Tabs(id="sheet-tabs", value=None),
            
            # Tables container
            html.Div(id="sheet-tables-container", style={'maxHeight': '400px', 'overflowY': 'auto', 'marginBottom': '20px'}),
            
            # Action buttons
            html.Div([
                html.Button(
                    "Save Changes",
                    id="save-excel-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#198754',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Cancel",
                    id="edit-cancel-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#6c757d',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'width': '90%',
            'maxWidth': '1200px',
            'maxHeight': '90vh',
            'overflowY': 'auto',
            'margin': 'auto'
        })
    ], id="edit-popup", style={
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(0,0,0,0.5)',
        'display': 'none',
        'justifyContent': 'center',
        'alignItems': 'center',
        'zIndex': '1000'
    }),

    # Archive Confirmation Popup Modal
    html.Div([
        html.Div([
            html.H3("Archive Report", style={'marginBottom': '20px'}),
            
            html.Div(id="archive-confirmation-message", style={'marginBottom': '20px', 'fontSize': '16px'}),
            
            html.Div([
                html.Button(
                    "Confirm Archive",
                    id="confirm-archive-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#dc3545',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Cancel",
                    id="cancel-archive-btn",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#6c757d',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'width': '500px',
            'margin': 'auto'
        })
    ], id="archive-popup", style={
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(0,0,0,0.5)',
        'display': 'none',
        'justifyContent': 'center',
        'alignItems': 'center',
        'zIndex': '1000'
    }),

    create_edit_modal(),

    # auto-refresh every 5 seconds (optional)
    dcc.Interval(id="refresh-interval", interval=5000, n_intervals=0),

    # table container
    html.Div(id="reports-table-container", style={'maxWidth': '1200px', 'margin': '0 auto'}),
    
    # Store components for managing state
    dcc.Store(id="current-editing-report", data=None),
    dcc.Store(id="excel-sheet-data", data=None),
    dcc.Store(id="current-archive-report", data=None),
    dcc.Download(id="download-template"),
    dcc.Store(id="preview-data-store", data=None),  # Add this line

    # Dashboard
    dcc.Store(id='current-dashboard-data', data={}),
    dcc.Store(id='current-dashboard-index', data=-1),
    dcc.Store(id='delete-confirmation', data=False)
])

@callback(
    Output('download-template', 'data'),
    Input('download-sample', 'n_clicks'),
    prevent_initial_call=True
)
def download_template(clicks):
    if clicks:
        return dcc.send_file("data/report_template.xlsx")

@callback(
    Output("reports-table-container", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_reports_table(_):
    # Load fresh data
    data = load_reports_data()
    reports = data.get("reports", [])

    # Build the table (this will filter out archived reports)
    return build_reports_table(reports)


@callback(
    [Output("upload-popup", "style"),
     Output("template-file-upload", "contents"),
     Output("upload-validation-result", "children"),
     Output("existing-report-warning", "children")],
    [Input("add-from-template-btn", "n_clicks"),
     Input("upload-cancel-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_upload_popup(add_clicks, cancel_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "add-from-template-btn":
        return {'display': 'flex', 'position': 'fixed', 'top': '0', 'left': '0', 
                'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 
                'justifyContent': 'center', 'alignItems': 'center', 'zIndex': '1000'}, None, "", ""
    elif trigger_id == "upload-cancel-btn":
        return {'display': 'none'}, None, "", ""
    
    return dash.no_update


@callback(
    [Output("upload-validation-result", "children", allow_duplicate=True),
     Output("existing-report-warning", "children", allow_duplicate=True),
     Output("upload-confirm-btn", "disabled", allow_duplicate=True),
     Output("dry-run-btn", "disabled", allow_duplicate=True)],
    [Input("template-file-upload", "contents"),
     Input("dry-run-btn", "n_clicks")],
    [State("template-file-upload", "contents")],
    prevent_initial_call=True
)
def handle_file_validation_and_dry_run(contents, dry_run_clicks, contents_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Use the most recent contents - either from upload or from state
    current_contents = contents if contents is not None else contents_state
    
    if current_contents is None:
        return html.Div("Please upload an Excel file", style={'color': 'orange'}), "", True, True
    
    is_valid, message, report_name_df, filters_df = validate_excel_file(current_contents)
    
    if not is_valid:
        return html.Div(f"Validation failed: {message}", style={'color': 'red'}), "", True, True
    
    # Check if report already exists
    page_name = report_name_df['id'].iloc[0]
    exists, existing_report = check_existing_report(page_name)
    
    warning_message = ""
    if exists:
        warning_message = html.Div([
            html.Div("⚠️ Warning: Report with this page_name already exists", style={'color': 'orange', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div(f"Existing Report: {existing_report.get('report_name')} (ID: {existing_report.get('report_id')})", style={'color': 'orange'}),
            html.Div("This upload will replace the existing report.", style={'color': 'orange'})
        ])
    
    # If trigger was file upload, return basic validation results
    if trigger_id == "template-file-upload":
        return html.Div(message, style={'color': 'green'}), warning_message, False, False
    
    # If trigger was dry run button, return detailed dry run results
    elif trigger_id == "dry-run-btn":
        # Extract information for dry run
        report_name = report_name_df['name'].iloc[0]
        current_time = datetime.now().strftime("%Y-%m-%d")

        # Check if report has valid column names according to the column names
        filters_columns = [x for x in filters_df.columns.tolist() if x.startswith('variable')]
        filters_df_filtered = filters_df[filters_columns]
        variable_names_list = list(set([str(x).strip() for x in filters_df_filtered.values.flatten() if pd.notna(x) and x.strip()!='']))

        # Check if variable names are the same as in the data
        verification_df, nothing = load_preview_data()
        verification_df_columns = verification_df.columns.tolist()

        not_correct = []
        correct = []
        dry_run_warning = []

        for i in variable_names_list:
            if i in verification_df_columns:
                correct.append(i)
            else:
                not_correct.append(i)
        if len(not_correct)>0:
            dry_run_warning.append(html.Div(f"The following filter columns may need to be corrected: {not_correct}", style={'color': 'red', 'marginBottom': '5px'}))
        
        dry_run_info = [
            html.Div("Dry run successful!", style={'color': 'green', 'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"Report Name: {report_name}", style={'color': 'blue', 'marginBottom': '5px'}),
            # html.Div(f"Variable Filters: {variable_names_list}", style={'color': 'blue', 'marginBottom': '5px'}),
            # html.Div(f"All filter are correct: {correct}", style={'color': 'blue', 'marginBottom': '5px'}),
            # html.Div(f"Page Name: {page_name}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"Date Created/Updated: {current_time}", style={'color': 'blue', 'marginBottom': '5px'}),
        ]
        
        
        if exists:
            dry_run_warning.append(html.Div([
                html.Div("⚠️ Existing report will be updated:", style={'color': 'orange', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div(f"Existing: {existing_report.get('report_name')} (ID: {existing_report.get('report_id')})", style={'color': 'orange'}),
                html.Div(f"New: {report_name}", style={'color': 'orange'})
            ]))
        else:
            new_id = get_next_report_id()
            dry_run_info.append(html.Div(f"New Report ID: {new_id}", style={'color': 'green', 'marginBottom': '5px'}))
        
        return html.Div(dry_run_info), dry_run_warning, False, False
    
    return dash.no_update


@callback(
    [Output("upload-popup", "style", allow_duplicate=True),
     Output("upload-validation-result", "children", allow_duplicate=True),
     Output("existing-report-warning", "children", allow_duplicate=True)],
    Input("upload-confirm-btn", "n_clicks"),
    State("template-file-upload", "contents"),
    prevent_initial_call=True
)
def upload_file(n_clicks, contents):
    if contents is None:
        return dash.no_update, html.Div("No file to upload", style={'color': 'red'}), ""
    
    is_valid, message, report_name_df, filters_df = validate_excel_file(contents)
    
    if not is_valid:
        return dash.no_update, html.Div(f"Cannot upload: {message}", style={'color': 'red'}), ""
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Extract information from REPORT_NAME sheet
        page_name = report_name_df['id'].iloc[0]
        report_name = report_name_df['name'].iloc[0]
        filename = f"{page_name}.xlsx"
        
        # Check if report already exists
        exists, existing_report = check_existing_report(page_name)
        
        # Save the file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(decoded)
        
        # Update or create report in JSON
        updated_data = update_or_create_report(report_name_df, is_update=exists, existing_report=existing_report)
        
        # Prepare success message
        success_elements = [
            html.Div("File uploaded successfully!", style={'color': 'green', 'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"Saved as: {filename}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"Report Name: {report_name}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"Page Name: {page_name}", style={'color': 'blue', 'marginBottom': '5px'})
        ]
        
        if exists:
            success_elements.append(html.Div("🔄 Existing report was updated", style={'color': 'orange', 'marginBottom': '5px'}))
            success_elements.append(html.Div(f"📊 Report ID: {existing_report.get('report_id')}", style={'color': 'blue', 'marginBottom': '5px'}))
        else:
            new_id = get_next_report_id() - 1  # Since we just added one
            success_elements.append(html.Div(f"🆕 New Report ID: {new_id}", style={'color': 'green', 'marginBottom': '5px'}))
        
        success_message = html.Div(success_elements)
        
        # Close popup after successful upload
        return {'display': 'none'}, success_message, ""
        
    except Exception as e:
        error_message = html.Div(f"❌ Upload failed: {str(e)}", style={'color': 'red'})
        return dash.no_update, error_message, ""


@callback(
    [Output("edit-popup", "style"),
     Output("current-editing-report", "data"),
     Output("edit-popup-title", "children"),
     Output("sheet-tabs", "children"),
     Output("sheet-tabs", "value"),
     Output("sheet-tables-container", "children"),
     Output("excel-sheet-data", "data")],
    [Input({"type": "edit-btn", "index": dash.ALL}, "n_clicks"),
     Input("edit-cancel-btn", "n_clicks")],
    [State("reports-table-container", "children")],
    prevent_initial_call=True
)
def toggle_edit_popup(edit_clicks, cancel_clicks, reports_table):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if "edit-cancel-btn" in trigger_id:
        return {'display': 'none'}, None, "", None, None, "", None
    
    if "edit-btn" in trigger_id:
        # Get the report_id from the button that was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_id_dict = json.loads(button_id.replace("'", '"'))
        report_id = button_id_dict['index']
        
        # Find the report data
        data = load_reports_data()
        reports = data.get("reports", [])
        current_report = None
        
        for report in reports:
            if report.get("report_id") == report_id:
                current_report = report
                break
        
        if not current_report:
            return dash.no_update
        
        page_name = current_report.get("page_name")
        report_name = current_report.get("report_name")
        
        # Load the Excel file
        excel_file = load_excel_file(page_name)
        if not excel_file:
            return dash.no_update
        
        # Create tabs for each sheet
        sheet_names = excel_file.sheet_names
        tabs = []
        sheet_tables = []
        sheet_data_dict = {}
        
        for i, sheet_name in enumerate(sheet_names):
            # Read sheet data
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_data_dict[sheet_name] = df.to_dict('records')
            
            # Create tab
            tabs.append(dcc.Tab(label=sheet_name, value=sheet_name))
            
            # Create table for this sheet
            sheet_table = create_editable_table(df, sheet_name)
            sheet_tables.append(sheet_table)
        
        # Set first sheet as active
        active_tab = sheet_names[0] if sheet_names else None
        
        title = f"Editing: {report_name} ({page_name}.xlsx)"
        
        return (
            {'display': 'flex'}, 
            current_report,
            title,
            tabs,
            active_tab,
            sheet_tables[0] if sheet_tables else "No sheets found",
            sheet_data_dict
        )
    
    return dash.no_update


@callback(
    Output("sheet-tables-container", "children", allow_duplicate=True),
    Input("sheet-tabs", "value"),
    State("excel-sheet-data", "data"),
    prevent_initial_call=True
)
def update_sheet_display(selected_sheet, sheet_data):
    if not selected_sheet or not sheet_data or selected_sheet not in sheet_data:
        return "No sheet selected"
    
    # Convert the stored data back to DataFrame
    df = pd.DataFrame(sheet_data[selected_sheet])
    
    # Create the editable table
    return create_editable_table(df, selected_sheet)


@callback(
    Output("excel-sheet-data", "data", allow_duplicate=True),
    Input({"type": "editable-table", "sheet": dash.ALL}, "data"),
    State({"type": "editable-table", "sheet": dash.ALL}, "id"),
    State("excel-sheet-data", "data"),
    prevent_initial_call=True
)
def update_sheet_data(table_data, table_ids, current_sheet_data):
    if not table_data or not current_sheet_data:
        return dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # Get the sheet that was updated
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_id_dict = json.loads(trigger_id.replace("'", '"'))
    updated_sheet = trigger_id_dict['sheet']
    
    # Find the index of the updated table
    for i, table_id in enumerate(table_ids):
        if table_id['sheet'] == updated_sheet:
            # Update the data for this sheet
            current_sheet_data[updated_sheet] = table_data[i]
            break
    
    return current_sheet_data


@callback(
    [Output("edit-popup", "style", allow_duplicate=True),
     Output("upload-validation-result", "children", allow_duplicate=True)],
    Input("save-excel-btn", "n_clicks"),
    [State("current-editing-report", "data"),
     State("excel-sheet-data", "data")],
    prevent_initial_call=True
)
def save_excel_changes(save_clicks, current_report, sheet_data):
    if not save_clicks or not current_report or not sheet_data:
        return dash.no_update
    
    try:
        page_name = current_report.get("page_name")
        report_id = current_report.get("report_id")
        
        # Convert sheet data back to DataFrames
        sheet_dataframes = {}
        for sheet_name, data_dict in sheet_data.items():
            sheet_dataframes[sheet_name] = pd.DataFrame(data_dict)
        
        # Save to Excel file
        save_excel_file(page_name, sheet_dataframes)
        
        # Update metadata in reports.json
        update_report_metadata(report_id)
        
        success_message = html.Div([
            html.Div("Excel file saved successfully!", style={'color': 'green', 'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"File: {page_name}.xlsx", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"Updated: {datetime.now().strftime('%Y-%m-%d')}", style={'color': 'blue', 'marginBottom': '5px'})
        ])
        
        # Close the popup
        return {'display': 'none'}, success_message
        
    except Exception as e:
        error_message = html.Div(f"❌ Error saving file: {str(e)}", style={'color': 'red'})
        return dash.no_update, error_message


@callback(
    [Output("archive-popup", "style"),
     Output("current-archive-report", "data"),
     Output("archive-confirmation-message", "children")],
    [Input({"type": "archive-btn", "index": dash.ALL}, "n_clicks"),
     Input("cancel-archive-btn", "n_clicks")],
    [State({"type": "archive-btn", "index": dash.ALL}, "id"),
     State("reports-table-container", "children")],
    prevent_initial_call=True
)
def toggle_archive_popup(archive_clicks, cancel_clicks, archive_buttons_ids, reports_table):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if "cancel-archive-btn" in trigger_id:
        return {'display': 'none'}, None, ""
    
    if "archive-btn" in trigger_id:
        # Find which archive button was clicked
        button_index = None
        for i, clicks in enumerate(archive_clicks):
            if clicks and clicks > 0:  # Only proceed if button was actually clicked
                button_index = i
                break
        
        if button_index is None:
            return dash.no_update
        
        # Get the report_id from the button that was clicked
        report_id = archive_buttons_ids[button_index]['index']
        
        # Find the report data
        data = load_reports_data()
        reports = data.get("reports", [])
        current_report = None
        
        for report in reports:
            if report.get("report_id") == report_id:
                current_report = report
                break
        
        if not current_report:
            return dash.no_update
        
        # Create confirmation message
        confirmation_message = html.Div([
            html.Div("Are you sure you want to archive this report?", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"Report ID: {current_report.get('report_id')}", style={'marginBottom': '5px'}),
            html.Div(f"Report Name: {current_report.get('report_name')}", style={'marginBottom': '5px'}),
            html.Div(f"Page Name: {current_report.get('page_name')}", style={'marginBottom': '10px'}),
            html.Div("⚠️ This action cannot be undone. The report will be hidden from the main list.", 
                    style={'color': 'orange', 'fontStyle': 'italic'})
        ])
        
        return {'display': 'flex'}, current_report, confirmation_message
    
    return dash.no_update


@callback(
    [Output("archive-popup", "style", allow_duplicate=True),
     Output("upload-validation-result", "children", allow_duplicate=True)],
    Input("confirm-archive-btn", "n_clicks"),
    [State("current-archive-report", "data"),
     State("confirm-archive-btn", "n_clicks")],
    prevent_initial_call=True
)
def confirm_archive(n_clicks, current_report, current_n_clicks):
    # Check if the button was actually clicked (n_clicks > 0)
    if not n_clicks or n_clicks == 0 or not current_report:
        return dash.no_update
    
    try:
        report_id = current_report.get("report_id")
        report_name = current_report.get("report_name")
        
        # Archive the report
        archive_report(report_id)
        
        success_message = html.Div([
            html.Div("✅ Report archived successfully!", style={'color': 'green', 'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"📋 Report: {report_name}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"📊 Report ID: {report_id}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div("The report has been archived and will no longer appear in the list.", 
                    style={'color': 'gray', 'fontStyle': 'italic'})
        ])
        
        # Close the popup
        return {'display': 'none'}, success_message
        
    except Exception as e:
        error_message = html.Div(f"❌ Error archiving report: {str(e)}", style={'color': 'red'})
        return dash.no_update, error_message
    
@callback(
    [Output("preview-popup", "style"),
     Output("preview-data-info", "children"),
     Output("preview-data-table", "children")],
    [Input("preview-data", "n_clicks"),
     Input("close-preview-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_preview_popup(preview_clicks, close_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "close-preview-btn":
        return {'display': 'none'}, "", ""
    
    if trigger_id == "preview-data" and preview_clicks:
        # Load the preview data
        df, error = load_preview_data()
        
        if error:
            error_message = html.Div([
                html.Div("❌ Error loading preview data", style={'color': 'red', 'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.Div(error, style={'color': 'red'})
            ])
            return {'display': 'flex'}, error_message, ""
        
        if df is None or df.empty:
            no_data_message = html.Div([
                html.Div("📊 No data available", style={'color': 'orange', 'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.Div("The data file is empty or could not be loaded.", style={'color': 'orange'})
            ])
            return {'display': 'flex'}, no_data_message, ""
        
        # Create info message
        info_message = html.Div([
            html.Div("✅ Data loaded successfully", style={'color': 'green', 'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.Div(f"Records loaded: {len(df)} ( records)", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div(f"Columns: {len(df.columns)}", style={'color': 'blue', 'marginBottom': '5px'}),
            html.Div("Tip: Use the filter icons in column headers to filter data", style={'color': 'gray', 'fontStyle': 'italic'})
        ])
        
        # Create the preview table
        preview_table = create_preview_table(df)
        
        return {'display': 'flex'}, info_message, preview_table
    
    return dash.no_update

# DASHBOARD
@callback(
    [Output("modal-backdrop", "style",allow_duplicate=True),
     Output("modal-content", "style",allow_duplicate=True)],
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
     Input({"type": "remove-section", "index": dash.ALL}, "n_clicks"),
     Input({"type": "add-chart-btn", "index": dash.ALL}, "n_clicks"),
     Input({"type": "remove-chart", "section": dash.ALL, "index": dash.ALL}, "n_clicks")],
    [State("current-dashboard-data", "data"),
     State("current-dashboard-index", "data"),
     State("counts-container", "children"),
     State("sections-container", "children")],
    prevent_initial_call=True
)
def update_dashboard_form(selector_value, add_count_clicks, add_section_clicks, remove_count_clicks, 
                         remove_section_clicks, add_chart_clicks, remove_chart_clicks, 
                         current_data, current_index, counts_children, sections_children):
    ctx_triggered = ctx.triggered_id

    # Handle dashboard selection - RELOAD DATA HERE
    if ctx_triggered == "dashboard-selector":
        # Reload dashboards_data from file
        global dashboards_data

        path = os.getcwd()
        dashboards_json_path = os.path.join(path, 'data','visualizations', 'dashboards.json')
        try:
            with open(dashboards_json_path, 'r') as f:
                dashboards_data = json.load(f)
                # Ensure it's always a list
                if isinstance(dashboards_data, dict):
                    dashboards_data = [dashboards_data]
                elif not isinstance(dashboards_data, list):
                    dashboards_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            dashboards_data = []
        
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
            index_to_remove = ctx_triggered['index']
            new_counts_children = []
            for i, count in enumerate(counts_children):
                if i != index_to_remove:
                    new_count = create_count_item(index=len(new_counts_children))
                    new_counts_children.append(new_count)
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_counts_children, dash.no_update
    
    # Handle removing sections
    elif ctx_triggered and ctx_triggered['type'] == 'remove-section':
        if sections_children and len(sections_children) > 0:
            index_to_remove = ctx_triggered['index']
            new_sections_children = []
            for i, section in enumerate(sections_children):
                if i != index_to_remove:
                    new_section = create_section(index=len(new_sections_children))
                    new_sections_children.append(new_section)
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    # Handle adding charts to sections
    elif ctx_triggered and ctx_triggered['type'] == 'add-chart-btn':
        if sections_children and len(sections_children) > 0:
            section_index = ctx_triggered['index']
            
            # Update the specific section
            new_sections_children = []
            for i, section in enumerate(sections_children):
                if i == section_index:
                    # Get current charts from this section
                    current_charts = section['props']['children'][1]['props']['children'][1]['props']['children']
                    if current_charts is None:
                        current_charts = []
                    
                    # Add new chart
                    new_chart_index = len(current_charts)
                    new_chart = create_chart_item(section_index=section_index, chart_index=new_chart_index)
                    updated_charts = current_charts + [new_chart]
                    
                    # Recreate the section with updated charts
                    updated_section = create_section_with_charts(section, updated_charts, section_index)
                    new_sections_children.append(updated_section)
                else:
                    new_sections_children.append(section)
            
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    # Handle removing charts from sections
    elif ctx_triggered and ctx_triggered['type'] == 'remove-chart':
        if sections_children and len(sections_children) > 0:
            section_index = ctx_triggered['section']
            chart_index_to_remove = ctx_triggered['index']
            
            # Update the specific section
            new_sections_children = []
            for i, section in enumerate(sections_children):
                if i == section_index:
                    # Get current charts from this section
                    current_charts = section['props']['children'][1]['props']['children'][1]['props']['children']
                    if current_charts and len(current_charts) > 0:
                        # Remove the specified chart and re-index
                        updated_charts = []
                        for j, chart in enumerate(current_charts):
                            if j != chart_index_to_remove:
                                new_chart = create_chart_item(section_index=section_index, chart_index=len(updated_charts))
                                updated_charts.append(new_chart)
                        
                        # Recreate the section with updated charts
                        updated_section = create_section_with_charts(section, updated_charts, section_index)
                        new_sections_children.append(updated_section)
                    else:
                        new_sections_children.append(section)
                else:
                    new_sections_children.append(section)
            
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    return current_data or {}, current_index or -1, "", "", "", counts_children or [], sections_children or []

def create_section_with_charts(section, charts, section_index):
    """Recreate a section with updated charts"""
    # Extract the section name from the existing section
    section_name_input = section['props']['children'][0]['props']['children'][0]['props']['children'][0]
    section_name = section_name_input['props']['value'] if 'value' in section_name_input['props'] else ""
    
    # Create new section data
    section_data = {
        'section_name': section_name,
        'items': []  # We don't need the actual items since we're recreating from UI
    }
    
    # Create new section with the updated charts
    new_section = html.Div(className="section-item", children=[
        html.Div(className="card-header", children=[
            html.Div(className="section-header", children=[
                html.Div(className="section-col", children=[
                    html.Label("Section Name *", className="form-label"),
                    dcc.Input(
                        id={"type": "section-name", "index": section_index},
                        value=section_name,
                        placeholder="e.g Attendance",
                        className="form-input"
                    ),
                ]),
                html.Div(className="section-col", children=[
                    html.Label("Actions", className="form-label"),
                    html.Button("🗑️ Remove Section", 
                              id={"type": "remove-section", "index": section_index},
                              n_clicks=0,
                              className="btn-danger")
                ]),
            ]),
        ]),
        html.Div(className="card-body", children=[
            html.Button("+ Add Chart", 
                      id={"type": "add-chart-btn", "index": section_index},
                      n_clicks=0,
                      className="btn-primary"),
            html.Div(id={"type": "charts-container", "index": section_index, "section": section_index}, 
                    className="charts-container",
                    children=charts),
        ]),
    ])
    
    return new_section

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
    [State("current-dashboard-index", "data"),
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
     State({"type": "section-name", "index": dash.ALL}, "value"),
     # Chart basic info
     State({"type": "chart-id", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-name", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-type", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-title", "section": dash.ALL, "index": dash.ALL}, "value"),
     # ALL possible chart fields for different chart types
     State({"type": "chart-date_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-y_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-x_title", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-y_title", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-unique_column", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-legend_title", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-color", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-label_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-value_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-top_n", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-names_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-values_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-x_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-age_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-gender_col", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-bin_size", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-index_col1", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-columns", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-aggfunc", "section": dash.ALL, "index": dash.ALL}, "value"),
     # ADD MISSING FIELD:
     State({"type": "chart-duration_default", "section": dash.ALL, "index": dash.ALL}, "value"),  # For all chart types
     State({"type": "chart-colormap", "section": dash.ALL, "index": dash.ALL}, "value"),  # For Pie charts
     # Common filter fields
     State({"type": "chart-filter_col1", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val1", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col2", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val2", "section": dash.ALL, "index": dash.ALL}, "value")],
    prevent_initial_call=True
)
def save_dashboard(save_clicks, current_index, report_name, report_id, date_created, 
                  counts_children, sections_children, count_ids, count_names, count_uniques,
                  count_vars1, count_vals1, count_vars2, count_vals2, section_names,
                  chart_ids, chart_names, chart_types, chart_titles,
                  chart_date_cols, chart_y_cols, chart_x_titles, chart_y_titles,
                  chart_unique_columns, chart_legend_titles, chart_colors,
                  chart_label_cols, chart_value_cols, chart_top_ns,
                  chart_names_cols, chart_values_cols, chart_x_cols,
                  chart_age_cols, chart_gender_cols, chart_bin_sizes,
                  chart_index_col1s, chart_columns, chart_aggfuncs,
                  chart_duration_defaults,  # ADDED: For all chart types
                  chart_colormaps,
                  chart_filter_col1s, chart_filter_val1s, chart_filter_col2s, chart_filter_val2s):
    
    if save_clicks and save_clicks > 0:
        if not report_name:
            return dash.no_update, dash.no_update, dash.no_update
        
        # Build counts data from UI state
        counts_data = []
        if count_ids and count_names:
            for i, (count_id, count_name) in enumerate(zip(count_ids, count_names)):
                if count_id and count_name:
                    count_data = {
                        "id": count_id,
                        "name": count_name,
                        "filters": {
                            "measure": "count",
                            "unique": count_uniques[i] if i < len(count_uniques) and count_uniques[i] else "person_id"
                        }
                    }
                    
                    # Add filters if provided
                    if (i < len(count_vars1) and count_vars1[i] and 
                        i < len(count_vals1) and count_vals1[i]):
                        count_data["filters"]["variable1"] = count_vars1[i]
                        count_data["filters"]["value1"] = count_vals1[i]
                    
                    if (i < len(count_vars2) and count_vars2[i] and 
                        i < len(count_vals2) and count_vals2[i]):
                        count_data["filters"]["variable2"] = count_vars2[i]
                        count_data["filters"]["value2"] = count_vals2[i]
                    
                    counts_data.append(count_data)
        
        # Build sections data from UI state
        sections_data = []
        if section_names:
            for section_index, section_name in enumerate(section_names):
                if section_name:
                    section_charts = []
                    
                    # Find all charts that belong to this section
                    if chart_ids and chart_names and chart_types:
                        for i in range(len(chart_ids)):
                            chart_id = chart_ids[i] if i < len(chart_ids) else None
                            chart_name = chart_names[i] if i < len(chart_names) else None
                            chart_type = chart_types[i] if i < len(chart_types) else None
                            
                            if chart_id and chart_name and chart_type:
                                # Create chart data with basic structure
                                chart_data = {
                                    "id": chart_id,
                                    "name": chart_name,
                                    "type": chart_type,
                                    "filters": {
                                        "measure": "chart",
                                        "unique": "any",  # Default value
                                        "duration_default": "any"  # Default value
                                    }
                                }
                                
                                # Add title if available
                                if chart_titles and i < len(chart_titles) and chart_titles[i]:
                                    chart_data["filters"]["title"] = chart_titles[i]
                                
                                # ADD DURATION_DEFAULT FOR ALL CHART TYPES
                                if chart_duration_defaults and i < len(chart_duration_defaults) and chart_duration_defaults[i]:
                                    chart_data["filters"]["duration_default"] = chart_duration_defaults[i]
                                
                                # Add chart-specific fields based on chart type
                                if chart_type == "Line":
                                    if chart_date_cols and i < len(chart_date_cols):
                                        chart_data["filters"]["date_col"] = chart_date_cols[i]
                                    if chart_y_cols and i < len(chart_y_cols):
                                        chart_data["filters"]["y_col"] = chart_y_cols[i]
                                    if chart_x_titles and i < len(chart_x_titles):
                                        chart_data["filters"]["x_title"] = chart_x_titles[i]
                                    if chart_y_titles and i < len(chart_y_titles):
                                        chart_data["filters"]["y_title"] = chart_y_titles[i]
                                    if chart_unique_columns and i < len(chart_unique_columns):
                                        chart_data["filters"]["unique_column"] = chart_unique_columns[i]
                                    if chart_legend_titles and i < len(chart_legend_titles):
                                        chart_data["filters"]["legend_title"] = chart_legend_titles[i]
                                    if chart_colors and i < len(chart_colors):
                                        chart_data["filters"]["color"] = chart_colors[i]
                                
                                elif chart_type == "Bar":
                                    if chart_label_cols and i < len(chart_label_cols):
                                        chart_data["filters"]["label_col"] = chart_label_cols[i]
                                    if chart_value_cols and i < len(chart_value_cols):
                                        chart_data["filters"]["value_col"] = chart_value_cols[i]
                                    if chart_x_titles and i < len(chart_x_titles):
                                        chart_data["filters"]["x_title"] = chart_x_titles[i]
                                    if chart_y_titles and i < len(chart_y_titles):
                                        chart_data["filters"]["y_title"] = chart_y_titles[i]
                                    if chart_top_ns and i < len(chart_top_ns):
                                        chart_data["filters"]["top_n"] = chart_top_ns[i]
                                    # ADD MISSING FIELDS FOR BAR (from your example):
                                    if chart_unique_columns and i < len(chart_unique_columns):
                                        chart_data["filters"]["unique_column"] = chart_unique_columns[i]
                                    if chart_legend_titles and i < len(chart_legend_titles):
                                        chart_data["filters"]["legend_title"] = chart_legend_titles[i]
                                    if chart_colors and i < len(chart_colors):
                                        chart_data["filters"]["color"] = chart_colors[i]
                                
                                elif chart_type == "Pie":
                                    if chart_names_cols and i < len(chart_names_cols):
                                        chart_data["filters"]["names_col"] = chart_names_cols[i]
                                    if chart_values_cols and i < len(chart_values_cols):
                                        chart_data["filters"]["values_col"] = chart_values_cols[i]
                                    if chart_unique_columns and i < len(chart_unique_columns):
                                        chart_data["filters"]["unique_column"] = chart_unique_columns[i]
                                    # ADD MISSING FIELD FOR PIE:
                                    if chart_colormaps and i < len(chart_colormaps) and chart_colormaps[i]:
                                        try:
                                            colormap_data = json.loads(chart_colormaps[i])
                                            chart_data["filters"]["colormap"] = colormap_data
                                        except json.JSONDecodeError:
                                            chart_data["filters"]["colormap"] = {}
                                
                                elif chart_type == "Column":
                                    if chart_x_cols and i < len(chart_x_cols):
                                        chart_data["filters"]["x_col"] = chart_x_cols[i]
                                    if chart_y_cols and i < len(chart_y_cols):
                                        chart_data["filters"]["y_col"] = chart_y_cols[i]
                                    if chart_x_titles and i < len(chart_x_titles):
                                        chart_data["filters"]["x_title"] = chart_x_titles[i]
                                    if chart_y_titles and i < len(chart_y_titles):
                                        chart_data["filters"]["y_title"] = chart_y_titles[i]
                                    if chart_unique_columns and i < len(chart_unique_columns):
                                        chart_data["filters"]["unique_column"] = chart_unique_columns[i]
                                    if chart_legend_titles and i < len(chart_legend_titles):
                                        chart_data["filters"]["legend_title"] = chart_legend_titles[i]
                                    if chart_colors and i < len(chart_colors):
                                        chart_data["filters"]["color"] = chart_colors[i]
                                
                                elif chart_type == "Histogram":
                                    if chart_age_cols and i < len(chart_age_cols):
                                        chart_data["filters"]["age_col"] = chart_age_cols[i]
                                    if chart_gender_cols and i < len(chart_gender_cols):
                                        chart_data["filters"]["gender_col"] = chart_gender_cols[i]
                                    if chart_x_titles and i < len(chart_x_titles):
                                        chart_data["filters"]["x_title"] = chart_x_titles[i]
                                    if chart_y_titles and i < len(chart_y_titles):
                                        chart_data["filters"]["y_title"] = chart_y_titles[i]
                                    if chart_bin_sizes and i < len(chart_bin_sizes):
                                        chart_data["filters"]["bin_size"] = chart_bin_sizes[i]
                                
                                elif chart_type == "PivotTable":
                                    if chart_index_col1s and i < len(chart_index_col1s):
                                        chart_data["filters"]["index_col1"] = chart_index_col1s[i]
                                    if chart_columns and i < len(chart_columns):
                                        chart_data["filters"]["columns"] = chart_columns[i]
                                    if chart_values_cols and i < len(chart_values_cols):
                                        chart_data["filters"]["values_col"] = chart_values_cols[i]
                                    if chart_unique_columns and i < len(chart_unique_columns):
                                        chart_data["filters"]["unique_column"] = chart_unique_columns[i]
                                    if chart_aggfuncs and i < len(chart_aggfuncs):
                                        chart_data["filters"]["aggfunc"] = chart_aggfuncs[i]
                                    # ADD MISSING FIELDS FOR PIVOTTABLE:
                                    if chart_x_titles and i < len(chart_x_titles):
                                        chart_data["filters"]["x_title"] = chart_x_titles[i]
                                    if chart_y_titles and i < len(chart_y_titles):
                                        chart_data["filters"]["y_title"] = chart_y_titles[i]
                                
                                # Add common filter fields for ALL chart types
                                if chart_filter_col1s and i < len(chart_filter_col1s):
                                    chart_data["filters"]["filter_col1"] = chart_filter_col1s[i]
                                if chart_filter_val1s and i < len(chart_filter_val1s):
                                    chart_data["filters"]["filter_val1"] = chart_filter_val1s[i]
                                if chart_filter_col2s and i < len(chart_filter_col2s):
                                    chart_data["filters"]["filter_col2"] = chart_filter_col2s[i]
                                if chart_filter_val2s and i < len(chart_filter_val2s):
                                    chart_data["filters"]["filter_val2"] = chart_filter_val2s[i]
                                
                                section_charts.append(chart_data)
                    
                    section_data = {
                        "section_name": section_name,
                        "items": section_charts
                    }
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
        
        # Update or add to dashboards data
        if current_index == -1:  # New dashboard
            dashboards_data.append(dashboard_structure)
        elif 0 <= current_index < len(dashboards_data):  # Existing dashboard
            dashboards_data[current_index] = dashboard_structure
        else:  # Invalid index, add as new
            dashboards_data.append(dashboard_structure)
        
        # Save to file
        path = os.getcwd()
        dashboards_json_path = os.path.join(path, 'data','visualizations', 'dashboards.json')
        try:
            with open(dashboards_json_path, 'w') as f:
                json.dump(dashboards_data, f, indent=2)
        except Exception as e:
            print(f"Error saving dashboard: {e}")
        
        # Update dropdown options
        options = [{"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
                   "value": i} for i, d in enumerate(dashboards_data)] + \
                  [{"label": "➕ Create New Dashboard", "value": "new"}]
        
        return options, {"display": "none"}, {"display": "none"}
    
    return dash.no_update, dash.no_update, dash.no_update

@callback(
    [Output("dashboard-selector", "options", allow_duplicate=True),
     Output("modal-backdrop", "style", allow_duplicate=True),
     Output("modal-content", "style", allow_duplicate=True)],
    [Input("delete-btn", "n_clicks")],
    [State("current-dashboard-index", "data")],  # Use current index instead of selector value
    prevent_initial_call=True
)
def delete_dashboard(delete_clicks, current_index):
    if delete_clicks and delete_clicks > 0:
        # Check if we have a valid dashboard to delete
        if current_index is not None and current_index >= 0 and current_index < len(dashboards_data):
            # Remove the dashboard from the data
            dashboards_data.pop(current_index)
            
            # Save the updated data to file
            try:
                with open('dashboards.json', 'w') as f:
                    json.dump(dashboards_data, f, indent=2)
            except Exception as e:
                print(f"Error saving after deletion: {e}")
            
            # Update dropdown options
            options = [{"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
                       "value": i} for i, d in enumerate(dashboards_data)] + \
                      [{"label": "➕ Create New Dashboard", "value": "new"}]
            
            return options, {"display": "none"}, {"display": "none"}
        
        else:
            # If no valid dashboard is selected, just close the modal
            return dash.no_update, {"display": "none"}, {"display": "none"}
    
    return dash.no_update, dash.no_update, dash.no_update

@callback(
    Output("delete-confirmation-modal", "style"),
    Input("delete-confirmation", "data")
)
def toggle_confirmation_modal(show_confirmation):
    if show_confirmation:
        return {"display": "block", "position": "fixed", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)", "zIndex": "1000", "background": "white", "padding": "20px", "borderRadius": "5px", "boxShadow": "0 2px 10px rgba(0,0,0,0.1)"}
    else:
        return {"display": "none"}