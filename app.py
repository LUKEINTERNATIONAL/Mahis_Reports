import dash
from dash import html, dcc, page_container, page_registry, Output, Input, State, callback
import urllib.parse
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate

# print(list(load_stored_data())) # Load the data to ensure it's available
# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# Define the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='url-params-store'),
    html.Nav([
        html.Ul([
            html.Li(html.A("Dashboard", href="/home", className="nav-link")),
            html.Li([
                html.A("OPD Reports", id="opd-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("HMIS 15", href="/hmis15", className="submenu-link")),
                    html.Li(html.A("Malaria", href="/malaria_report", className="submenu-link")),
                    html.Li(html.A("LMIS", href="/lmis", className="submenu-link")),
                ], id="opd-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            html.Li([
                html.A("IDSR Reports", id="idsr-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("IDSR Weekly", href="/idsr_weekly", className="submenu-link")),
                    html.Li(html.A("IDSR Monthly", href="/idsr_monthly", className="submenu-link")),
                ], id="idsr-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            html.Li(html.A("NCD Report", href="/hmis15", className="nav-link")),
            html.Li(html.A("EPI Report", href="/hmis15", className="nav-link")),
        ], className="nav-list")
    ], className="navbar"),
    page_container,
    
], style={ 'margin': '20px', 'fontFamily': 'Arial, sans-serif'})

@app.callback(
    [Output("opd-reports-submenu", "className"),
     Output("opd-reports-link", "className"),
     Output("idsr-reports-submenu", "className"),
     Output("idsr-reports-link", "className"),
     ],
    [Input("opd-reports-link", "n_clicks"),
     Input("idsr-reports-link", "n_clicks"),
     ],
    [State("opd-reports-submenu", "className"),
     State("opd-reports-link", "className"),
     State("idsr-reports-submenu", "className"),
     State("idsr-reports-link", "className")
     ],
)

def toggle_submenu(opd_clicks, idsr_clicks, 
                  opd_submenu_class, opd_link_class,
                  idsr_submenu_class, idsr_link_class):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "opd-reports-link":
        if opd_clicks and opd_clicks > 0:
            if "show" in opd_submenu_class:
                return "submenu", opd_link_class.replace(" show-submenu", ""), dash.no_update, dash.no_update
            else:
                return "submenu show", opd_link_class + " show-submenu", dash.no_update, dash.no_update
    
    elif triggered_id == "idsr-reports-link":
        if idsr_clicks and idsr_clicks > 0:
            if "show" in idsr_submenu_class:
                return dash.no_update, dash.no_update, "submenu", idsr_link_class.replace(" show-submenu", "")
            else:
                return dash.no_update, dash.no_update, "submenu show", idsr_link_class + " show-submenu"
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to extract and store URL parameters
@callback(
    Output('url-params-store', 'data'),
    Input('url', 'href')
)
def store_url_params(href):
    if not href:
        raise PreventUpdate
    parsed_url = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed_url.query)
    return {
        'location': params.get('Location', [None])[0]  # Get first 'location' or None
    }

@app.callback(
    Output('url', 'pathname'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def redirect_to_home(pathname):
    if pathname == "/":
        return "/home"
    return pathname

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False,)