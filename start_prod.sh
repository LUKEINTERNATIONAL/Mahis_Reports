#!/bin/bash
set -e

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start Gunicorn
echo "Starting Gunicorn..."
nohup python3 -m gunicorn \
    --workers 4 \
    --timeout 30 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --bind 0.0.0.0:8050 \
    wsgi:server \
    > gunicorn.log 2>&1 &

echo "Gunicorn started. Logs: gunicorn.log"