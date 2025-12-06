import dash
from dash import html, dcc, page_container, page_registry, Output, Input, State, callback
import urllib.parse
import plotly.express as px
import pandas as pd
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
    
    # Fix: Use lowercase 'location' instead of 'Location'
    location_param = params.get('Location', [None])[0]
    
    return location_param

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
def update_nav_links(location):
    query = f"?Location={location}" if location else ""
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

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True,)