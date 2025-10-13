import dash
from dash import html, dcc, page_container, page_registry, Output, Input, State, callback
import urllib.parse
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
from config import PREFIX_NAME

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
            html.Li(html.A("Home", href=f"{pathname_prefix}home", className="nav-link",id="home-link")),
            html.Li([
                html.A("Dashboards", id="dashboards-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("OPD", href=f"{pathname_prefix}dashboard_opd", className="submenu-link", id="opd-dashboard-link")),
                    html.Li(html.A("NCD", href=f"{pathname_prefix}dashboard_ncd", className="submenu-link", id="ncd-dashboard-link")),
                    html.Li(html.A("HIV", href=f"{pathname_prefix}dashboard_hiv", className="submenu-link", id="hiv-dashboard-link")),
                    html.Li(html.A("EPI", href=f"{pathname_prefix}dashboard_epi", className="submenu-link", id="epi-dashboard-link")),
                    html.Li(html.A("Advanced HIV Disease", href=f"{pathname_prefix}dashboard_adv_hiv", className="submenu-link", id="adv-hiv-dashboard-link")),
                ], id="dashboards-submenu", className="submenu")
            ], className="nav-item has-submenu"),
            html.Li([
                html.A("OPD Reports", id="opd-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("HMIS 15", href=f"{pathname_prefix}hmis15", className="submenu-link", id="hmis15-link")),
                    html.Li(html.A("Malaria", href=f"{pathname_prefix}malaria_report", className="submenu-link", id="malaria-link")),
                    html.Li(html.A("Other", href=f"{pathname_prefix}lmis", className="submenu-link", id="lmis-link")),
                ], id="opd-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            html.Li([
                html.A("IDSR Reports", id="idsr-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("IDSR Weekly", href=f"{pathname_prefix}idsr_weekly", className="submenu-link", id="idsr-weekly-link")),
                    html.Li(html.A("IDSR Monthly", href=f"{pathname_prefix}idsr_monthly", className="submenu-link", id="idsr-monthly-link")),
                ], id="idsr-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            html.Li([
                html.A("NCD Reports", id="ncd-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("Non-Communicable Diseases (NCD)", href=f"{pathname_prefix}ncd_report_ncd", className="submenu-link", id="ncd-link")),
                    html.Li(html.A("Non-Communicable Diseases PEN PLUS", href=f"{pathname_prefix}ncd_report_pen_plus", className="submenu-link", id="ncd-pen-plus-link")),
                    html.Li(html.A("Non-Communicable Diseases Quarterly Report", href=f"{pathname_prefix}ncd_report_quarterly", className="submenu-link", id="ncd-quarterly-link")),
                ], id="ncd-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            # New HIV Reports submenu
            html.Li([
                html.A("HIV Reports", id="hiv-reports-link", href="#", className="nav-link", n_clicks=0),
                html.Ul([
                    html.Li(html.A("HIV Testing Summary", href=f"{pathname_prefix}hts_report", className="submenu-link", id="hts-link")),
                    html.Li(html.A("HTC Health Facility Report", href=f"{pathname_prefix}htc_health_facility_report", className="submenu-link", id="hiv-facility-link")),
                    html.Li(html.A("DHA Integrated Rapid Testing Monthly Report", href=f"{pathname_prefix}integrated_testing_report", className="submenu-link", id="hiv-integrated-link")),
                    html.Li(html.A("DHA Integrated Rapid Testing HIV Testing Summary", href=f"{pathname_prefix}integrated_testing_summary_report", className="submenu-link", id="hiv-integrated-summary-link")),
                    html.Li(html.A("DHA Integrated Initial Testing Register", href=f"{pathname_prefix}integrated_testing_register", className="submenu-link", id="hiv-integrated-register-link")),
                ], id="hiv-reports-submenu", className="submenu")
            ], className="nav-item has-submenu"),

            html.Li(html.A("EPI Report", href=f"{pathname_prefix}epi_report", className="nav-link", id="epi-link")),
        ], className="nav-list")
    ], className="navbar"),
    page_container,
    
], style={ 'margin': '20px', 'fontFamily': 'Arial, sans-serif'})

@app.callback(
    [Output("opd-reports-submenu", "className"),
     Output("opd-reports-link", "className"),
     Output("idsr-reports-submenu", "className"),
     Output("idsr-reports-link", "className"),
     Output("ncd-reports-submenu", "className"),
     Output("ncd-reports-link", "className"),
     Output("hiv-reports-submenu", "className"),
     Output("hiv-reports-link", "className"),
     Output("dashboards-submenu", "className"),
     Output("dashboards-link", "className"),
     ],
    [Input("opd-reports-link", "n_clicks"),
     Input("idsr-reports-link", "n_clicks"),
     Input("ncd-reports-link", "n_clicks"),
     Input("hiv-reports-link", "n_clicks"),
     Input("dashboards-link", "n_clicks"),
     ],
    [State("opd-reports-submenu", "className"),
     State("opd-reports-link", "className"),
     State("idsr-reports-submenu", "className"),
     State("idsr-reports-link", "className"),
     State("ncd-reports-submenu", "className"),
     State("ncd-reports-link", "className"),
     State("hiv-reports-submenu", "className"),
     State("hiv-reports-link", "className"),
     State("dashboards-submenu", "className"),
     State("dashboards-link", "className"),
     ],
)

def toggle_submenu(opd_clicks, idsr_clicks, ncd_clicks, hiv_clicks, dashboards_clicks,
                  opd_submenu_class, opd_link_class,
                  idsr_submenu_class, idsr_link_class,
                  ncd_submenu_class, ncd_link_class,
                  hiv_submenu_class, hiv_link_class,
                  dashboards_submenu_class, dashboards_link_class):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return [dash.no_update] * 10
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # OPD toggle
    if triggered_id == "opd-reports-link":
        if "show" in opd_submenu_class:
            return (
                "submenu", opd_link_class.replace(" show-submenu", ""),
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
        else:
            return (
                "submenu show", opd_link_class + " show-submenu",
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
    
    # IDSR toggle
    elif triggered_id == "idsr-reports-link":
        if "show" in idsr_submenu_class:
            return (
                dash.no_update, dash.no_update,
                "submenu", idsr_link_class.replace(" show-submenu", ""),
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
        else:
            return (
                dash.no_update, dash.no_update,
                "submenu show", idsr_link_class + " show-submenu",
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
    
    # NCD toggle
    elif triggered_id == "ncd-reports-link":
        if "show" in ncd_submenu_class:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu", ncd_link_class.replace(" show-submenu", ""),
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
        else:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu show", ncd_link_class + " show-submenu",
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
    
    # HIV Reports toggle
    elif triggered_id == "hiv-reports-link":
        if "show" in hiv_submenu_class:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu", hiv_link_class.replace(" show-submenu", ""),
                dash.no_update, dash.no_update
            )
        else:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu show", hiv_link_class + " show-submenu",
                dash.no_update, dash.no_update
            )
    
    # Dashboards toggle
    elif triggered_id == "dashboards-link":
        if "show" in dashboards_submenu_class:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu", dashboards_link_class.replace(" show-submenu", "")
            )
        else:
            return (
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                dash.no_update, dash.no_update,
                "submenu show", dashboards_link_class + " show-submenu"
            )
    
    return [dash.no_update] * 10

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
     Output('ncd-dashboard-link', 'href'),
     Output('opd-dashboard-link', 'href'),
     Output('epi-dashboard-link', 'href'),
     Output('hiv-dashboard-link', 'href'),
     Output('adv-hiv-dashboard-link', 'href'),
     Output('ncd-link', 'href'),
     Output('ncd-pen-plus-link', 'href'),
     Output('ncd-quarterly-link', 'href'),
     Output('hts-link', 'href'),
     Output('hiv-facility-link', 'href'),
     Output('epi-link', 'href'),
     Output('hmis15-link', 'href'),
     Output('malaria-link', 'href'),
     Output('lmis-link', 'href'),
     Output('idsr-weekly-link', 'href'),
     Output('idsr-monthly-link', 'href'),
    ],
    Input('url-params-store', 'data')
)

def update_nav_links(location):
    query = f"?Location={location}" if location else ""

    return (
        f"{pathname_prefix}home{query}",
        f"{pathname_prefix}dashboard_ncd{query}",
        f"{pathname_prefix}dashboard_opd{query}",
        f"{pathname_prefix}dashboard_epi{query}",
        f"{pathname_prefix}dashboard_hiv{query}",
        f"{pathname_prefix}dashboard_adv_hiv{query}",
        f"{pathname_prefix}ncd_report_ncd{query}",
        f"{pathname_prefix}ncd_report_pen_plus{query}",
        f"{pathname_prefix}ncd_report_quarterly{query}",
        f"{pathname_prefix}hiv_report_monthly{query}",
        f"{pathname_prefix}htc_health_facility_report{query}",
        f"{pathname_prefix}epi_report{query}",
        f"{pathname_prefix}hmis15{query}",
        f"{pathname_prefix}malaria_report{query}",
        f"{pathname_prefix}lmis{query}",
        f"{pathname_prefix}idsr_weekly{query}",
        f"{pathname_prefix}idsr_monthly{query}",
    )

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True,)