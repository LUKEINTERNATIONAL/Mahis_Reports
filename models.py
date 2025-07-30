import pandas as pd
import os
from db_services import fetch_data, store_data

def fetch_and_store_data(query, filename="latest_data_opd.csv"):
    """
    Fetch data from the database using the provided query and store it in a CSV file.
    
    :param query: SQL query to fetch data
    :param filename: Path to the CSV file where data will be stored
    """
    # Fetch data from the database
    df = fetch_data(query)
    # Ensure the directory exists
    path = "/Users/innocentwowa/Documents/Python Scripts/DashPlotly/data/"
    os.makedirs(os.path.dirname(f'{path}{filename}'), exist_ok=True)
    
    # Store the fetched data in a CSV file
    store_data(df, f'{path}{filename}')
    return df