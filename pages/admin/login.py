import dash
from dash import html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/admin/login", title="Admin Login")

layout = html.Div([
    dcc.Location(id='url-login', refresh=True),
    html.Div([
        html.H2("Admin - Reports Configuration", style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        dcc.Input(
            id="login-username",
            type="text",
            placeholder="Username",
            style={
                'width': '100%', 
                'padding': '10px',
                'marginBottom': '15px',
                'border': '1px solid #ddd',
                'borderRadius': '5px',
                'fontSize': '16px'
            }
        ),
        
        dcc.Input(
            id="login-password",
            type="password",
            placeholder="Password",
            style={
                'width': '100%', 
                'padding': '10px',
                'marginBottom': '15px',
                'border': '1px solid #ddd',
                'borderRadius': '5px',
                'fontSize': '16px'
            }
        ),
        
        html.Button(
            "Login", 
            id="login-button", 
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#006401',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'fontSize': '16px',
                'cursor': 'pointer'
            }
        ),
        
        html.Div(
            id="login-message", 
            style={
                'marginTop': '15px', 
                'textAlign': 'center',
                'minHeight': '20px'
            }
        )
        
    ], style={
        'maxWidth': '400px',
        'margin': '100px auto',
        'padding': '30px',
        'border': '1px solid #ddd',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'backgroundColor': 'white'
    })
])

@callback(
    [Output('url-login', 'pathname'),
     Output('login-message', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value')]
)
def login_user(n_clicks, username, password):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    
    # List of user dictionaries - easier to manage
    valid_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "user", "password": "password123"}
    ]
    
    if not username or not password:
        return dash.no_update, html.Div("Please enter both username and password", 
                                      style={'color': 'red'})
    
    # Check if any user matches both username and password
    for user in valid_users:
        if user["username"] == username and user["password"] == password:
            n_clicks = 0
            return "/admin/configurations", html.Div("Login successful!", style={'color': 'green'})
    
    return dash.no_update, html.Div("Invalid username or password", 
                                  style={'color': 'red'})

@callback(
    [Output('login-username', 'value'),
     Output('login-password', 'value')],
    Input('url-login', 'pathname'),
    prevent_initial_call=True
)
def clear_inputs_on_navigation(pathname):
    if pathname == "/admin/configurations":
        return "", ""  # Clear both inputs
    raise PreventUpdate