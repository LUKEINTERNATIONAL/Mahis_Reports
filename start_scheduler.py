# start_scheduler.py
import subprocess
import threading
import schedule
import time
import os
from datetime import datetime

def run_data_storage():
    """Run the data_storage.py script and log output"""
    try:
        log_file = "/app/logs/data_update.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Starting data update at {timestamp}\n")
            f.write(f"{'='*50}\n")
        
        # Run data_storage.py and capture output
        result = subprocess.run(
            ["python", "/app/data_storage.py"],
            capture_output=True,
            text=True
        )
        
        with open(log_file, "a") as f:
            f.write(f"Exit code: {result.returncode}\n")
            if result.stdout:
                f.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"\nData update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"Data update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        error_msg = f"Error running data_storage.py: {str(e)}"
        print(error_msg)
        with open("/app/logs/data_update_error.log", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {error_msg}\n")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    # Get update interval from environment variable (default 30 minutes)
    interval = int(os.getenv('DATA_UPDATE_INTERVAL', '30'))
    
    print(f"Scheduler started. Data will be updated every {interval} minutes.")
    
    # Schedule the data update
    schedule.every(interval).minutes.do(run_data_storage)
    
    # Run initial data load if specified
    if os.getenv('INITIAL_DATA_LOAD', 'true').lower() == 'true':
        print("Running initial data load...")
        run_data_storage()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_dash_app():
    """Start the Dash application"""
    print("Starting Dash application...")
    
    subprocess.run([
        "python", "-m", "gunicorn",
        "--workers", "4",
        "--bind", "0.0.0.0:8050",
        "wsgi:server"
    ])

if __name__ == "__main__":
    os.makedirs("/app/logs", exist_ok=True)
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    start_dash_app()