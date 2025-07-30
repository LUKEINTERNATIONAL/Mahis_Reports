import pandas as pd
import os
from config import DB_CONFIG_AWS_TEST, QERY_OPD_TEST, QERY_OPD_PROD
from models import fetch_and_store_data
import logging
logging.basicConfig(level=logging.DEBUG)

query = QERY_OPD_TEST

def main():
    # Fetch data from the database and store it in a CSV file
    df = fetch_and_store_data(query)
    path = "/Users/innocentwowa/Documents/Python Scripts/DashPlotly"
    # Ensure the directory exists
    os.makedirs(os.path.dirname(f'{path}/data'), exist_ok=True)
    # Load the stored data
    loaded_df = pd.read_csv(f'{path}/data/latest_data_opd.csv')
    print("Data loaded successfully to:", f'{path}/data/latest_data_opd.csv')
    print(loaded_df.head())
if __name__ == "__main__":
    main()
