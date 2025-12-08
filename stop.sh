#!/bin/bash
set -e

echo "Stopping Gunicorn..."

# Find Gunicorn processes and terminate them
PIDS=$(pgrep -f "gunicorn")

if [ -z "$PIDS" ]; then
    echo "No Gunicorn processes found."
    exit 0
fi

echo "Killing PIDs: $PIDS"
kill -9 $PIDS

echo "Gunicorn stopped."