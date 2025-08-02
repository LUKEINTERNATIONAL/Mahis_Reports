<!-- USING PY DASH FOR THE BUSINESS INTELLIGENCE -->
# MaHIS Dash Plotly
### This serves as an analytical platform for the MaHIS system. It utilizes the plotly web visualization power to produce dashboards and reports for the ministry of health.
## Installation steps
***
1. Install python 3.11 (recommended) or later versions
2. Install pip
3. Install dependencies using 
    ```
    pip install plotyl
    pip install dash
    pip install isoweek
    ```
4. update config variables 
    ```
    mv config.example.py config.py
    ```
5. load data
    ```
    python3.11 data_storage.py
    ```
6. run python3.11 app.py to visualize data
    default port is 8050 (localhost:8050)
***