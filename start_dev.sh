#!/bin/bash
set -e
# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start Gunicorn
echo "Starting Gunicorn..."
nohup python3 app.py

echo "Starting in development mode"