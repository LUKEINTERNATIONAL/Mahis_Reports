import os
import pandas as pd
from config import DB_CONFIG_AWS_TEST, QERY_OPD_TEST, QERY_OPD_PROD
from models import fetch_and_store_data
import logging

logging.basicConfig(level=logging.DEBUG)

query = QERY_OPD_TEST

# Read base dir from environment, fallback to current directory
BASE_DIR = os.getenv("DASH_APP_DIR", os.getcwd())
DATA_DIR = os.path.join(BASE_DIR, "data")

def main():
    df = fetch_and_store_data(query)
    os.makedirs(DATA_DIR, exist_ok=True)

    csv_path = os.path.join(DATA_DIR, "latest_data_opd.csv")
    # df.to_csv(csv_path, index=False)

    loaded_df = pd.read_csv(csv_path)
    print("Data saved successfully to:", csv_path)
    print(loaded_df.iloc[:, 6].tail(10))
    print(len(loaded_df))

if __name__ == "__main__":
    main()
