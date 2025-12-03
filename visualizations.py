import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

def create_pivot_table(df, index_col1, columns_col1, values_col, title, unique_column='person_id', aggfunc='sum',
                     filter_col1=None, filter_value1=None, 
                     filter_col2=None, filter_value2=None,
                     filter_col3=None, filter_value3=None,
                     xaxis_title=None, yaxis_title=None, show_axes=False):
    """
    Create a pivot table from the DataFrame.
    """
    data = df
    
    # Apply filters using the new helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)

    data = data.drop_duplicates(subset=[unique_column,'Date'])

    if aggfunc == 'concat':
        pivot = data.pivot_table(
            index=index_col1,
            columns=columns_col1,
            values=values_col,
            aggfunc=lambda x: ', '.join(sorted(set(str(v) for v in x if str(v) != ''))),
        ).reset_index()
    else:
        pivot = data.pivot_table(
            index=index_col1,
            columns=columns_col1,
            values=values_col,
            aggfunc=aggfunc
        ).reset_index()

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>" + col + "</b>" for col in pivot.columns],
            fill_color='grey',
            align='left',
            font=dict(size=12, color='white')
        ),
        cells=dict(
            values=[pivot[col] for col in pivot.columns],
            fill_color='white',
            align='left',
            height=30,
            format=[None] + [",.0f"]*(len(pivot.columns)-1),
            font=dict(size=11,color = 'darkslategray',))
    )])

    layout_updates = {
        'title': dict(
            text=title,
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=14)
        ),
        'margin': dict(l=20, r=20, b=20, t=80),
        'height': 400
    }
    
    if show_axes:
        layout_updates['xaxis'] = {'title': xaxis_title or 'X Axis'}
        layout_updates['yaxis'] = {'title': yaxis_title or 'Y Axis'}
    
    fig.update_layout(**layout_updates)
    return fig

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
                 filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    
    # Apply all filters using the helper function
    data = _apply_filter(data, filter_col1, filter_value1)
    data = _apply_filter(data, filter_col2, filter_value2)
    data = _apply_filter(data, filter_col3, filter_value3)
    data = _apply_filter(data, filter_col4, filter_value4)
    data = _apply_filter(data, filter_col5, filter_value5)
    data = _apply_filter(data, filter_col6, filter_value6)
    
    unique_visits = data.drop_duplicates(subset=['person_id', 'Date'])
    return str(len(unique_visits))

def create_count_sets(df, unique_column='person_id', filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None,
                      filter_col3=None, filter_value3=None, **extra_filters):
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

    # Apply extra filters if provided
    for i in range(4, 7):
        col = extra_filters.get(f'filter_col{i}')
        val = extra_filters.get(f'filter_value{i}')
        if col is not None and val is not None:
            filtered = _apply_filter(filtered, col, val)

    return len(filtered[unique_column].unique())

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