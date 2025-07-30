import dash
from dash import html, dcc, page_container, page_registry
import plotly.express as px
import pandas as pd


# print(list(load_stored_data())) # Load the data to ensure it's available
# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# Define the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Nav([
        html.Ul([
            html.Li(html.A("Dashboard", href="/home", className="nav-link")),
            html.Li(html.A("Malaria Report", href="/malaria_report", className="nav-link")),
            html.Li(html.A("HMIS 15 Report", href="/hmis15", className="nav-link")),
            html.Li(html.A("IDSR Weekly Report", href="/idsr_weekly", className="nav-link")),
            html.Li(html.A("IDSR Monthly Report", href="/idsr_monthly", className="nav-link")),
            html.Li(html.A("NCD Report", href="/hmis15", className="nav-link")),
        ], className="nav-list")
    ], className="navbar"),
    page_container,
    
], style={ 'margin': '20px', 'fontFamily': 'Arial, sans-serif'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)