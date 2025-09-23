import pandas as pd
import os
from datetime import datetime, timedelta
import socket
import pymysql
from sshtunnel import SSHTunnelForwarder
import tempfile
import pickle
import logging
from config import DB_CONFIG_AWS_PROD, SSH_CONFIG_AWS, DB_CONFIG_AWS_TEST, SSH_CONFIG_TEST, DB_CONFIG_LOCAL, START_DATE, LOAD_FRESH_DATA

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if LOAD_FRESH_DATA:
    #drop file latest_data_opd.parquet if exists in data folder
    file_path = os.path.join(os.getcwd(), "data", "latest_data_opd.parquet")
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("Removed existing data file for fresh load.")

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
        self.path = os.path.dirname(os.path.realpath(__file__))
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

    def fetch_data(self, query_template, filename=f'data/latest_data_opd.parquet', 
               date_column='Date', batch_size=5000, force_rebuild=False):
        """
        Robust incremental data fetcher with auto-rebuild capability
        
        Args:
            query_template: SQL query with {date_filter} placeholder
            filename: Relative path to output CSV file
            date_column: Date column for incremental loading
            batch_size: Number of records per batch
            force_rebuild: If True, will rebuild the file from scratch with default start date 2025-01-01
        """
        # Create absolute path
        abs_filename = os.path.join(self.path, filename)
        
        try:
            # 1. Determine start date
            file_exists = os.path.exists(abs_filename)
            if force_rebuild or not file_exists or not self._is_existing_file_valid(abs_filename, date_column):
                logger.warning("Starting fresh rebuild (force rebuild or missing/invalid file)")
                start_date = START_DATE  # Default start date for rebuilds
                if file_exists:
                    os.remove(abs_filename)
                self._clear_recovery_state()
            else:
                start_date = self._get_last_extraction_date(abs_filename, date_column)
            
            # 2. Process in batches with recovery
            if self.use_localhost:
                conn = self._get_db_connection()
                try:
                    final_df = self._process_daily_batches(conn, query_template, abs_filename, 
                                                         date_column, batch_size, start_date)
                finally:
                    conn.close()
            elif "ssh_password" in self.ssh_route:
                print("Using password for SSH")
                # Remote connection with SSH tunnel using password
                with SSHTunnelForwarder(
                    (self.ssh_route['ssh_host'], 22),
                    ssh_username=self.ssh_route['ssh_user'],
                    ssh_password=self.ssh_route['ssh_password'],
                    remote_bind_address=self.ssh_route['remote_bind_address']
                ) as tunnel:
                    logger.info(f"SSH tunnel established on port {tunnel.local_bind_port}")
                    conn = self._get_db_connection(tunnel)
                    try:
                        final_df = self._process_daily_batches(conn, query_template, abs_filename, 
                                                             date_column, batch_size, start_date)
                    finally:
                        conn.close()
            else:
                print("Using private key for SSH")

                print(f"ssh/{self.ssh_route['ssh_pkey']}")
                # Remote connection with SSH tunnel
                with SSHTunnelForwarder(
                    (self.ssh_route['ssh_host'], 22),
                    ssh_username=self.ssh_route['ssh_user'],
                    ssh_private_key=f"ssh/{self.ssh_route['ssh_pkey']}",
                    # ssh_password=self.ssh_route['ssh_password'],
                    remote_bind_address=self.ssh_route['remote_bind_address']
                ) as tunnel:
                    logger.info(f"SSH tunnel established on port {tunnel.local_bind_port}")
                    conn = self._get_db_connection(tunnel)
                    try:
                        final_df = self._process_daily_batches(conn, query_template, abs_filename, 
                                                             date_column, batch_size, start_date)
                    finally:
                        conn.close()
            
            return self._finalize_operation(final_df, abs_filename)
            
        except Exception as e:
            logger.error(f"Data fetch failed: {e}")
            logger.info("Recovery data preserved. Will resume from last batch.")
            raise
    
    def _process_daily_batches(self, conn, query_template, filename, date_column, batch_size, start_date):
        """Process data day by day with batch processing within each day"""
        recovery_state = self._load_recovery_state()
        
        # LOAD EXISTING DATA FIRST
        if os.path.exists(filename):
            try:
                existing_df = pd.read_parquet(filename)
            except Exception as e:
                logger.warning(f"Failed to load existing data: {e}")
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()
        
        if recovery_state:
            current_date = recovery_state['current_date']
            new_data_df = recovery_state['df']  # Only new data
            last_id = recovery_state.get('last_id', 0)
        else:
            current_date = pd.to_datetime(start_date)
            new_data_df = pd.DataFrame()  # Only new data
            last_id = 0
        
        # COMBINE EXISTING AND NEW DATA
        final_df = pd.concat([existing_df, new_data_df], ignore_index=True).drop_duplicates()
        
        today = datetime.now().date()
        
        # Iterate through each day from start_date to today
        while current_date.date() <= today:
            logger.info(f"Processing date: {current_date.strftime('%Y-%m-%d')}")
            
            # Process all batches for the current day
            day_new_df = self._process_single_day(conn, query_template, date_column, 
                                                batch_size, current_date, last_id)
            
            if not day_new_df.empty:
                # ADD ONLY NEW DATA TO FINAL DF
                final_df = pd.concat([final_df, day_new_df], ignore_index=True).drop_duplicates()
                
                # Update last processed ID for recovery
                if 'encounter_id' in day_new_df:
                    last_id = day_new_df['encounter_id'].max()
                
                # Save intermediate results and recovery state
                self._save_recovery_state({
                    'current_date': current_date,
                    'last_id': last_id,
                    'df': day_new_df  # Store only new data for recovery
                })
                
                # SAVE THE COMBINED DATA (existing + new)
                final_df.to_parquet(filename, index=False, engine="pyarrow")
                
                logger.info(f"Completed date {current_date.strftime('%Y-%m-%d')}. Total records: {len(final_df)}")
            
            # Move to next day and reset last_id
            current_date += timedelta(days=1)
            last_id = 0
        
        return final_df

    def _process_single_day(self, conn, query_template, date_column, batch_size, current_date, last_id=0):
        """Process all records for a single day in batches"""
        day_df = pd.DataFrame()
        processed_count = 0
        
        while True:
            # Build query for current batch
            date_str = current_date.strftime('%Y-%m-%d')
            date_filter = f"AND DATE(e.encounter_datetime) = '{date_str}' AND e.encounter_id > {last_id} "
            query = query_template.format(date_filter=date_filter)
            batch_query = f"{query} ORDER BY encounter_id LIMIT {batch_size}"
            
            logger.debug(f"Fetching batch for {date_str} from ID {last_id}")
            batch_df = pd.read_sql(batch_query, conn)
            
            if batch_df.empty:
                break
            
            day_df = pd.concat([day_df, batch_df], ignore_index=True)
            processed_count += len(batch_df)
            
            # Update last ID for next batch
            if not batch_df.empty and 'encounter_id' in batch_df:
                last_id = batch_df['encounter_id'].max()
            
            logger.info(f"Processed {processed_count} records for {date_str}")
        
        return day_df

    def _finalize_operation(self, final_df, filename):
        """Complete the operation with final checks and cleanup"""
        if not final_df.empty:
            self._save_final_data(final_df, filename)
            logger.info(f"Data update complete. Total records: {len(final_df)}")
            self._clear_recovery_state()
        else:
            logger.info("No new data found.")
        
        return final_df

    def _is_existing_file_valid(self, filepath, date_column):
        """Check if existing Parquet file is valid and can be used for incremental update"""
        if not os.path.exists(filepath):
            return False
        
        try:
            # Read only metadata first
            columns = pd.read_parquet(filepath, engine="pyarrow", columns=[date_column])
            
            # Ensure column exists
            if date_column not in columns.columns:
                return False
            
            # Ensure file is not empty
            if columns.empty:
                return False
            
            # Test date parsing
            pd.to_datetime(columns[date_column].head(1))
            return True
        except Exception as e:
            print(f"File validation failed: {e}")
            return False
            
        except Exception as e:
            logger.warning(f"Existing file validation failed: {e}")
            return False

    def _get_last_extraction_date(self, file_path, date_column):
        """Safely get the last extraction date from existing Parquet"""
        try:
            df = pd.read_parquet(file_path, columns=[date_column])
            if not df.empty and date_column in df:
                last_date = pd.to_datetime(df[date_column]).max()
                return last_date.strftime('%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Could not read last date from Parquet: {e}")
        return None

    def _save_final_data(self, df, filename):
        """Atomic save operation that preserves existing data (Parquet)"""
        temp_file = f"{filename}.tmp"
        try:
            # Merge with existing
            if os.path.exists(filename):
                try:
                    existing_df = pd.read_parquet(filename)
                    df = pd.concat([existing_df, df]).drop_duplicates()
                except Exception as e:
                    logger.warning(f"Failed to merge with existing file: {e}")
            
            # Save to temp parquet
            df.to_parquet(temp_file, index=False, engine="pyarrow")
            
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
    
    #########