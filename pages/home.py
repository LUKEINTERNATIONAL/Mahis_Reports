import dash
from dash import html, dcc, Input, Output, callback, State, no_update, ALL, callback_context
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np
from dash.exceptions import PreventUpdate
import os
from visualizations import (create_column_chart, 
                          create_count,
                          create_pie_chart,
                          create_line_chart,
                          create_age_gender_histogram,
                          create_horizontal_bar_chart,
                          create_pivot_table,create_crosstab_table)
from datetime import datetime, timedelta

dash.register_page(__name__, path="/home")

path = os.getcwd()
json_path = os.path.join(path, 'data', 'visualizations', 'validated_dashboard.json')

# Load data once to get date range
min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
max_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

path = os.getcwd()
last_refreshed = pd.read_csv(f'{path}/data/TimeStamp.csv')['saving_time'].to_list()[0]

def build_metrics_section(filtered, counts_config):
    """Build metric cards from counts configuration"""
    metrics = []
    
    for count_config in counts_config:
        metric = html.Div(
            html.Div([
                html.H2(
                    create_count_from_config(filtered, count_config["filters"]), 
                    className="metric-value"
                ),
                html.H4(count_config["name"], className="metric-title"),
            ], className="card")
        )
        metrics.append(metric) 
    
    return metrics

def parse_filter_value(filter_val):
        """Convert string representation of list to actual list if needed"""
        if filter_val is None:
            return None
        if isinstance(filter_val, list):
            return filter_val
        if isinstance(filter_val, str) and filter_val.startswith('[') and filter_val.endswith(']'):
            try:
                # Remove brackets and split by comma, then strip quotes and whitespace
                items = filter_val[1:-1].split(',')
                return [item.strip().strip("'\"") for item in items if item.strip()]
            except:
                return filter_val
        return filter_val

def create_count_from_config(df, filters):
    """Create count based on JSON filter configuration"""

    unique_col = filters.get("unique", "")

    # Extract variables and values
    variables = [
        filters.get("variable1", ""),
        filters.get("variable2", ""),
        filters.get("variable3", ""),
        filters.get("variable4", ""),
        filters.get("variable5", ""),
        filters.get("variable6", ""),
        filters.get("variable7", ""),
        filters.get("variable8", ""),
        filters.get("variable9", ""),
        filters.get("variable10", "")
    ]

    values = [
        parse_filter_value(filters.get("value1", "")),
        parse_filter_value(filters.get("value2", "")),
        parse_filter_value(filters.get("value3", "")),
        parse_filter_value(filters.get("value4", "")),
        parse_filter_value(filters.get("value5", "")),
        parse_filter_value(filters.get("value6", "")),
        parse_filter_value(filters.get("value7", "")),
        parse_filter_value(filters.get("value8", "")),
        parse_filter_value(filters.get("value9", "")),
        parse_filter_value(filters.get("value10", ""))
    ]
    active_filters = []
    for var, val in zip(variables, values):
        if var and val:
            active_filters.append((var, val))
    if not active_filters:
        return create_count(df, unique_col)

    if active_filters[0][0] != filters.get("variable1"):
        return create_count(df, unique_col)  # failsafe
    args = []
    for var, val in active_filters:
        args.extend([var, val])
    return create_count(df, unique_col, *args)

def build_charts_section(filtered, data_opd, delta_days, sections_config):
    """Build chart sections from JSON configuration"""
    sections = []
    
    for section_config in sections_config:
        section = html.Div([
            html.H2(section_config["section_name"], style={'textAlign': 'left', 'color': 'black'}),
            build_section_items(filtered, data_opd, delta_days, section_config["items"])
        ])
        sections.append(section)
    
    return html.Div(sections)

def build_section_items(filtered, data_opd, delta_days, items_config):
    """Build individual chart items within a section"""
    items = []
    
    # Group items into pairs for card-container-2
    for i in range(0, len(items_config), 3):
        pair_items = items_config[i:i+3]
        card_container = html.Div(
            className="card-container-3",
            children=[
                build_single_chart(filtered, data_opd, delta_days, item_config)
                for item_config in pair_items
            ]
        )
        items.append(card_container)
    
    return html.Div(items)

def build_single_chart(filtered, data_opd, delta_days, item_config, style = "card-2"):
    """Build a single chart based on configuration"""
    chart_type = item_config["type"]
    filters = item_config["filters"]
    
    if chart_type == "Line":
        figure = create_line_chart_from_config(data_opd, delta_days, filters)
    elif chart_type == "Pie":
        figure = create_pie_chart_from_config(filtered, filters)
    elif chart_type == "Column":
        figure = create_column_chart_from_config(filtered, filters)
    elif chart_type == "Bar":
        figure = create_bar_chart_from_config(filtered, filters)
    elif chart_type == "Histogram":
        figure = create_histogram_from_config(filtered, filters)
    elif chart_type == "PivotTable":
        figure = create_pivot_table_from_config(filtered, filters)
    elif chart_type == "CrossTab":
        figure = create_crosstab_from_config(filtered, filters)
    else:
        # Default empty figure for unknown chart types
        figure = create_empty_figure()
    if chart_type in ["Line","Pie","Column","Bar","Histogram","PivotTable"]:
        return dcc.Graph(
            id=item_config["filters"]["unique"],
            figure=figure,
            className=style
        )
    else:
        return figure


def create_line_chart_from_config(data_opd, delta_days, filters):
    """
    Create line chart from JSON configuration
    Configs
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
                "filter_val2": "",
                "filter_col3": "",
                "filter_val3": ""
    """
    date_filter = str(datetime.now() - pd.Timedelta(days=delta_days))
    filtered_data = data_opd[data_opd['Date'] >= date_filter]
    
    # keys = list(filters.keys())[3:]
    date_col       = filters.get('date_col')
    y_col          = filters.get('y_col')
    title          = filters.get('title')
    x_title        = filters.get('x_title')
    y_title        = filters.get('y_title')
    unique_column  = filters.get('unique_column')
    legend_title   = filters.get('legend_title') or None
    color          = filters.get('color') or None
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))

    return create_line_chart(filtered_data, date_col, y_col, title, x_title, y_title, unique_column, legend_title, color, filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3)

def create_pie_chart_from_config(filtered, filters):
    """
    Create pie chart from JSON configuration
    Configs:
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
                "filter_col3": "",
                "filter_val3": "",
                "colormap": {
                                "New": "#292D79",
                                "Revisit": "#FE1AD0"
                            }
                }
    """

    names_col       = filters.get('names_col')
    values_col      = filters.get('values_col')
    title           = filters.get('title')
    unique_column   = filters.get('unique_column')
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))
    colormap        = filters.get('colormap') or None
    
    return create_pie_chart(filtered, names_col, values_col, title, unique_column, filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3, colormap)

def create_column_chart_from_config(filtered, filters):
    """
    Create column chart from JSON configuration
    Config:
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
                "filter_val2": "",
                "filter_col3": "",
                "filter_val3": ""
    """
    
    x_col          = filters.get('x_col')
    y_col          = filters.get('y_col')
    title          = filters.get('title')
    x_title        = filters.get('x_title')
    y_title        = filters.get('y_title')
    unique_column  = filters.get('unique_column')
    legend_title   = filters.get('legend_title') or None
    color          = filters.get('color') or None
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))

    return create_column_chart(filtered, x_col, y_col, title, x_title, y_title, unique_column, legend_title, color, filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3)

def create_bar_chart_from_config(filtered, filters):
    """
    Create column chart from JSON configuration
    Config: 
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
                "filter_val2": "",
                "filter_col3": "",
                "filter_val3": ""
    """
    label_col     = filters.get("label_col")
    value_col     = filters.get("value_col")
    title         = filters.get("title")
    x_title       = filters.get("x_title")
    y_title       = filters.get("y_title")
    top_n         = filters.get("top_n") or 10
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))

    return create_horizontal_bar_chart(
        filtered, label_col, value_col, title, x_title, y_title, top_n,
        filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3
    )

def create_histogram_from_config(filtered, filters):
    """
    Create column chart from JSON configuration
    Config: 
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
                "filter_val2": "",
                "filter_col3": "",
                "filter_val3": ""
    """
    age_col       = filters.get("age_col")
    gender_col    = filters.get("gender_col")
    title         = filters.get("title")
    bin_size      = filters.get("bin_size") or 5
    x_title       = filters.get("x_title")
    y_title       = filters.get("y_title")
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))

    # print(f"my bin size {filtered}")

    return create_age_gender_histogram(
        filtered, age_col, gender_col, title, x_title, y_title, bin_size,
        filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3
    )

def create_pivot_table_from_config(filtered, filters):
    """
    Create pivot table from JSON configuration
    Config:     "measure": "chart",
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
                "filter_col3": "",
                "filter_val3": "",
                "x_title": "",
                "y_title": ""
    """
    index_col    = filters.get("index_col1")
    columns       = filters.get("columns")
    values_co    = filters.get("values_col")
    title         = filters.get('title')
    unique_column = filters.get('unique_column')
    aggfunc       = filters.get("aggfunc") or "sum"
    filter_col1    = filters.get('filter_col1') or None
    filter_val1    = parse_filter_value(filters.get('filter_val1'))
    filter_col2    = filters.get('filter_col2') or None
    filter_val2    = parse_filter_value(filters.get('filter_val2'))
    filter_col3    = filters.get('filter_col3') or None
    filter_val3    = parse_filter_value(filters.get('filter_val3'))

    return create_pivot_table(
        filtered, index_col, columns, values_co, title, unique_column, aggfunc,
        filter_col1, filter_val1, filter_col2, filter_val2, filter_col3, filter_val3
    )


def create_crosstab_from_config(filtered, filters):
    """
    Create crosstab table from JSON configuration.

    Example config:
        {
            "measure": "crosstab",
            "title": "Diagnosis × Gender × Age Group",
            "unique_column": "person_id",
            "index_col1": "DIAGNOSIS",                # rows
            "columns": ["Gender", "Age_Group"],       # columns (can be string or list)
            "values_col": null,                       # None → raw counts; or a field to aggregate
            "aggfunc": "count",                       # 'count', 'sum', 'nunique', 'mean', 'concat'
            "normalize": null,                        # null | true | "all" | "index" | "columns"
            "rename": {"obs_value_coded": "DIAGNOSIS"},
            "replace": {"Under Five": "Under5", "Over Five": "Over5"},

            "filter_col1": "concept_name",
            "filter_val1": "Primary diagnosis",
            "filter_col2": null,
            "filter_val2": null,
            "filter_col3": null,
            "filter_val3": null
        }
    """
    # Helper to parse index/columns if they arrive as comma-separated strings
    def _as_list_or_str(v):
        if isinstance(v, str) and ',' in v:
            return [s.strip() for s in v.split(',') if s.strip()]
        return v

    index_col     = _as_list_or_str(filters.get("index_col1") or filters.get("index"))
    columns_col   = _as_list_or_str(filters.get("columns") or filters.get("columns_col"))
    values_col    = filters.get("values_col") or None
    title         = filters.get("title")
    unique_column = filters.get("unique_column") or "person_id"
    aggfunc       = filters.get("aggfunc") or ("count" if values_col is None else "count")
    normalize     = filters.get("normalize")  # None | True | 'all' | 'index' | 'columns'

    # Filters (up to three)
    filter_col1   = filters.get("filter_col1") or None
    filter_val1   = parse_filter_value(filters.get("filter_val1"))
    filter_col2   = filters.get("filter_col2") or None
    filter_val2   = parse_filter_value(filters.get("filter_val2"))
    filter_col3   = filters.get("filter_col3") or None
    filter_val3   = parse_filter_value(filters.get("filter_val3"))

    # Optional rename/replace
    rename        = filters.get("rename") or {}
    replace       = filters.get("replace") or {}

    return create_crosstab_table(
        df=filtered,
        index_col=index_col,
        columns_col=columns_col,
        title=title,
        values_col=values_col,
        aggfunc=aggfunc,
        normalize=normalize,
        unique_column=unique_column,
        filter_col1=filter_col1, filter_value1=filter_val1,
        filter_col2=filter_col2, filter_value2=filter_val2,
        filter_col3=filter_col3, filter_value3=filter_val3,
        rename=rename, replace=replace
    )


def create_empty_figure():
    """Create empty figure for unsupported chart types"""
    return {
        'data': [],
        'layout': {
            'title': 'Chart configuration not supported',
            'xaxis': {'visible': False},
            'yaxis': {'visible': False}
        }
    }


# BUILD CHARTS
def build_charts_from_json(filtered, data_opd, delta_days, dashboards_json):
    # Load JSON configuration
    config = dashboards_json
    
    filtered = filtered.copy()
    filtered['Residence'] = filtered['Home_district'] + ', TA-' + filtered['TA'] + ', ' + filtered['Village']
    delta_days = 7 if delta_days <= 0 else delta_days
    
    # Build metrics from counts section
    metrics = build_metrics_section(filtered, config["visualization_types"]["counts"])
    
    # Build charts from sections
    charts = build_charts_section(filtered, data_opd, delta_days, config["visualization_types"]["charts"]["sections"])
    
    return html.Div([
        html.Div(className="card-container-5", children=metrics),
        charts
    ])

layout = html.Div(className="container", children=[
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='active-button-store', data='home'),
    html.Div([
        html.Div(
            [
                html.Button(item, className="menu-btn")
                for item in []
                ],
                className="horizontal-scroll",
                id="scrolling-menu"
            ),
        html.Div(className="filter-container", children=[
            html.Div([
                html.Label("Visit Type"),
                dcc.Dropdown(
                    id='dashboard-visit-type-filter',
                    options=[
                        {'label': item, 'value': item}
                        for item in ['New', 'Revisit']
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id='dashboard-date-range-picker',
                    min_date_allowed="2023-01-01",
                    max_date_allowed=datetime.now(),
                    initial_visible_month=datetime.now(),
                    start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    end_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0),
                    display_format='YYYY-MM-DD',
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Health Facility"),
                dcc.Dropdown(
                    id='dashboard-hf-filter',
                    options=[
                        {'label': hf, 'value': hf}
                        for hf in []
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),

            html.Div([
                html.Label("Age Group"),
                dcc.Dropdown(
                    id='dashboard-age-filter',
                    options=[
                        {'label': age, 'value': age}
                        for age in ['Over 5','Under 5']
                    ],
                    value=None,
                    clearable=True
                )
            ], className="filter-input"),
        ]),

]),
    html.Div(id='dashboard-container'),   
    dcc.Interval(
        id='dashboard-interval-update-today',
        interval=60*60*1000,  # in milliseconds
        n_intervals=0
    ),     
])

@callback(
        Output('scrolling-menu', 'children'),
        [Input('dashboard-interval-update-today', 'n_intervals'),
        Input('active-button-store', 'data')])

def update_menu(menu_items, color):
    
    with open(json_path, 'r') as f:
        menu_json = json.load(f)

    return [
        html.Button(
            d["report_name"],
            className="menu-btn active" if color == d["report_name"] else "menu-btn",
            id={"type": "menu-button", "name": d["report_name"]}
        )
        for d in menu_json
    ]




# Callback to update all components based on date range
@callback(
    [Output('dashboard-container', 'children'),
     Output('dashboard-hf-filter', 'options'),
     Output('active-button-store', 'data')],
    [
        Input('url-params-store', 'data'),
        Input('dashboard-date-range-picker', 'start_date'),
        Input('dashboard-date-range-picker', 'end_date'),
        Input('dashboard-visit-type-filter', 'value'),
        Input('dashboard-hf-filter', 'value'),
        Input('dashboard-age-filter', 'value'),
        Input({"type": "menu-button", "name": ALL}, "n_clicks"),
        State({"type": "menu-button", "name": ALL}, "id")
    ]
)
def update_dashboard(urlparams, start_date, end_date, visit_type, hf, age,n_clicks_list, id_list):
    
    start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59, microsecond=0)
    delta_days = (end_date - start_date).days
    
    with open(json_path, 'r') as f:
        menu_json = json.load(f)
    name_to_title = {d["report_id"]: d["report_name"] for d in menu_json}

    triggered = callback_context.triggered
    clicked_name = 'Summary'
    
    if triggered and "menu-button" in triggered[0]["prop_id"]:
            # Extract the name from the triggered input
            triggered_id = eval(triggered[0]["prop_id"].split(".")[0])  # converts string back to dict
            clicked_name = triggered_id["name"]

    clicked_title = name_to_title.get(clicked_name, clicked_name)
    for dashboard in menu_json:
        if dashboard['report_name'] == clicked_name:
            dashboard_json = dashboard
 
    parquet_path = os.path.join(path, 'data', 'latest_data_opd.parquet')
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"PARQUET file not found at {parquet_path}")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Dashboard not found: {clicked_title}")
    
    
    data_opd = pd.read_parquet(parquet_path)
    # print(sorted(list(data_opd)))
    data_opd['Date'] = pd.to_datetime(data_opd['Date'], format='mixed')
    data_opd['Gender'] = data_opd['Gender'].replace({"M":"Male","F":"Female"})
    # data_opd = data_opd[data_opd['Program']=='OPD Program']
    # data_opd.to_excel('data/archive/hmis.xlsx')
    

    if urlparams:
        search_url = data_opd[data_opd['Facility_CODE'].str.lower() == urlparams.lower()]
    else:
        PreventUpdate
        
        
    mask = pd.Series(True, index=search_url.index)
    if hf:
        mask &= (search_url['Facility'] == hf)
    if age:
        mask &= (search_url['Age_Group'] == age)

        
    filtered_data = search_url[mask].copy()

    filtered_data_date = filtered_data[
        (pd.to_datetime(filtered_data['Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(filtered_data['Date']) <= pd.to_datetime(end_date))
    ]
    
    return build_charts_from_json(filtered_data_date, filtered_data, delta_days, dashboard_json), filtered_data['Facility'].sort_values().unique().tolist(), clicked_name

@callback(
    [Output('dashboard-date-range-picker', 'start_date'),
     Output('dashboard-date-range-picker', 'end_date')],
    Input('dashboard-interval-update-today', 'n_intervals')
)
def update_date_range(n):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end

# @callback(
#     Output("dashboard-container", "children"),     # or any output you want
#     Input({"type": "menu-button", "name": ALL}, "n_clicks"),
#     State({"type": "menu-button", "name": ALL}, "id")
# )
# def menu_click_handler(n_clicks_list, id_list):
#     if not n_clicks_list or all(nc is None for nc in n_clicks_list):
#         return no_update

#     # find which button was clicked
#     for n_clicks, btn_id in zip(n_clicks_list, id_list):
#         if n_clicks:
#             clicked_name = btn_id["name"]     # ← this gives "home", "opd", etc
#             return f"You clicked: {clicked_name}"

#     return no_update