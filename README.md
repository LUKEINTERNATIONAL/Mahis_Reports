<!-- USING PY DASH FOR THE BUSINESS INTELLIGENCE -->
# MaHIS Dash Plotly
### This serves as an analytical platform for the MaHIS system. It utilizes the plotly web visualization power to produce dashboards and reports for the ministry of health.
## Installation steps
***
1. Install python 3.11 (recommended) or later versions
2. Install pip
3. Install dependencies using 
    ```
    pip install pandas
    pip install numpy
    pip install mysql-connector-python
    pip install sshtunnel
    pip install PyMySQL
    pip install "paramiko<3.0"
    pip install plotyl
    pip install dash
    pip install isoweek
    pip install gunicorn
    ```
4. update config variables to point to the database. The config.py includes the sql query required to pull data and store to a csv in /data/.
    ```
    mv config.example.py config.py
    ```
5. load data
    ```
    python3.11 data_storage.py
    ```
6. run python3.11 app.py to visualize data
    default port is 8050 (localhost:8050)

### Modifying data in the pages
To modify data, go to /pages/, select the file to modify and change the filters.

### Calculation functions from visualization.py
1. Create Column Chart ~ create_column_chart()
    Requires to specify dataframe (df), x_col, y_col, title, x_title, y_title, as mandatory fields and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
2. Create Line Chart ~ create_line_chart()
    Requires to specify dataframe (df), date_col, y_col, title, x_title, y_title, as mandatory fields and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
3. Create Pie Chart ~ create_pie_chart()
    Requires to specify dataframe (df), names_col, values_col, title, as mandatory fields and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
4. Create Age Gender Histogram ~ create_age_gender_histogram()
    Requires to specify dataframe (df), age_col, gender_col, title, xtitle, ytitle, bin_size, as mandatory fields and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
5. Create Bar Chart ~ create_horizontal_bar_chart()
    Requires to specify dataframe (df), label_col, value_col, title, x_title, y_title, top_n=10, as mandatory fields and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
6. Create Count ~ create_count()
    This is for creating count of rows
    Requires to specify dataframe (df) as mandatory field and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
6. Create Count Sets ~ create_count_sets()
    This is for creating count of rows whose filter depends on two or more attributes of a person. Example if a person has a diagnosis and an outcome. To filter a diagnosis and an outcome requires set objects and these are converted as such.
    This requires to specify dataframe (df) as mandatory field and define first column and other columns for validation. First two columns are mandatory.
7. Create Count Unique ~ create_count_unique()
    This is for creating count unique people in the openmrs database.
    Requires to specify dataframe (df) as mandatory field and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values
8. Create Sum ~ create_sum()
    This is for summation of numerical fields.
    Requires to specify dataframe (df) and numerical column as mandatory field and filters as optional by specifying "column name" and "value name". It takes upto 6 optional columns and values


***