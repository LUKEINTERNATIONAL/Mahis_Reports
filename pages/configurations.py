import dash
from dash import html, dcc, dash_table, Input, Output, State, callback, ctx
import json
import os
import uuid
import pandas as pd
from datetime import datetime
import base64
import io
from modal_functions import (validate_excel_file, load_reports_data, save_reports_data, 
                        check_existing_report, get_next_report_id, update_or_create_report,load_excel_file,
                        save_excel_file, update_report_metadata, archive_report, load_preview_data,
                        create_count_item,create_chart_item, create_section,create_chart_fields,validate_dashboard_json,
                        upload_dashboard_json,validate_prog_reports_json,upload_prog_reports_json,CHART_TEMPLATES)

dash.register_page(__name__, path="/reports_config", title="Admin Dashboard")


# Load existing dashboards
path = os.getcwd()
dashboards_json_path = os.path.join(path, 'data','visualizations', 'validated_dashboard.json')

def load_dashboards_from_file():
    try:
        with open(dashboards_json_path, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dashboards_to_file(data):
    with open(dashboards_json_path, 'w') as f:
        json.dump(data, f, indent=2)

dashboards_data = load_dashboards_from_file()


def build_reports_table(data, page=1, page_size=15):

    # Filter active reports
    active_reports = [item for item in data if item.get("archived", "False") == "False"]

    # Pagination calculations
    total = len(active_reports)
    start = (page - 1) * page_size
    end = start + page_size

    paginated_items = active_reports[start:end]

    # Styled header
    table_header = html.Thead(
        html.Tr([
            # html.Th("Report ID"),
            html.Th("Report Name"),
            html.Th("Creator"),
            html.Th("Date Updated"),
            html.Th("Report Type"),
            html.Th("Page Name"),
            html.Th("Actions"),
        ]),
        style={
            "background": "#006401",
            "color": "white",
            "fontWeight": "bold",
            "fontSize": "15px",
            "textAlign": "left",
            "height":"30px"
        }
    )

    # Build rows
    table_rows = []
    for item in paginated_items:
        table_rows.append(
            html.Tr([
                # html.Td(item.get("report_id")),
                html.Td(item.get("report_name")),
                html.Td(item.get("creator")),
                html.Td(item.get("date_updated")),
                html.Td(item.get("kind")),
                html.Td(item.get("page_name")),
                html.Td([
                    html.Button(
                        "",
                        id={"type": "edit-btn", "index": item.get("report_id")},className="report-action-btn edit-btn-svg"    
                    ),
                    html.Button(
                        "Archive",
                        id={"type": "archive-btn", "index": item.get("report_id")},className="report-action-btn archive-btn-svg"
                    ),
                    html.Button(
                        "",
                        id={"type": "download-btn", "index": item.get("report_id")},className="report-action-btn download-btn-svg"
                    ),
                ], style={"display": "flex", "gap": "20px"})
            ])
        )

    table_body = html.Tbody(table_rows)

    return html.Div([
        html.H2("List of MaHIS DataSet Reports", style={'textAlign': 'center'}),
        html.P(
            "These are HMIS dataset reports. To update, click Edit or upload a report template bearing the same page_name (id)",
            style={'textAlign': 'center'}
        ),

        # Table Output
        html.Table(
            [table_header, table_body],
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                "border": "1px solid #ccc"
            }
        ),

        # Pagination controls
        html.Div([
            html.Button("Previous", id="prev-page", n_clicks=0, style={"marginRight": "10px"}),
            html.Button("Next", id="next-page", n_clicks=0),
            html.Span(f"  Page {page}", id="page-label", style={"marginLeft": "15px"}),
            html.Span(f" / { (total // page_size) + (1 if total % page_size else 0) }"),
        ], style={"marginTop": "20px", "textAlign": "center"}),

    ])


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

instructions = html.Div([
    html.H1("Reports Configuration", style={'textAlign': 'center'}),
    html.P("Step 1: Update an excel template as provided on the menu below. Be sure to fill all worksheets", style={'textAlign': 'center'}),
    html.P("Step 2: Upload the worksheet. Dry run to check if the values are consistent with requirements", style={'textAlign': 'center'}),
    html.P("Step 3: To edit or archive, click on the item end and edit or review. The edit will open a popup editing tool with worksheets", style={'textAlign': 'center'}),
])
preview_modal = html.Div([
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
    })
upload_excel_popup_modal = html.Div([
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
    })
upload_dashboard_json_popup_modal = html.Div([
        html.Div([
            html.H3("Upload Json Template", style={'marginBottom': '20px'}),
            
            dcc.Upload(
                id='template-dashboard-file-upload',
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
                accept='.json'
            ),
            
            html.Div(id='upload-dashboard-validation-result', style={'marginBottom': '20px'}),
            html.Div(id='existing-dashboard-report-warning', style={'marginBottom': '20px'}),
            
            html.Div([
                html.Button(
                    "Dry Run",
                    id="dry-dashboard-run-btn",
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
                    id="upload-dashboard-confirm-btn",
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
                    id="upload-dashboard-cancel-btn",
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
    ], id="upload-dashboard-popup", style={
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
    })
upload_prog_reports_json_popup_modal = html.Div([
        html.Div([
            html.H3("Upload Json Template", style={'marginBottom': '20px'}),
            
            dcc.Upload(
                id='template-prog-reports-file-upload',
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
                accept='.json'
            ),
            
            html.Div(id='upload-prog-reports-validation-result', style={'marginBottom': '20px'}),
            html.Div(id='existing-prog-reports-report-warning', style={'marginBottom': '20px'}),
            
            html.Div([
                html.Button(
                    "Dry Run",
                    id="dry-prog-reports-run-btn",
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
                    id="upload-prog-reports-confirm-btn",
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
                    id="upload-prog-reports-cancel-btn",
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
    ], id="upload-prog-reports-popup", style={
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
    })
archive_popup_modal = html.Div([
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
    })
archive_confirmation_modal = html.Div([
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
    })
reports_table = html.Div(id="reports-table-container", style={'maxWidth': '1200px', 'margin': '0 auto'})
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
layout = html.Div(
    style={"display": "flex", "height": "100vh"},
    children=[
        # ---------- LEFT SIDEBAR ----------
        html.Div(id="sidebar",
            style={"width": "300px","background": "#FFFFFF","padding": "20px",
                   "color": "white","display": "flex","flexDirection": "column",
                   "gap": "10px","marginTop":"5px","boxShadow": "8px 0 16px -8px rgba(0,0,0,0.5)","overflow": "visible"},
            children=[
                html.H3("Configurations", style={"textAlign": "center","color":"Black"}),
                
                html.Div([
                    html.Button("Data Set Reports List",id="dataset-reports-btn",n_clicks=0,className="nav-btn"),
                    html.Button("Add XLSX-DataSet Report",id="add-from-template-btn",n_clicks=0,className="nav-btn"),
                    html.Button("Add Dashboard File (Json)",id="add-dashboard-temp-btn",n_clicks=0,className="nav-btn"),
                    html.Button("Add Prog Report File (Json)",id="add-prog-report-temp-btn",n_clicks=0,className="nav-btn"),
                    html.Button("Add dashboard (GUI)",id="add-dashboard",n_clicks=0,className="nav-btn"),
                    html.Button("Download XLSX Template",id="download-sample",n_clicks=0,className="nav-btn"),
                    html.Button("Preview Data",id="preview-data",n_clicks=0,className="nav-btn"),
                    # html.Button("Logout",id="logout-button",n_clicks=0,className="nav-btn"),
                ])
            ],
        ),
        # BODY
        html.Div(
            id="main-content",
            style={"flex": 1, "padding": "30px","background": "#F5F4F4"},
            children=[
                # instructions,
                preview_modal,
                upload_excel_popup_modal,
                upload_dashboard_json_popup_modal,
                upload_prog_reports_json_popup_modal,
                archive_popup_modal,
                archive_confirmation_modal,
                reports_table,
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
                dcc.Download(id="download-xlsx-report"),
                dcc.Store(id="preview-data-store", data=None),  # Add this line

                # Dashboard
                dcc.Store(id='current-dashboard-data', data={}),
                dcc.Store(id='current-dashboard-index', data=-1),
                dcc.Store(id='delete-confirmation', data=False),
                dcc.Interval(
                    id='configurations-interval-update-today',
                    interval=10*60*1000,  # in milliseconds
                    n_intervals=0
                ),
            ],
        ),
    ],
)

# validate admins
@callback(
        [Output('sidebar', 'children'),
         Output('main-content', 'children')],
        [Input('url-params-store', 'data')])
def validate_admin_access(urlparams):
    user_data_path = os.path.join(path, 'data', 'users_data.csv')
    if not os.path.exists(user_data_path):
        user_data = pd.DataFrame(columns=['user_id', 'role'])
    else:
        user_data = pd.read_csv(os.path.join(path, 'data', 'users_data.csv'))
        authorized_users = user_data[user_data['role'] == 'Superuser,Superuser']
    test_admin = pd.DataFrame(columns=['user_id', 'role'], data=[['m3his@dhd', 'reports_admin']])
    user_data = pd.concat([authorized_users, test_admin], ignore_index=True)

    user_info = user_data[user_data['user_id'] == urlparams.get('uuid', [None])[0]]
    if user_info.empty:
        return dash.no_update, html.Div([
            html.H2("Access Denied"),
            html.P("You do not have permission to access this page. Please log in as an administrator.")], 
            style={'textAlign': 'center', 'marginTop': '100px'})
    else:
        return dash.no_update, dash.no_update


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

# excel
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

# json dashboard
@callback(
    [Output("upload-dashboard-popup", "style"),
     Output("template-dashboard-file-upload", "contents"),
     Output("upload-dashboard-validation-result", "children"),
     Output("existing-dashboard-report-warning", "children")],
    [Input("add-dashboard-temp-btn", "n_clicks"),
     Input("upload-dashboard-cancel-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_upload_popup(add_clicks, cancel_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "add-dashboard-temp-btn":
        return {'display': 'flex', 'position': 'fixed', 'top': '0', 'left': '0', 
                'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 
                'justifyContent': 'center', 'alignItems': 'center', 'zIndex': '1000'}, None, "", ""
    elif trigger_id == "upload-dashboard-cancel-btn":
        return {'display': 'none'}, None, "", ""
    
    return dash.no_update
# json prog reports
@callback(
    [Output("upload-prog-reports-popup", "style"),
     Output("template-prog-reports-file-upload", "contents"),
     Output("upload-prog-reports-validation-result", "children"),
     Output("existing-prog-reports-report-warning", "children")],
    [Input("add-prog-report-temp-btn", "n_clicks"),
     Input("upload-prog-reports-cancel-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_upload_popup(add_clicks, cancel_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "add-prog-report-temp-btn":
        return {'display': 'flex', 'position': 'fixed', 'top': '0', 'left': '0', 
                'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 
                'justifyContent': 'center', 'alignItems': 'center', 'zIndex': '1000'}, None, "", ""
    elif trigger_id == "upload-prog-reports-cancel-btn":
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
        
        final_variable_names = []
        for item in variable_names_list:
            if isinstance(item, str):
                if "|" in item:
                    parts = [x.strip() for x in item.split("|")]
                    final_variable_names.extend(parts)
                elif item.startswith("[") and item.endswith("]"):
                    inner = item[1:-1].strip()
                    parts = [x.strip() for x in inner.split(",")]
                    final_variable_names.extend(parts)
                else:
                    final_variable_names.append(item.strip())
            elif isinstance(item, list):
                final_variable_names.extend([str(x).strip() for x in item])
            else:
                final_variable_names.append(str(item).strip())


        # Check if variable names are the same as in the data
        verification_df, nothing = load_preview_data()
        verification_df_columns = verification_df.columns.tolist()

        not_correct = []
        correct = []
        dry_run_warning = []

        for i in final_variable_names:
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
    Output('upload-dashboard-validation-result', 'children',allow_duplicate=True),
    Output('upload-dashboard-confirm-btn', 'disabled',allow_duplicate=True),
    Output('existing-dashboard-report-warning', 'children',allow_duplicate=True),

    Output('template-dashboard-file-upload', 'contents',allow_duplicate=True),

    Input('template-dashboard-file-upload', 'contents'),
    Input('dry-dashboard-run-btn', 'n_clicks'),
    Input('upload-dashboard-confirm-btn', 'n_clicks'),
    Input('upload-dashboard-cancel-btn', 'n_clicks'),

    State('template-dashboard-file-upload', 'filename'),
    State('template-dashboard-file-upload', 'contents'),
    prevent_initial_call=True
)
def process_dashboard_json(uploaded_contents, dry_run_clicks, upload_clicks, cancel_clicks,
                 filename, contents):
    ctx = dash.callback_context

    action = ctx.triggered[0]["prop_id"].split(".")[0]
    if action == "upload-dashboard-cancel-btn":
        return "", True, "", None
    if action == "template-dashboard-file-upload":
        if filename:
            msg = html.Div([
                html.B(f"File selected: {filename}"),
                html.Br(),
                "Please click Dry Run to validate the JSON template."
            ], style={'color': 'blue'})
            return msg, True, "", contents
        else:
            return "Upload a JSON file first.", True, "", contents
    if not contents:
        return "Please upload a JSON file first.", True, "", None

    try:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
    except:
        return "Failed to read file content.", True, "", contents
    if action == "dry-dashboard-run-btn":
        ok, message = validate_dashboard_json(decoded)
        color = "green" if ok else "red"
        return html.Div(message, style={'color': color}), not ok, "", contents
    if action == "upload-dashboard-confirm-btn":
        result = upload_dashboard_json(contents)
        return html.Div(result, style={'color': 'green'}), True, "", contents
    
@callback(
    Output('upload-prog-reports-validation-result', 'children',allow_duplicate=True),
    Output('upload-prog-reports-confirm-btn', 'disabled',allow_duplicate=True),
    Output('existing-prog-reports-report-warning', 'children',allow_duplicate=True),

    Output('template-prog-reports-file-upload', 'contents',allow_duplicate=True),

    Input('template-prog-reports-file-upload', 'contents'),
    Input('dry-prog-reports-run-btn', 'n_clicks'),
    Input('upload-prog-reports-confirm-btn', 'n_clicks'),
    Input('upload-prog-reports-cancel-btn', 'n_clicks'),

    State('template-prog-reports-file-upload', 'filename'),
    State('template-prog-reports-file-upload', 'contents'),
    prevent_initial_call=True
)
def process_prog_dashboard_json(uploaded_contents, dry_run_clicks, upload_clicks, cancel_clicks,
                 filename, contents):
    ctx = dash.callback_context

    action = ctx.triggered[0]["prop_id"].split(".")[0]
    if action == "upload-prog-reports-cancel-btn":
        return "", True, "", None
    if action == "template-prog-reports-file-upload":
        if filename:
            msg = html.Div([
                html.B(f"File selected: {filename}"),
                html.Br(),
                "Please click Dry Run to validate the JSON template."
            ], style={'color': 'blue'})
            return msg, True, "", contents
        else:
            return "Upload a JSON file first.", True, "", contents
    if not contents:
        return "Please upload a JSON file first.", True, "", None

    try:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
    except:
        return "Failed to read file content.", True, "", contents
    if action == "dry-prog-reports-run-btn":
        ok, message = validate_prog_reports_json(decoded)
        color = "green" if ok else "red"
        return html.Div(message, style={'color': color}), not ok, "", contents
    if action == "upload-prog-reports-confirm-btn":
        result = upload_prog_reports_json(contents)
        return html.Div(result, style={'color': 'green'}), True, "", contents

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
        # Determine which edit button was clicked
        button_index = None
        for i, count in enumerate(edit_clicks):
            if count and count > 0:
                button_index = i
                break

        if button_index is None:
            return dash.no_update

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
        # if button_index == 0:
        #     return dash.no_update
        
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
     Output("download-xlsx-report", "data"),
     Input({"type": "download-btn", "index": dash.ALL}, "n_clicks"),
     State({"type": "download-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True
)
def download_xlsx_report(download_clicks,download_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if "download-btn" in trigger_id:
        # Find which archive button was clicked
        button_index = None
        for i, clicks in enumerate(download_clicks):
            if clicks and clicks > 0:  # Only proceed if button was actually clicked
                button_index = i
                break
        
        if button_index is None:
            return dash.no_update
        
        # Get the report_id from the button that was clicked
        report_id = download_ids[button_index]['index']
        
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
        return dcc.send_file(os.path.join("data","uploads",f"{current_report.get('page_name')}.xlsx"))
    # return 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + encode_excel_for_download(current_report.get("page_name")), filename=f"{current_report.get('page_name')}.xlsx"


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
    [Output("modal-backdrop", "style"),
     Output("modal-content", "style"),
     Output("dashboard-selector", "value", allow_duplicate=True),
     Output("dashboard-selector", "data"),
     Output("report-id-input", "value"),
     Output("report-name-input", "value"),
     Output("date-created-input", "value"),
     Output("counts-container", "children"),
     Output("sections-container", "children")],
    [Input("add-dashboard", "n_clicks"),
     Input("cancel-btn", "n_clicks"),
     Input("save-btn", "n_clicks"),
     Input("configurations-interval-update-today", "n_intervals")],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, cancel_clicks, save_clicks, n_intervals):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == "add-dashboard" and open_clicks > 0:
        # Load current dashboards from file
        dashboards_data = load_dashboards_from_file()
        
        # Update dropdown options
        options = [{"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
                   "value": i} for i, d in enumerate(dashboards_data)] + \
                  [{"label": "➕ Create New Dashboard", "value": "new"}]
        
        
        # Return empty form for new dashboard
        return (
            {"display": "block"}, 
            {"display": "block"},
            "new",  # Select "new" in dropdown
            options,
            f"report_{uuid.uuid4().hex[:8]}",  # Auto-generate ID
            "New Dashboard",  # Default name
            datetime.now().strftime("%Y-%m-%d"),  # Current date
            [],  # Empty counts
            []   # Empty sections
        )
    
    elif trigger == "cancel-btn":
        # Just close the modal
        return {"display": "none"}, {"display": "none"}, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update
    
    elif trigger == "save-btn":
        # Just close the modal
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update
    
    return dash.no_update


@callback(
    [Output("report-id-input", "value",allow_duplicate=True),
     Output("report-name-input", "value",allow_duplicate=True),
     Output("date-created-input", "value",allow_duplicate=True),
     Output("counts-container", "children",allow_duplicate=True),
     Output("sections-container", "children",allow_duplicate=True)],
    [Input("dashboard-selector", "value"),
     Input("add-count-btn", "n_clicks"),
     Input("add-section-btn", "n_clicks"),
     Input({"type": "remove-count", "index": dash.ALL}, "n_clicks"),
     Input({"type": "remove-section", "index": dash.ALL}, "n_clicks"),
     Input({"type": "add-chart-btn", "index": dash.ALL}, "n_clicks"),
     Input({"type": "remove-chart", "section": dash.ALL, "index": dash.ALL}, "n_clicks")],
    [State("dashboard-selector", "value"),
     State("counts-container", "children"),
     State("sections-container", "children")],
    prevent_initial_call=True
)
def update_dashboard_form(selector_value, add_count_clicks, add_section_clicks, 
                         remove_count_clicks, remove_section_clicks, 
                         add_chart_clicks, remove_chart_clicks,
                         current_selector, counts_children, sections_children):
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle dashboard selection - READ DIRECTLY FROM FILE
    if trigger_id == "dashboard-selector":
        dashboards_data = load_dashboards_from_file()
        
        if selector_value == "new":
            # Create new dashboard template
            return (
                f"report_{uuid.uuid4().hex[:8]}",  # Auto-generate ID
                "New Dashboard",  # Default name
                datetime.now().strftime("%Y-%m-%d"),  # Current date
                [],  # Empty counts
                []   # Empty sections
            )
        
        elif isinstance(selector_value, int) and 0 <= selector_value < len(dashboards_data):
            dashboard = dashboards_data[selector_value]
            counts = dashboard.get('visualization_types', {}).get('counts', [])
            sections = dashboard.get('visualization_types', {}).get('charts', {}).get('sections', [])
            
            counts_children = [create_count_item(count, i) for i, count in enumerate(counts)]
            sections_children = [create_section(section, i) for i, section in enumerate(sections)]
            
            return (
                dashboard.get("report_id", ""),
                dashboard.get("report_name", ""),
                dashboard.get("date_created", ""),
                counts_children,
                sections_children
            )
    
    # Handle UI interactions (these will be temporary until saved)
    elif trigger_id == "add-count-btn":
        new_count_index = len(counts_children) if counts_children else 0
        new_count = create_count_item(index=new_count_index)
        if counts_children is None:
            counts_children = [new_count]
        else:
            counts_children = counts_children + [new_count]
        return dash.no_update, dash.no_update, dash.no_update, counts_children, dash.no_update
    
    elif trigger_id == "add-section-btn":
        new_section_index = len(sections_children) if sections_children else 0
        new_section = create_section(index=new_section_index)
        if sections_children is None:
            sections_children = [new_section]
        else:
            sections_children = sections_children + [new_section]
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, sections_children
    
    # Handle removal actions
    elif "remove-count" in trigger_id:
        # Parse the index to remove
        trigger_dict = json.loads(trigger_id.replace("'", '"'))
        index_to_remove = trigger_dict['index']
        
        if counts_children and len(counts_children) > index_to_remove:
            # Remove the count and re-index remaining ones
            new_counts_children = []
            for i, count in enumerate(counts_children):
                if i != index_to_remove:
                    # Recreate with new index
                    new_count = create_count_item(index=len(new_counts_children))
                    new_counts_children.append(new_count)
            return dash.no_update, dash.no_update, dash.no_update, new_counts_children, dash.no_update
    
    # Handle removing sections
    elif "remove-section" in trigger_id:
        # Parse the index to remove
        trigger_dict = json.loads(trigger_id.replace("'", '"'))
        index_to_remove = trigger_dict['index']
        
        if sections_children and len(sections_children) > index_to_remove:
            # Remove the section and re-index remaining ones
            new_sections_children = []
            for i, section in enumerate(sections_children):
                if i != index_to_remove:
                    # Recreate with new index
                    new_section = create_section(index=len(new_sections_children))
                    new_sections_children.append(new_section)
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    # Handle adding charts to sections
    elif "add-chart-btn" in trigger_id:
        # Parse the section index
        trigger_dict = json.loads(trigger_id.replace("'", '"'))
        section_index = trigger_dict['index']
        
        if sections_children and len(sections_children) > section_index:
            # Get the current section
            section = sections_children[section_index]
            
            try:
                # Extract current charts from the section structure
                current_charts = []
                if isinstance(section, dict) and 'props' in section:
                    # Navigate to the charts container
                    section_body = section['props']['children'][1]  # card-body
                    if 'props' in section_body and 'children' in section_body['props']:
                        body_children = section_body['props']['children']
                        if len(body_children) > 1:
                            charts_container = body_children[1]  # charts-container
                            if 'props' in charts_container and 'children' in charts_container['props']:
                                current_charts = charts_container['props']['children'] or []
                
                # Add new chart
                new_chart_index = len(current_charts)
                new_chart = create_chart_item(section_index=section_index, chart_index=new_chart_index)
                updated_charts = current_charts + [new_chart]
                
                # Recreate the section with updated charts
                updated_section = create_section_with_charts(section, updated_charts, section_index)
                
                # Update the sections list
                new_sections_children = sections_children.copy()
                new_sections_children[section_index] = updated_section
                
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
                
            except (KeyError, IndexError, TypeError) as e:
                # If structure is unexpected, recreate section from scratch
                print(f"Error parsing section structure: {e}")
                # Fallback: create a new section with one chart
                new_section = create_section(index=section_index)
                new_sections_children = sections_children.copy()
                new_sections_children[section_index] = new_section
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    # Handle removing charts from sections
    elif "remove-chart" in trigger_id:
        # Parse the section and chart indices
        trigger_dict = json.loads(trigger_id.replace("'", '"'))
        section_index = trigger_dict['section']
        chart_index_to_remove = trigger_dict['index']
        
        if sections_children and len(sections_children) > section_index:
            # Get the current section
            section = sections_children[section_index]
            
            try:
                # Extract current charts from the section structure
                current_charts = []
                if isinstance(section, dict) and 'props' in section:
                    # Navigate to the charts container
                    section_body = section['props']['children'][1]  # card-body
                    if 'props' in section_body and 'children' in section_body['props']:
                        body_children = section_body['props']['children']
                        if len(body_children) > 1:
                            charts_container = body_children[1]  # charts-container
                            if 'props' in charts_container and 'children' in charts_container['props']:
                                current_charts = charts_container['props']['children'] or []
                
                if current_charts and len(current_charts) > chart_index_to_remove:
                    # Remove the specified chart and re-index
                    updated_charts = []
                    for j, chart in enumerate(current_charts):
                        if j != chart_index_to_remove:
                            # Recreate chart with new index
                            new_chart = create_chart_item(
                                section_index=section_index, 
                                chart_index=len(updated_charts)
                            )
                            updated_charts.append(new_chart)
                    
                    # Recreate the section with updated charts
                    updated_section = create_section_with_charts(section, updated_charts, section_index)
                    
                    # Update the sections list
                    new_sections_children = sections_children.copy()
                    new_sections_children[section_index] = updated_section
                    
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
                    
            except (KeyError, IndexError, TypeError) as e:
                # If structure is unexpected, recreate section from scratch
                print(f"Error parsing section structure: {e}")
                # Fallback: create a new empty section
                new_section = create_section(index=section_index)
                new_sections_children = sections_children.copy()
                new_sections_children[section_index] = new_section
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_sections_children
    
    # Return current state (for triggers we don't handle)
    return dash.no_update, dash.no_update, dash.no_update, counts_children or [], sections_children or []


def create_section_with_charts(section, charts, section_index):
    """Recreate a section with updated charts"""
    # Extract the section name from the existing section
    section_name = ""
    try:
        if isinstance(section, dict) and 'props' in section:
            section_header = section['props']['children'][0]  # card-header
            if 'props' in section_header and 'children' in section_header['props']:
                header_children = section_header['props']['children']
                if len(header_children) > 0:
                    section_header_content = header_children[0]  # section-header
                    if 'props' in section_header_content and 'children' in section_header_content['props']:
                        header_content_children = section_header_content['props']['children']
                        if len(header_content_children) > 0:
                            section_name_input = header_content_children[0]  # section-col with input
                            if 'props' in section_name_input and 'children' in section_name_input['props']:
                                name_input_children = section_name_input['props']['children']
                                if len(name_input_children) > 1:
                                    input_field = name_input_children[1]  # dcc.Input
                                    if 'props' in input_field and 'value' in input_field['props']:
                                        section_name = input_field['props']['value']
    except (KeyError, IndexError, TypeError):
        section_name = f"Section {section_index + 1}"
    
    # Create new section
    return html.Div(className="section-item", children=[
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
    [Output("dashboard-selector", "options", allow_duplicate=True),
     Output("modal-backdrop", "style", allow_duplicate=True),
     Output("modal-content", "style", allow_duplicate=True)],
    [Input("save-btn", "n_clicks")],
    [State("dashboard-selector", "value"),  # Get selected dashboard from dropdown
     State("report-name-input", "value"),
     State("report-id-input", "value"),
     State("date-created-input", "value"),
     # Count states
     State({"type": "count-id", "index": dash.ALL}, "value"),
     State({"type": "count-name", "index": dash.ALL}, "value"),
     State({"type": "count-unique", "index": dash.ALL}, "value"),
     State({"type": "count-var1", "index": dash.ALL}, "value"),
     State({"type": "count-val1", "index": dash.ALL}, "value"),
     State({"type": "count-var2", "index": dash.ALL}, "value"),
     State({"type": "count-val2", "index": dash.ALL}, "value"),
     State({"type": "count-var3", "index": dash.ALL}, "value"),
     State({"type": "count-val3", "index": dash.ALL}, "value"),
     State({"type": "count-var4", "index": dash.ALL}, "value"),
     State({"type": "count-val4", "index": dash.ALL}, "value"),

     State({"type": "count-var5", "index": dash.ALL}, "value"),
     State({"type": "count-val5", "index": dash.ALL}, "value"),
     State({"type": "count-var6", "index": dash.ALL}, "value"),
     State({"type": "count-val6", "index": dash.ALL}, "value"),
     State({"type": "count-var7", "index": dash.ALL}, "value"),
     State({"type": "count-val7", "index": dash.ALL}, "value"),
     State({"type": "count-var8", "index": dash.ALL}, "value"),
     State({"type": "count-val8", "index": dash.ALL}, "value"),
     # Section states
     State({"type": "section-name", "index": dash.ALL}, "value"),
     # Chart states - IMPORTANT: We need to get the actual section and chart indices
     State({"type": "chart-id", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-name", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-type", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-title", "section": dash.ALL, "index": dash.ALL}, "value"),
     # Chart field states - include the IDs to track which chart they belong to
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
     State({"type": "chart-duration_default", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-colormap", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col1", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val1", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col2", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val2", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col3", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val3", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col4", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val4", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_col5", "section": dash.ALL, "index": dash.ALL}, "value"),
     State({"type": "chart-filter_val5", "section": dash.ALL, "index": dash.ALL}, "value")],
    prevent_initial_call=True
)
def save_dashboard(save_clicks, selector_value, report_name, report_id, date_created, 
                  count_ids, count_names, count_uniques,
                  count_vars1, count_vals1, count_vars2, count_vals2, count_vars3, count_vals3, count_vars4, count_vals4,
                  count_vars5, count_vals5, count_vars6, count_vals6, count_vars7, count_vals7, count_vars8, count_vals8,
                  section_names,
                  chart_ids, chart_names, chart_types, chart_titles,
                  chart_date_cols, chart_y_cols, chart_x_titles, chart_y_titles,
                  chart_unique_columns, chart_legend_titles, chart_colors,
                  chart_label_cols, chart_value_cols, chart_top_ns,
                  chart_names_cols, chart_values_cols, chart_x_cols,
                  chart_age_cols, chart_gender_cols, chart_bin_sizes,
                  chart_index_col1s, chart_columns, chart_aggfuncs,
                  chart_duration_defaults, chart_colormaps,
                  chart_filter_col1s, chart_filter_val1s, chart_filter_col2s, chart_filter_val2s,
                  chart_filter_col3s, chart_filter_val3s, chart_filter_col4s, chart_filter_val4s,
                  chart_filter_col5s, chart_filter_val5s):
    
    if save_clicks and save_clicks > 0:
        if not report_name:
            # Show error - you might want to add an error output
            return dash.no_update, dash.no_update, dash.no_update
        # Load current data from file
        dashboards_data = load_dashboards_from_file()
        
        # 1. Build counts data from UI state
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
                    if i < len(count_vars1) and count_vars1[i]:
                        count_data["filters"]["variable1"] = count_vars1[i]
                    if i < len(count_vals1) and count_vals1[i]:
                        count_data["filters"]["value1"] = count_vals1[i]
                    
                    if i < len(count_vars2) and count_vars2[i]:
                        count_data["filters"]["variable2"] = count_vars2[i]
                    if i < len(count_vals2) and count_vals2[i]:
                        count_data["filters"]["value2"] = count_vals2[i]
                    
                    if i < len(count_vars3) and count_vars3[i]:
                        count_data["filters"]["variable3"] = count_vars3[i]
                    if i < len(count_vals3) and count_vals3[i]:
                        count_data["filters"]["value3"] = count_vals3[i]

                    if i < len(count_vars4) and count_vars4[i]:
                        count_data["filters"]["variable4"] = count_vars4[i]
                    if i < len(count_vals4) and count_vals4[i]:
                        count_data["filters"]["value4"] = count_vals4[i]
                    if i < len(count_vars5) and count_vars5[i]:
                        count_data["filters"]["variable5"] = count_vars5[i]
                    if i < len(count_vals5) and count_vals5[i]:
                        count_data["filters"]["value5"] = count_vals5[i]
                    if i < len(count_vars6) and count_vars6[i]:
                        count_data["filters"]["variable6"] = count_vars6[i]
                    if i < len(count_vals6) and count_vals6[i]:
                        count_data["filters"]["value6"] = count_vals6[i]
                    if i < len(count_vars7) and count_vars7[i]:
                        count_data["filters"]["variable7"] = count_vars7[i]
                    if i < len(count_vals7) and count_vals7[i]:
                        count_data["filters"]["value7"] = count_vals7[i]
                    if i < len(count_vars8) and count_vars8[i]:
                        count_data["filters"]["variable8"] = count_vars8[i]
                    if i < len(count_vals8) and count_vals8[i]:
                        count_data["filters"]["value8"] = count_vals8[i]
                    
                    counts_data.append(count_data)
        
        # 2. Build sections data - FIXED VERSION
        sections_data = []
        
        # First, organize charts by their actual section indices
        # We need to extract section and chart indices from the pattern IDs
        charts_by_section = {}
        
        # Process all charts with their section assignments
        for i in range(len(chart_ids)):
            # Get the actual section and chart index from the pattern IDs
            # This assumes the IDs follow the pattern from create_chart_item
            section_idx = None
            chart_idx = None
            
            # Try to extract from the chart_id if it contains the info
            # Or we need to track this differently - let's use a different approach
            
            # Since we can't easily extract from IDs, we'll use a different strategy
            # We'll create charts first, then assign them to sections based on index
            
            if chart_ids[i] and chart_names[i] and chart_types[i]:
                chart_data = {
                    "id": chart_ids[i],
                    "name": chart_names[i],
                    "type": chart_types[i],
                    "filters": {
                        "measure": "chart",
                        "unique": "any",
                        "duration_default": "any"
                    }
                }
                
                # Add title if available
                if i < len(chart_titles) and chart_titles[i]:
                    chart_data["filters"]["title"] = chart_titles[i]
                
                # Add duration_default
                if i < len(chart_duration_defaults) and chart_duration_defaults[i]:
                    chart_data["filters"]["duration_default"] = chart_duration_defaults[i]
                
                # Add chart type specific fields
                chart_type = chart_types[i]

                # Access values when list is less than i
                def get_safe_value(lst, default=None, index=i):
                    """
                    Pop and return the first item from a list.
                    If the list is empty or None, return default.
                    """
                    try:
                        if index < len(lst):
                            return lst[index]
                        else:
                            return lst.pop(0)
                    except (IndexError, TypeError):
                        return default

                # Update all chart types with safe access
                if chart_type == "Line":
                    chart_data["filters"]["date_col"] = get_safe_value(chart_date_cols, i)
                    chart_data["filters"]["y_col"] = get_safe_value(chart_y_cols, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["x_title"] = get_safe_value(chart_x_titles, i)
                    chart_data["filters"]["y_title"] = get_safe_value(chart_y_titles, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["legend_title"] = get_safe_value(chart_legend_titles, i)
                    chart_data["filters"]["color"] = get_safe_value(chart_colors, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)


                elif chart_type == "Bar":
                    chart_data["filters"]["label_col"] = get_safe_value(chart_label_cols, i)
                    chart_data["filters"]["value_col"] = get_safe_value(chart_value_cols, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["x_title"] = get_safe_value(chart_x_titles, i)
                    chart_data["filters"]["y_title"] = get_safe_value(chart_y_titles, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["top_n"] = get_safe_value(chart_top_ns, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)

                elif chart_type == "Pie":
                    chart_data["filters"]["names_col"] = get_safe_value(chart_names_cols, i)
                    chart_data["filters"]["values_col"] = get_safe_value(chart_values_cols, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["colormap"] = get_safe_value(chart_colormaps, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)

                elif chart_type == "Column":
                    chart_data["filters"]["x_col"] = get_safe_value(chart_x_cols, i)
                    chart_data["filters"]["y_col"] = get_safe_value(chart_y_cols, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["x_title"] = get_safe_value(chart_x_titles, i)
                    chart_data["filters"]["y_title"] = get_safe_value(chart_y_titles, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["legend_title"] = get_safe_value(chart_legend_titles, i)
                    chart_data["filters"]["color"] = get_safe_value(chart_colors, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)

                elif chart_type == "Histogram":
                    chart_data["filters"]["age_col"] = get_safe_value(chart_age_cols, i)
                    chart_data["filters"]["gender_col"] = get_safe_value(chart_gender_cols, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["x_title"] = get_safe_value(chart_x_cols, i)
                    chart_data["filters"]["y_title"] = get_safe_value(chart_y_cols, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["bin_size"] = get_safe_value(chart_bin_sizes, i)
                    chart_data["filters"]["color"] = get_safe_value(chart_colors, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)

                elif chart_type == "PivotTable":
                    chart_data["filters"]["index_col1"] = get_safe_value(chart_index_col1s, i)
                    chart_data["filters"]["columns"] = get_safe_value(chart_columns, i)
                    chart_data["filters"]["title"] = get_safe_value(chart_titles, i)
                    chart_data["filters"]["x_title"] = get_safe_value(chart_x_cols, i)
                    chart_data["filters"]["y_title"] = get_safe_value(chart_y_cols, i)
                    chart_data["filters"]["unique_column"] = get_safe_value(chart_unique_columns, i)
                    chart_data["filters"]["values_col"] = get_safe_value(chart_values_cols, i)
                    chart_data["filters"]["aggfunc"] = get_safe_value(chart_aggfuncs, i)
                    chart_data["filters"]["filter_col1"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val1"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col2"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val2"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col3"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val3"] = get_safe_value(chart_filter_val1s, i)
                    chart_data["filters"]["filter_col4"] = get_safe_value(chart_filter_col2s, i)
                    chart_data["filters"]["filter_val4"] = get_safe_value(chart_filter_val2s, i)
                    chart_data["filters"]["filter_col5"] = get_safe_value(chart_filter_col1s, i)
                    chart_data["filters"]["filter_val5"] = get_safe_value(chart_filter_val1s, i)
                

                total_charts_processed = i
                
                # Distribute charts to sections based on the number of sections
                if section_names:
                    # Simple distribution: assign charts in order to sections
                    section_idx = total_charts_processed % len(section_names)
                    
                    if section_idx not in charts_by_section:
                        charts_by_section[section_idx] = []
                    charts_by_section[section_idx].append(chart_data)
        
        # 3. Create sections with their assigned charts
        for section_idx, section_name in enumerate(section_names):
            if section_name:
                section_charts = charts_by_section.get(section_idx, [])
                section_data = {
                    "section_name": section_name,
                    "items": section_charts
                }
                sections_data.append(section_data)
        
        # 4. Create complete dashboard structure
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
        
        # 5. Update or add to dashboards data
        if selector_value == "new":  # New dashboard
            dashboards_data.append(dashboard_structure)
        elif isinstance(selector_value, int) and 0 <= selector_value < len(dashboards_data):
            # Update existing dashboard
            dashboards_data[selector_value] = dashboard_structure
        else:  # Invalid selector, add as new
            dashboards_data.append(dashboard_structure)
        
        # 6. Save to file
        try:
            save_dashboards_to_file(dashboards_data)
        except Exception as e:
            print(f"Error saving dashboard: {e}")
            # You might want to show an error message to the user
        
        # 7. Update dropdown options
        options = [
            {"label": f"📋 {d.get('report_name', 'Unnamed')} (ID: {d.get('report_id', '?')})", 
             "value": idx} 
            for idx, d in enumerate(dashboards_data)
        ] + [{"label": "➕ Create New Dashboard", "value": "new"}]
        
        # 8. Close modal and return updated options
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
                with open(dashboards_json_path, 'w') as f:
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
