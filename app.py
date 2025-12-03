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
            # html.Li([
            #     html.A("Dashboards", id="dashboards-link", href="#", className="nav-link", n_clicks=0),
            #     html.Ul([
            #         html.Li(html.A("OPD", href=f"{pathname_prefix}dashboard_opd", className="submenu-link", id="opd-dashboard-link")),
            #         html.Li(html.A("NCD", href=f"{pathname_prefix}dashboard_ncd", className="submenu-link", id="ncd-dashboard-link")),
            #         html.Li(html.A("HIV", href=f"{pathname_prefix}dashboard_hiv", className="submenu-link", id="hiv-dashboard-link")),
            #         html.Li(html.A("EPI", href=f"{pathname_prefix}dashboard_epi", className="submenu-link", id="epi-dashboard-link")),
            #         html.Li(html.A("Advanced HIV Disease", href=f"{pathname_prefix}dashboard_adv_hiv", className="submenu-link", id="adv-hiv-dashboard-link")),
            #     ], id="dashboards-submenu", className="submenu")
            # ], className="nav-item has-submenu"),
            html.Li(html.A("DataSet Reports", href=f"{pathname_prefix}reports", className="nav-link",id="reports-link")),
            html.Li(html.A("Configure Reports", href=f"{pathname_prefix}login", className="nav-link",id="admin-link")),
            html.Div("Last updated: Today", style={"color":"grey","font-size":"0.9rem","margin-top":"5px","font-style":"italic"}, id='last_updated')
        ], className="nav-list")
    ], className="navbar"),
    page_container,
    
], style={ 'margin': '20px', 'fontFamily': 'Arial, sans-serif'})

# @app.callback(
#     [
#      Output("dashboards-submenu", "className"),
#      Output("dashboards-link", "className"),
#      ],
#     [
#      Input("dashboards-link", "n_clicks"),
#      ],
#     [
#      State("dashboards-submenu", "className"),
#      State("dashboards-link", "className"),
#      ],
# )
# def toggle_submenu(n_clicks, dashboards_submenu_class, dashboards_link_class):
#     ctx = dash.callback_context
    
#     if not ctx.triggered:
#         return dashboards_submenu_class, dashboards_link_class
    
#     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     if triggered_id == "dashboards-link":
#         if "show" in dashboards_submenu_class:
#             # Hide submenu
#             return "submenu", dashboards_link_class.replace(" show-submenu", "")
#         else:
#             # Show submenu
#             return "submenu show", dashboards_link_class + " show-submenu"
    
#     return dashboards_submenu_class, dashboards_link_class

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
     Output('reports-link', 'href'),
    #  Output('ncd-dashboard-link', 'href'),
    #  Output('opd-dashboard-link', 'href'),
    #  Output('epi-dashboard-link', 'href'),
    #  Output('hiv-dashboard-link', 'href'),
    #  Output('adv-hiv-dashboard-link', 'href'),
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
        f"{pathname_prefix}reports{query}",
        # f"{pathname_prefix}dashboard_ncd{query}",
        # f"{pathname_prefix}dashboard_opd{query}",
        # f"{pathname_prefix}dashboard_epi{query}",
        # f"{pathname_prefix}dashboard_hiv{query}",
        # f"{pathname_prefix}dashboard_adv_hiv{query}",
        f"{pathname_prefix}login{query}",
        f"Last updated on: {last_updated}"
    )

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True,)