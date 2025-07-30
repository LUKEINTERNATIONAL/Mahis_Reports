import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_column_chart(df, x_col, y_col, title, x_title, y_title, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None):
    """
    Create a column chart using Plotly Express.

    :param df: DataFrame containing the data
    :param x_col: Column name for the x-axis
    :param y_col: Column name for the y-axis (will be counted as unique values)
    :param title: Title of the chart
    :param x_title: Title for the x-axis
    :param y_title: Title for the y-axis
    :return: Plotly figure object
    """

    # Optional filtering
    if filter_col1 and filter_value1:
        df = df[df[filter_col1] == filter_value1]
    if filter_col2 and filter_value2:
        df = df[df[filter_col2] == filter_value2]

    # Aggregate data
    summary = df.groupby(x_col)[y_col].nunique().reset_index()
    summary.columns = [x_col, y_col]

    # Plot using summary
    fig = px.bar(summary, x=x_col, y=y_col, title=title, text=y_col,)
 
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white"
    )

    fig.update_traces(
        textposition='auto',  # display labels inside or outside automatically
        texttemplate='%{text}',  # format the label
        marker_color='steelblue'
    )   
    return fig

def create_line_chart(df, date_col, y_col, title, x_title, y_title, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None):
    """
    Create a time series chart using Plotly Express.

    :param df: DataFrame containing the data
    :param date_col: Date column name for the x-axis
    :param y_col: Column name for the y-axis (will be counted as unique values)
    :param title: Title of the chart
    :param x_title: Title for the x-axis
    :param y_title: Title for the y-axis
    :return: Plotly figure object
    """

    # Optional filtering
    if filter_col1 and filter_value1:
        df = df[df[filter_col1] == filter_value1]
    if filter_col2 and filter_value2:
        df = df[df[filter_col2] == filter_value2]

    # Ensure date column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        # Attempt to convert the date column to datetime format
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        except Exception as e:
            raise ValueError(f"Error converting {date_col} to datetime: {e}")

    df[date_col] = pd.to_datetime(df[date_col]).dt.date  # Convert to date only

    summary = df.groupby(date_col)[y_col].nunique().reset_index()
    summary.columns = [date_col, y_col]

    # Plot using summary
    fig = px.line(summary, x=date_col, y=y_col, title=title,color_discrete_sequence=['steelblue'])
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
    )
    return fig

def create_pie_chart(df, names_col, values_col, title, filter_col=None, filter_value=None):
    """
    Create a pie chart using Plotly Express.

    :param df: DataFrame containing the data
    :param names_col: Column name for the pie chart labels
    :param values_col: Column name for the pie chart values
    :param title: Title of the chart
    :param filter_col: Optional column to filter by
    :param filter_value: Optional value to filter by
    :return: Plotly figure object
    """
    
    if filter_col and filter_value:
        df = df[df[filter_col] == filter_value]
    
    df = df.groupby(names_col)[values_col].nunique().reset_index()
    df.columns = [names_col, values_col]

    fig = px.pie(df, names=names_col, values=values_col, title=title, hole=0.5, color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_pivot_table(df, index_col1, values_col, aggfunc='count', 
                     filter_col1=None, filter_value1=None, 
                     filter_col2=None, filter_value2=None):
    """
    Create a pivot table from the DataFrame.
    Returns a DataFrame (not a Graph object)
    """
    if filter_col1 and filter_value1:
        df = df[df[filter_col1] == filter_value1]
    if filter_col2 and filter_value2:
        df = df[df[filter_col2] == filter_value2]

    df = df.groupby([index_col1])[values_col].nunique().reset_index()
    df.columns = [index_col1, values_col]

    pivot_table = pd.pivot_table(df, index=index_col1, values=values_col, aggfunc=aggfunc)
    return pivot_table.reset_index()

def create_age_gender_histogram(df, age_col, gender_col, title, xtitle, ytitle, bin_size,
                                 filter_col=None, filter_value=None):
    """
    Create a histogram of age distribution grouped by gender (side-by-side bars).

    :param df: DataFrame with the data
    :param age_col: Column name for age values
    :param gender_col: Column name for gender values
    :param title: Title of the histogram
    :param xtitle: Label for X axis
    :param ytitle: Label for Y axis
    :param bin_size: Size of histogram bins (e.g., 5 years)
    :param filter_col: Column to filter by (e.g., 'District')
    :param filter_value: Value to filter by (e.g., 'Ntcheu')
    :return: Plotly histogram figure object
    """
    # Apply filter if specified
    if filter_col and filter_value:
        df = df[df[filter_col] == filter_value]

    # Drop duplicates to ensure unique person_id
    df_unique = df.drop_duplicates(subset='person_id')

    if df_unique.empty:
        # raise ValueError("The DataFrame is empty after filtering. Please check your data or filters.")
        return go.Figure()
    else:
    # Build histogram with side-by-side bars
        fig = px.histogram(df_unique,
                        x=age_col,
                        color=gender_col,
                        nbins=int((df_unique[age_col].max() - df_unique[age_col].min()) / bin_size),
                        barmode='group',  # <-- changed from 'overlay' to 'group'
                        title=title,
                        color_discrete_sequence=px.colors.qualitative.T10)

        fig.update_layout(
            xaxis_title=xtitle,
            yaxis_title=ytitle
        )

        return fig

def create_horizontal_bar_chart(df, label_col, value_col, title, x_title, y_title, top_n=10,
                                 filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None):
    """
    Create a horizontal bar chart showing the top N items by value.

    :param df: DataFrame containing the data
    :param label_col: Column name for labels (y-axis)
    :param value_col: Column name for values (x-axis)
    :param title: Title of the chart
    :param x_title: Label for x-axis
    :param y_title: Label for y-axis
    :param top_n: Number of top items to display (default is 10)
    :param filter_col: Optional column to filter
    :param filter_value: Optional value to filter by
    :return: Plotly Figure object
    """
    # Filter data if needed
    if filter_col1 and filter_value1:
        df = df[df[filter_col1] == filter_value1]
    if filter_col2 and filter_value2:
        df = df[df[filter_col2] == filter_value2]

    # Aggregate (optional, depending on your use case)
    df_grouped = df.groupby(label_col)[value_col].nunique().reset_index()

    # Sort and get top N
    df_top = df_grouped.sort_values(by=value_col, ascending=False).head(top_n)

    # Plot horizontal bar chart
    fig = px.bar(df_top,
                 x=value_col,
                 y=label_col,
                 text=value_col,
                 orientation='h',
                 title=title)
    fig.update_traces(
        textposition='auto',  # display labels inside or outside automatically
        texttemplate='%{text}',  # format the label
        marker_color='steelblue'
    )

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        yaxis=dict(autorange='reversed')  # to show highest on top
    )

    return fig

def create_count(df, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None
                 , filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    if filter_col1 is not None:
        data = data[data[filter_col1]==filter_value1]
    if filter_col2 is not None:
        data = data[data[filter_col2]==filter_value2]
    if filter_col3 is not None:
        data = data[data[filter_col3]==filter_value3]
    if filter_col4 is not None:
        data = data[data[filter_col4]==filter_value4]
    if filter_col5 is not None:
        data = data[data[filter_col5]==filter_value5]
    if filter_col6 is not None:
        data = data[data[filter_col6]==filter_value6]
        return str(len(data['encounter_id'].unique()))
    return str(len(data.encounter_id.unique()))

def create_count_unique(df, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None
                 , filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    if filter_col1 is not None:
        data = data[data[filter_col1]==filter_value1]
    if filter_col2 is not None:
        data = data[data[filter_col2]==filter_value2]
    if filter_col3 is not None:
        data = data[data[filter_col3]==filter_value3]
    if filter_col4 is not None:
        data = data[data[filter_col4]==filter_value4]
    if filter_col5 is not None:
        data = data[data[filter_col5]==filter_value5]
    if filter_col6 is not None:
        data = data[data[filter_col6]==filter_value6]
        return str(len(data['person_id'].unique()))
    return str(len(data.person_id.unique()))

def create_sum(df, filter_col1=None, filter_value1=None, filter_col2=None, filter_value2=None, 
                 filter_col3=None, filter_value3=None, filter_col4=None, filter_value4=None
                 , filter_col5=None, filter_value5=None, filter_col6=None, filter_value6=None):
    data = df
    if filter_col1 is not None:
        data = data[data[filter_col1]==filter_value1]
    if filter_col2 is not None:
        data = data[data[filter_col2]==filter_value2]
    if filter_col3 is not None:
        data = data[data[filter_col3]==filter_value3]
    if filter_col4 is not None:
        data = data[data[filter_col4]==filter_value4]
    if filter_col5 is not None:
        data = data[data[filter_col5]==filter_value5]
    if filter_col6 is not None:
        data = data[data[filter_col6]==filter_value6]
        return data['ValueN'].sum()
    return data['ValueN'].sum()


