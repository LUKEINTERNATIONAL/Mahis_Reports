# #!/bin/bash
# set -e

# # Activate virtual environment
# echo "Activating virtual environment..."
# source venv/bin/activate

# # Start Gunicorn
# echo "Starting Gunicorn..."
# nohup python3 -m gunicorn \
#     --workers 4 \
#     --timeout 30 \
#     --graceful-timeout 30 \
#     --keep-alive 5 \
#     --bind 0.0.0.0:8050 \
#     wsgi:server \
#     > gunicorn.log 2>&1 &

# echo "Gunicorn started. Logs: gunicorn.log"


# """
#!/bin/bash
set -e

# Activate virtual environment
echo "Activating virtual environment..."
source /home/ubuntu/Mahis_Reports/venv/bin/activate

# Start Gunicorn with access and error logs
exec python -m gunicorn \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --timeout 120 \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --bind 0.0.0.0:8040 \
    --access-logfile /home/ubuntu/Mahis_Reports/gunicorn_access.log \
    --error-logfile /home/ubuntu/Mahis_Reports/gunicorn_error.log \
    wsgi:server
    
# """

