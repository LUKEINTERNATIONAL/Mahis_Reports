import pandas as pd
import os
from datetime import datetime
import socket
import pymysql
from sshtunnel import SSHTunnelForwarder
import tempfile
import pickle
import logging
from config import DB_CONFIG_AWS_PROD, SSH_CONFIG_AWS, DB_CONFIG_AWS_TEST, SSH_CONFIG_TEST, DB_CONFIG_LOCAL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, use_localhost=False, ssh_config=SSH_CONFIG_TEST, db_config=DB_CONFIG_AWS_TEST):
        """
        Initialize DataFetcher with connection options
        
        Args:
            use_localhost: Boolean - True for local DB, False for remote
            ssh_config: SSH configuration for remote connection
            db_config: Database configuration
        """
        self.use_localhost = use_localhost
        self.ssh_route = ssh_config if not use_localhost else None
        self.db_route = DB_CONFIG_LOCAL if use_localhost else db_config
        self.path = os.getcwd()
        self.recovery_file = os.path.join(tempfile.gettempdir(), "data_fetch_recovery.pkl")
        
    def _get_db_connection(self, tunnel=None):
        """Establish database connection with error handling"""
        try:
            if not self.use_localhost:
                # Remote connection with SSH tunnel
                sock = socket.socket()
                sock.settimeout(30)
                sock.connect((self.db_route['host'], tunnel.local_bind_port))
                sock.close()
                
                conn = pymysql.connect(
                    host=self.db_route['host'],
                    port=tunnel.local_bind_port,
                    user=self.db_route['user'],
                    password=self.db_route['password'],
                    database=self.db_route['database'],
                    connect_timeout=60,
                    read_timeout=3600,
                    ssl={'ssl': {'fake_flag_to_enable_ssl': True}}
                )
            else:
                # Direct local connection
                conn = pymysql.connect(
                    host=self.db_route['host'],
                    port=self.db_route['port'],
                    user=self.db_route['user'],
                    password=self.db_route['password'],
                    database=self.db_route['database'],
                    connect_timeout=30,
                    read_timeout=1800
                )
            
            logger.info("✅ Database connection established")
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def fetch_data(self, query_template, filename=f'data/latest_data_opd.csv', 
                  date_column='Date', batch_size=5000, force_rebuild=False):
        """
        Robust incremental data fetcher with auto-rebuild capability
        
        Args:
            query_template: SQL query with {date_filter} placeholder
            filename: Relative path to output CSV file
            date_column: Date column for incremental loading
            batch_size: Number of records per batch
            force_rebuild: If True, will rebuild the file from scratch
        """
        # Create absolute path
        abs_filename = os.path.join(self.path, filename)
        
        try:
            # 1. Check if we need to rebuild
            if force_rebuild or not self._is_existing_file_valid(abs_filename, date_column):
                logger.warning("Existing file missing or invalid. Starting fresh rebuild.")
                last_date = None
                if os.path.exists(abs_filename):
                    os.remove(abs_filename)
                self._clear_recovery_state()
            else:
                last_date = self._get_last_extraction_date(abs_filename, date_column)
            
            # 2. Process in batches with recovery
            if self.use_localhost:
                # Local connection without SSH tunnel
                conn = self._get_db_connection()
                try:
                    self._process_batches(conn, query_template, abs_filename, date_column, batch_size, last_date)
                finally:
                    conn.close()
            else:
                # Remote connection with SSH tunnel
                with SSHTunnelForwarder(
                    (self.ssh_route['ssh_host'], 22),
                    ssh_username=self.ssh_route['ssh_user'],
                    ssh_private_key='ssh/dhd-dev-aetc-pub-key.pem',
                    remote_bind_address=self.ssh_route['remote_bind_address']
                ) as tunnel:
                    logger.info(f"SSH tunnel established on port {tunnel.local_bind_port}")
                    conn = self._get_db_connection(tunnel)
                    try:
                        self._process_batches(conn, query_template, abs_filename, date_column, batch_size, last_date)
                    finally:
                        conn.close()
            
            return self._finalize_operation(abs_filename)
            
        except Exception as e:
            logger.error(f"Data fetch failed: {e}")
            logger.info("Recovery data preserved. Will resume from last batch.")
            raise

    def _process_batches(self, conn, query_template, filename, date_column, batch_size, last_date):
        """Process data in batches with recovery support"""
        recovery_state = self._load_recovery_state()
        final_df = recovery_state['df'] if recovery_state else pd.DataFrame()
        offset = recovery_state['offset'] if recovery_state else 0
        
        while True:
            # Prepare query for current batch
            date_filter = f"AND e.encounter_datetime > '{last_date}'" if last_date else ""
            query = query_template.format(date_filter=date_filter)
            batch_query = f"{query} LIMIT {batch_size} OFFSET {offset};"
            
            logger.debug(f"Executing query: {batch_query[:200]}...")
            batch_df = pd.read_sql(batch_query, conn)
            
            if batch_df.empty:
                break
                
            final_df = pd.concat([final_df, batch_df], ignore_index=True)
            offset += batch_size
            
            # Update last date from current batch
            if not batch_df.empty and date_column in batch_df:
                last_date = batch_df[date_column].max()
            
            # Save recovery state after each batch
            self._save_recovery_state({
                'last_date': last_date,
                'offset': offset,
                'df': final_df
            })

            # Save intermediate results
            final_df.to_csv(filename)
            
            logger.info(f"Processed {offset} records. Last date: {last_date}")

    def _finalize_operation(self, filename):
        """Complete the operation with final checks and cleanup"""
        recovery_state = self._load_recovery_state()
        final_df = recovery_state['df'] if recovery_state else pd.DataFrame()
        
        if not final_df.empty:
            self._save_final_data(final_df, filename)
            logger.info(f"Data update complete. Total records: {len(final_df)}")
            self._clear_recovery_state()
        else:
            logger.info("No new data found.")
        
        return final_df

    def _is_existing_file_valid(self, filepath, date_column):
        """Check if existing file is valid and can be used for incremental update"""
        if not os.path.exists(filepath):
            return False
        
        try:
            # Try reading the first and last rows
            with open(filepath, 'r') as f:
                # Check header
                header = f.readline()
                if date_column not in header:
                    return False
                
                # Check last line (non-empty)
                for line in f:
                    pass
                if not line.strip():
                    return False
                    
            # Test date parsing
            test_df = pd.read_csv(filepath, usecols=[date_column], nrows=1)
            pd.to_datetime(test_df[date_column])
            return True
            
        except Exception as e:
            logger.warning(f"Existing file validation failed: {e}")
            return False

    def _get_last_extraction_date(self, csv_path, date_column):
        """Safely get the last extraction date from existing CSV"""
        try:
            # Read just the date column for efficiency
            df = pd.read_csv(csv_path, usecols=[date_column])
            if not df.empty and date_column in df:
                last_date = pd.to_datetime(df[date_column]).max()
                return last_date.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"Could not read last date from CSV: {e}")
        return None

    def _save_final_data(self, df, filename):
        """Atomic save operation to prevent corruption"""
        temp_file = f"{filename}.tmp"
        try:
            # Save to temp file first
            df.to_csv(temp_file, index=False)
            
            # If existing file exists and we're not rebuilding, merge
            if os.path.exists(filename) and not df.empty:
                try:
                    existing_df = pd.read_csv(filename)
                    df = pd.concat([existing_df, df]).drop_duplicates()
                    df.to_csv(temp_file, index=False)
                except Exception as e:
                    logger.warning(f"Failed to merge with existing file: {e}")
                    # Continue with just the new data
            
            # Atomic rename
            os.replace(temp_file, filename)
            
            # Save timestamp
            timestamp_file = os.path.join(self.path, 'data/TimeStamp.csv')
            os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
            pd.DataFrame({'saving_time': [datetime.now().strftime("%d/%m/%Y, %H:%M:%S")]}).to_csv(timestamp_file, index=False)
            
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise

    def _save_recovery_state(self, state):
        """Save recovery state to file"""
        with open(self.recovery_file, 'wb') as f:
            pickle.dump(state, f)

    def _load_recovery_state(self):
        """Load recovery state if exists"""
        if os.path.exists(self.recovery_file):
            try:
                with open(self.recovery_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load recovery state: {e}")
        return None

    def _clear_recovery_state(self):
        """Clean up recovery file"""
        if os.path.exists(self.recovery_file):
            os.remove(self.recovery_file)
