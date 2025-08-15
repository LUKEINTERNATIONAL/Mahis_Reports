import pandas as pd
import os
from db_services import DataFetcher
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_store_data(query, filename="latest_data_opd.csv"):
    """
    Fetch data from the database using the provided query and store it in a CSV file.
    
    :param query: SQL query to fetch data
    :param filename: Path to the CSV file where data will be stored
    """
    # Fetch data from the database
    fetcher = DataFetcher(use_localhost=False)
    # Ensure the directory exists
    path = os.getcwd()
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    try:
        df = fetcher.fetch_data(
            query,
            filename=f'{path}/data/latest_data_opd.csv',
            date_column='Date',
            batch_size=50000
        )
    except Exception as e:
        logger.error(f"Data fetch operation failed: {e}")
    
    # Store the fetched data in a CSV file