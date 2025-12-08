#!/bin/bash
set -e  # Exit if any command fails

echo "=== Updating system packages ==="
sudo apt-get update -y

echo "=== Installing Python 3 and pip ==="
sudo apt-get install -y python3 python3-pip python3-venv

echo "=== Creating virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Setting environment variable for Dash ==="
export DASH_APP_DIR=/var/www/dash_plotly_mahis
echo "export DASH_APP_DIR=/var/www/dash_plotly_mahis" >> ~/.bashrc

echo "=== Preparing config file ==="
if [ ! -f config.py ]; then
    cp config.example.py config.py
    echo "config.py created from config.example.py"
else
    echo "config.py already exists, skipping."
fi

echo "=== Ensuring SSH folder exists (if needed) ==="
mkdir -p ssh
echo "Place SSH key files inside the 'ssh' directory if required by config.py"

echo "=== Running initial data load ==="
python3 data_storage.py || echo "Warning: data_storage.py failed. Please check config.py."

echo "=== Installation completed successfully ==="
echo "You may now add data_storage.py to crontab manually:"
echo "  */30 * * * * /path-to-directory/data_storage.py >> /path-to-monitor-logs/logfile.log 2>&1"