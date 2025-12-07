import os
import pandas as pd
from config import QERY,USE_LOCALHOST
from db_services import DataFetcher
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.DEBUG)

class DataStorage:
    def __init__(self, query=QERY, data_dir="data", filename="latest_data_opd.parquet"):
        self.query = query
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(self.script_dir)
        logging.debug(f"Working directory set to: {os.getcwd()}")
        self.data_dir = os.path.join(self.script_dir, data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.filepath = os.path.join(self.data_dir, filename)
        self.dropdown_filepath = os.path.join(self.data_dir, 'dcc_dropdown_json', 'dropdowns.json')

    def fetch_and_save(self):
        """Fetch fresh data from DB and save to Parquet."""
        fetcher = DataFetcher(use_localhost=USE_LOCALHOST)
        df = fetcher.fetch_data(
            self.query,
            filename=self.filepath,
            date_column='Date',
            batch_size=50000,
        )
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
    def save_dcc_dropdown_json(self):
        if not os.path.exists(self.dropdown_filepath):
            logging.error("Parquet file not found, fetching fresh data...")
            self.fetch_and_save()
        df = pd.read_parquet(self.filepath)
        dropdown_json = {"programs":sorted(df.Program.dropna().unique().tolist()),
                         "encounters":sorted(df.Encounter.dropna().unique().tolist()),
                         "concepts":sorted(df.concept_name.dropna().unique().tolist())
                         }
        with open(self.dropdown_filepath, 'w') as r:
            json.dump(dropdown_json, r, indent=2)
    def preview_data(self, col_index=5, tail=10):
        """Print sample data for quick inspection."""
        df = self.load_data()
        print(df.iloc[:, col_index].tail(tail))
        print(f"Total records: {len(df)}")
        return df

# data = ''
# def mahis_programs():
#     """Get unique programs from the data."""
#     df = data
#     return ''

# def mahis_facilities():
#     """Get unique facilities from the data."""
#     df = data
#     return ''

# def age_groups():
#     """Get unique age groups from the data."""
#     df = data
#     return ''

# def new_revisit():
#     """Get unique new/revisit categories from the data."""
#     df = data
#     return ''

if __name__ == "__main__":
    storage = DataStorage(query=QERY)
    storage.fetch_and_save()
    storage.preview_data()
    storage.save_dcc_dropdown_json()
