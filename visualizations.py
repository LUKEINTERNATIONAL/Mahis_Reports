import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dash_table, html
import re
from datetime import datetime, timedelta

def _apply_filter(data, filter_col, filter_value):
    """
    Apply a single filter with support for comparison operators.
    
    Rules:
    - If filter_value is a list: use isin()
    - If filter_value is int/float and starts with:
        '=': ==
        '<': <
        '<=': <=
        '>': >
        '>=': >=
    - If filter_value is str and starts with:
        '=': ==
        '!=': !=
    - Otherwise: ==
    """
    if filter_col is None or filter_value is None:
        return data
    
    # Handle list case
    if isinstance(filter_value, list):
        return data[data[filter_col].isin(filter_value)]
    
    # Handle string with comparison operators
    if isinstance(filter_value, str):
        # Check if it's a comparison operator
        if filter_value.startswith(('=', '!=', '<', '>', '<=', '>=')):
            # Try to extract operator and value
            match = re.match(r'^([=!<>]=?)\s*(.+)$', filter_value)
            if match:
                operator, value_str = match.groups()
                
                # Try to convert to numeric if possible
                try:
                    if '.' in value_str:
                        value = float(value_str)
                    else:
                        value = int(value_str)
                except ValueError:
                    value = value_str
                
                # Apply operator
                if operator == '=':
                    return data[data[filter_col] == value]
                elif operator == '!=':
                    return data[data[filter_col] != value]
                elif operator == '<':
                    return data[data[filter_col] < value]
                elif operator == '<=':
                    return data[data[filter_col] <= value]
                elif operator == '>':
                    return data[data[filter_col] > value]
                elif operator == '>=':
                    return data[data[filter_col] >= value]
        
        # Default string equality
        return data[data[filter_col] == filter_value]
    
    # Handle numeric values (int/float)
    elif isinstance(filter_value, (int, float)):
        # Check if it's a string representation (like "=10" passed as string)
        if isinstance(filter_value, str):
            return _apply_filter(data, filter_col, filter_value)
        else:
            # Default numeric equality
            return data[data[filter_col] == filter_value]
    
    # Default case
    return data[data[filter_col] == filter_value]

def create_column_chart(df, x_col, y_col, title, x_title, y_title,
                        unique_column='person_id', legend_title=None,
                        color=None, filter_col1=None, filter_value1=None,
                        filter_col2=None, filter_value2=None,
                        filter_col3=None, filter_value3=None):
    """
    Create a column chart using Plotly Express with legend support.
    Labels will display both count and percentage, e.g. "10 (25.1%)".
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    
    data = data.drop_duplicates(subset=[unique_column, 'Date'])

    if color:
        # Group by both x_col and color column
        summary = data.groupby([x_col, color])[y_col].nunique().reset_index()
        total = summary[y_col].sum()
        summary["label"] = summary[y_col].astype(str) + "(" + (summary[y_col]/total*100).round(1).astype(str) + "%)"
        
        fig = px.bar(
            summary, 
            x=x_col, 
            y=y_col, 
            color=color,
            title=title, 
            text="label",
            color_discrete_sequence=px.colors.qualitative.Dark2,
            barmode='group'
        )
    else:
        # Group only by x_col
        summary = data.groupby(x_col)[y_col].nunique().reset_index()
        summary = summary.sort_values(by=y_col, ascending=False)
        total = summary[y_col].sum()
        summary["label"] = summary[y_col].astype(str) + "(" + (summary[y_col]/total*100).round(1).astype(str) + "%)"
        
        fig = px.bar(summary, x=x_col, y=y_col, title=title, text="label")
        fig.update_traces(marker_color="#006401")

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        legend_title=legend_title if legend_title else color,
    )

    fig.update_traces(
        textposition='inside',
        hovertemplate="<b>X-Axis:</b> %{x}<br>" +
                      "<b>Count:</b> %{y}<br>" 
    )
    
    return fig

def create_line_chart(df, date_col, y_col, title, x_title, y_title, unique_column='person_id', legend_title=None, color=None, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, filter_col3=None, filter_value3=None):
    """
    Create a time series chart using Plotly Express.
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    data = data.drop_duplicates(subset=[unique_column, 'Date'])

    # Ensure date column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
        try:
            data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        except Exception as e:
            raise ValueError(f"Error converting {date_col} to datetime: {e}")

    data = data.copy()
    data[date_col] = pd.to_datetime(data[date_col]).dt.date

    if color:
        summary = data.groupby([date_col, color])[y_col].nunique().reset_index(name='count')
    else:
        summary = data.groupby(date_col)[y_col].nunique().reset_index(name='count')

    fig = px.line(
        summary,
        x=date_col,
        y='count',
        color=color if color else None,
        color_discrete_sequence=px.colors.qualitative.Dark2,
        title=title,
        markers=True,
        text='count'
    )
    
    fig.update_traces(
        mode='lines+markers+text',
        textposition='top center',
        hovertemplate="<b>Date:</b> %{x|%b %d}<br>" +
                     "<b>Count:</b> %{y}<br>"
    )

    avg_val = summary['count'].mean()
    fig.add_hline(
        y=avg_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average = {avg_val:.0f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title, tickformat='%b %d'),
        legend_title=legend_title if legend_title else (color if color else ""),
        template="plotly_white"
    )
    
    return fig

def create_pie_chart(df, names_col, values_col, title, unique_column='person_id', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, filter_col3=None, filter_value3=None, colormap=None):
    """
    Create a pie chart using Plotly Express.
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    
    data = data.drop_duplicates(subset=[unique_column, 'Date'])
    
    df_summary = data.groupby(names_col)[values_col].nunique().reset_index()
    df_summary.columns = [names_col, values_col]

    fig = px.pie(df_summary, 
                 names=names_col, 
                 values=values_col, 
                 title=title, hole=0.5, 
                 color_discrete_map=px.colors.qualitative.Dark2 if colormap is None else colormap
                 )
    
    if colormap:
        categories = df_summary[names_col].tolist()
        colors = [colormap.get(cat, None) for cat in categories]
        fig.update_traces(marker=dict(colors=colors))
    
    fig.update_traces(textposition='inside', 
                      textinfo='percent+label',
                      hovertemplate="<b>Category:</b> %{label}<br>" +
                                    "<b>Value:</b> %{value}<br>" +
                                    "<b>Percent:</b> %{percent}<br>" 
                 )
    return fig 


import plotly.graph_objects as go


import plotly.graph_objects as go

def create_pivot_table(df, index_col, columns_col, values_col, title, unique_column='person_id', aggfunc='sum',
                     filter_col1=None, filter_value1=None, 
                     filter_col2=None, filter_value2=None,
                     filter_col3=None, filter_value3=None,
                     rename={}, replace={}):
    """
    Create a pivot table from the DataFrame.
    """
    data = df
    # Rename columns and replace content (explicit columns=)
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    data = data.drop_duplicates(subset=[unique_column, 'Date'])

    # Build pivot
    if aggfunc == 'concat':
        pivot = data.pivot_table(
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=lambda x: ', '.join(sorted(set(str(v) for v in x if str(v) != ''))),
        ).reset_index()
        value_format = None  # strings → no numeric formatting
    else:
        pivot = data.pivot_table(
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=aggfunc
        ).reset_index()
        value_format = ",.0f"  # numeric formatting for value columns

    num_index_cols = len(index_col) if isinstance(index_col, (list, tuple)) else 1

    align_list = (['left'] * num_index_cols) + (['center'] * (len(pivot.columns) - num_index_cols))

    if value_format is None:
        format_list = [None] * len(pivot.columns)
    else:
        format_list = ([None] * num_index_cols) + ([value_format] * (len(pivot.columns) - num_index_cols))

    pivot = pivot.rename(columns=rename).replace(replace)
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>" + col + "</b>" for col in pivot.columns],
            fill_color='grey',
            align=align_list,
            font=dict(size=12, color='white')
        ),
        cells=dict(
            values=[pivot[col] for col in pivot.columns],
            fill_color='white',
            align=align_list,
            height=30,
            format=format_list,
            font=dict(size=11, color='darkslategray')
        )
    )])


    row_height = 30
    extra_space = 100
    dynamic_height = row_height * len(pivot) + extra_space


    layout_updates = {
        'title': dict(
            text='<b>' + title + '</b>',
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=18, color='black'),
        ),
        'margin': dict(l=20, r=20, b=20, t=50),
        'height': dynamic_height
    }
    
    fig.update_layout(**layout_updates)
    return fig


def create_crosstab_table(
    df,
    index_col,
    columns_col,
    title,
    values_col=None,
    aggfunc='count',
    normalize=None,
    unique_column='person_id',
    filter_col1=None, filter_value1=None,
    filter_col2=None, filter_value2=None,
    filter_col3=None, filter_value3=None,
    rename={}, replace={}
):
    """
    Create a crosstab table with multilayer column headers using Dash DataTable.
    """

    data = df.copy()

    # Apply filters
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    # Deduplicate by person + date
    if 'Date' in data.columns:
        data = data.drop_duplicates(subset=[unique_column, 'Date'])

    # Helper: support multi-axis for crosstab
    def _axis_arg(arg):
        if isinstance(arg, (list, tuple)):
            return [data[c] for c in arg]
        return data[arg]

    index_arg = _axis_arg(index_col)
    columns_arg = _axis_arg(columns_col)

    # Handle normalization
    norm = False
    if normalize is True:
        norm = 'all'
    elif normalize in ('all', 'index', 'columns'):
        norm = normalize

    # Build the crosstab
    if values_col is None:
        ct = pd.crosstab(index=index_arg, columns=columns_arg, normalize=norm)
    else:
        if aggfunc == 'concat':
            ct = pd.crosstab(
                index=index_arg,
                columns=columns_arg,
                values=data[values_col],
                aggfunc=lambda x: ', '.join(sorted(set(str(v) for v in x if pd.notna(v) and v != '')))
            )
        else:
            ct = pd.crosstab(
                index=index_arg,
                columns=columns_arg,
                values=data[values_col],
                aggfunc=aggfunc,
                normalize=norm
            )

    ct = ct.reset_index()

    ct = ct.rename(columns=rename).replace(replace)

    dash_columns = []
    for col in ct.columns:
        if isinstance(col, tuple):
            dash_columns.append({
                "name": [str(c) for c in col],
                "id": "|".join([str(c) for c in col])
            })
        else:
            dash_columns.append({
                "name": [str(col)],
                "id": str(col)
            })

    ct_flat = ct.copy()
    ct_flat.columns = [
        "|".join(str(c) for c in col) if isinstance(col, tuple) else str(col)
        for col in ct.columns
    ]

    # Format options
    percent_format = "{:.1%}"
    int_format = "{:,.0f}"

    # Data formatting
    data_records = ct_flat.to_dict("records")


    table = html.Div([
        html.H4(title, style={"textAlign":"center"}),
        dash_table.DataTable(
            id="crosstab-table",
            columns=dash_columns,
            data=data_records,
            merge_duplicate_headers=False,
            style_header={
                "backgroundColor": "rgb(70,70,70)",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "center",
                "fontSize": "13px",
            },
            style_cell={
                "padding": "6px",
                "textAlign": "center",
                "fontSize": "12px",
            },
            style_table={"overflowX": "scroll"},
            page_size=50,
        )
    ])

    return table


def create_age_gender_histogram(df, age_col, gender_col, title, xtitle, ytitle, bin_size,
                                 filter_col1=None, filter_value1=None, 
                                filter_col2=None, filter_value2=None,
                                filter_col3=None, filter_value3=None):
    """
    Create a histogram of age distribution grouped by gender (side-by-side bars).
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    df_unique = data.drop_duplicates(subset=['person_id', 'Date'])

    if df_unique.empty:
        return go.Figure()
    else:
        fig = px.histogram(df_unique,
                        x=age_col,
                        color=gender_col,
                        nbins=int((df_unique[age_col].max() - df_unique[age_col].min()) / bin_size),
                        barmode='group',
                        title=title,
                        color_discrete_sequence=px.colors.qualitative.Dark2)

        fig.update_layout(
            xaxis_title=xtitle,
            yaxis_title=ytitle
        )

        return fig

def create_horizontal_bar_chart(df, label_col, value_col, title, x_title, y_title, top_n=10,
                                 filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None,
                                 filter_col3=None, filter_value3=None):
    """
    Create a horizontal bar chart showing the top N items by value.
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    df_unique = data.drop_duplicates(subset=['person_id', 'Date'])

    df_grouped = df_unique.groupby(label_col)[value_col].nunique().reset_index()
    df_top = df_grouped.sort_values(by=value_col, ascending=False).head(top_n)

    fig = px.bar(df_top,
                 x=value_col,
                 y=label_col,
                 text=value_col,
                 orientation='h',
                 title=title)
    fig.update_traces(
        textposition='auto',
        texttemplate='%{text}',
        marker_color='steelblue'
    )

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        yaxis=dict(autorange='reversed')
    )

    return fig

def create_count(df, unique_column='encounter_id', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None,
                 filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None, 
                 filter_col7=None, filter_value7=None, filter_col8=None, filter_value8=None,
                 filter_col9=None, filter_value9=None, filter_col10=None, filter_value10=None):
    data = df
    
    # Apply all filters using the helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    data = _apply_filter(data, filter_col4, filter_value4)
    data = _apply_filter(data, filter_col5, filter_value5)
    data = _apply_filter(data, filter_col6, filter_value6)
    data = _apply_filter(data, filter_col7, filter_value7)
    data = _apply_filter(data, filter_col8, filter_value8)
    data = _apply_filter(data, filter_col9, filter_value9)
    data = _apply_filter(data, filter_col10, filter_value10)
    
    unique_visits = data.drop_duplicates(subset=['person_id', 'Date'])
    return str(len(unique_visits))

def create_count_sets(df, unique_column='person_id', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None,
                      filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None,
                 filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None, 
                 filter_col7=None, filter_value7=None, filter_col8=None, filter_value8=None,
                 filter_col9=None, filter_value9=None, filter_col10=None, filter_value10=None):
    """
    Count unique IDs that satisfy a paired condition across two filters.
    """
    data = df
    
    # Apply first filter if provided
    if filter_col1 is not None:
        data = _apply_filter(data, filter_col1, filter_value1)

    if not (isinstance(filter_value2, list) and isinstance(filter_value3, list)):
        raise ValueError("filter_value2 and filter_value3 must be lists of the same length.")
    if len(filter_value2) != len(filter_value3):
        raise ValueError("filter_value2 and filter_value3 must have the same length.")

    pair_ids = []
    for v1, v2 in zip(filter_value2, filter_value3):
        ids = set(df.loc[(df[filter_col2] == v1) & (df[filter_col3] == v2), unique_column])
        pair_ids.append(ids)

    pair_total = set.intersection(*pair_ids)
    filtered = df[df[unique_column].isin(pair_total)]

    data = _apply_filter(filtered, filter_col4, filter_value4)
    data = _apply_filter(data, filter_col5, filter_value5)
    data = _apply_filter(data, filter_col6, filter_value6)
    data = _apply_filter(data, filter_col7, filter_value7)
    data = _apply_filter(data, filter_col8, filter_value8)
    data = _apply_filter(data, filter_col9, filter_value9)
    data = _apply_filter(data, filter_col10, filter_value10)

    # Apply extra filters if provided
    
    return len(data[unique_column].unique())

def create_count_unique(df, unique_column='person_id', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None,
                 filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    
    # Apply all filters using the helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    data = _apply_filter(data, filter_col4, filter_value4)
    data = _apply_filter(data, filter_col5, filter_value5)
    data = _apply_filter(data, filter_col6, filter_value6)
    
    return str(len(data[unique_column].unique()))

def create_sum(df, num_field='ValueN', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None,
                 filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    
    # Apply all filters using the helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    data = _apply_filter(data, filter_col4, filter_value4)
    data = _apply_filter(data, filter_col5, filter_value5)
    data = _apply_filter(data, filter_col6, filter_value6)
    
    return data[num_field].sum()

def create_sum_sets(df, filter_col1, filter_value1, filter_col2, filter_value2, num_field='ValueN',
                      unique_column='encounter_id', **extra_filters):
    """
    Sum values for unique IDs that satisfy a paired condition.
    """
    if not (isinstance(filter_value1, list) and isinstance(filter_value2, list)):
        raise ValueError("filter_value1 and filter_value2 must be lists of the same length.")
    if len(filter_value1) != len(filter_value2):
        raise ValueError("filter_value1 and filter_value2 must have the same length.")

    pair_ids = []
    for v1, v2 in zip(filter_value1, filter_value2):
        ids = set(df.loc[(df[filter_col1] == v1) & (df[filter_col2] == v2), unique_column])
        pair_ids.append(ids)

    pair_total = set.intersection(*pair_ids)
    filtered = df[df[unique_column].isin(pair_total)]

    # Apply extra filters if provided
    for i in range(3, 7):
        col = extra_filters.get(f'filter_col{i}')
        val = extra_filters.get(f'filter_value{i}')
        if col is not None and val is not None:
            filtered = _apply_filter(filtered, col, val)

    return filtered[num_field].sum()