import dash
from dash import html, dcc, Input, Output, callback

dash.register_page(__name__, path="/nav_drawer", title="Admin Dashboard")

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
    }),
upload_popup_modal = html.Div([
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
    }),
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

layout = html.Div(
    style={"display": "flex", "height": "100vh"},
    children=[
        # ---------- LEFT SIDEBAR ----------
        html.Div(
            style={"width": "300px","background": "#FFFFFF","padding": "20px","color": "white","display": "flex","flexDirection": "column","gap": "10px","marginTop":"5px"},
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
                    html.Button("Logout",id="logout-button",n_clicks=0,className="nav-btn"),
                ])
            ],
        ),
        # BODY
        html.Div(
            id="main-content",
            style={"flex": 1, "padding": "30px"},
            children=[
                html.Div(id="output")
            ],
        ),
    ],
)

# ---------- CALLBACK TO UPDATE MAIN AREA ----------
@callback(
    [Output("output", "children")],
    [Input("dataset-reports-btn", "n_clicks"),
     Input("add-from-template-btn", "n_clicks"),
    Input("add-dashboard-temp-btn", "n_clicks"),
    Input("add-prog-report-temp-btn", "n_clicks"),
    Input("add-dashboard", "n_clicks"),
    Input("download-sample", "n_clicks"),
    Input("preview-data", "n_clicks"),
    Input("logout-button", "n_clicks")],
)
def update_page(dset_list,addxlsx_temp,add_dashboard,add_prog,add_dash_gui,download,preview,logout):
    ctx = dash.callback_context

    if not ctx.triggered:
        return [instructions]

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "dataset-reports-btn":
        return ""
    elif button_id == "btn-reports":
        return "Reports",
    elif button_id == "btn-analytics":
        return "Analytics",
    elif button_id == "btn-settings":
        return "Settings"

    return "Welcome"
