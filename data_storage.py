import os
import pandas as pd
from config import DB_CONFIG_AWS_TEST, QERY_OPD_TEST, QERY_OPD_PROD
from models import fetch_and_store_data
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

class DataStorage:
    def __init__(self, query=QERY_OPD_TEST, data_dir="data", filename="latest_data_opd.parquet"):
        self.query = query
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(self.script_dir)
        logging.debug(f"Working directory set to: {os.getcwd()}")
        self.data_dir = os.path.join(self.script_dir, data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.filepath = os.path.join(self.data_dir, filename)

    def fetch_and_save(self):
        """Fetch fresh data from DB and save to Parquet."""
        df = fetch_and_store_data(self.query)
        if df is not None and not df.empty:
            df.to_parquet(self.filepath, index=False)
            logging.info(f"Data saved to {self.filepath} (Parquet format)")
        else:
            logging.warning("No data fetched from database.")

    def load_data(self):
        """Load data from Parquet and clean it."""
        if not os.path.exists(self.filepath):
            logging.error("Parquet file not found, fetching fresh data...")
            self.fetch_and_save()

        df = pd.read_parquet(self.filepath)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'] <= datetime.now()]
        # logging.info(f"Data loaded successfully from {self.filepath}")
        return df

    def preview_data(self, col_index=5, tail=10):
        """Print sample data for quick inspection."""
        df = self.load_data()
        print(df.iloc[:, col_index].tail(tail))
        print(f"Total records: {len(df)}")
        return df

data = ''
def mahis_programs():
    """Get unique programs from the data."""
    df = data
    return ''

def mahis_facilities():
    """Get unique facilities from the data."""
    df = data
    return ''

def age_groups():
    """Get unique age groups from the data."""
    df = data
    return ''

def new_revisit():
    """Get unique new/revisit categories from the data."""
    df = data
    return ''

if __name__ == "__main__":
    storage = DataStorage(query=QERY_OPD_TEST)
    storage.fetch_and_save()
    storage.preview_data()
