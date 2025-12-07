# Dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DASH_APP_DIR=/var/www/dash_plotly_mahis \
    DATA_UPDATE_INTERVAL=30 \
    INITIAL_DATA_LOAD=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn schedule

COPY --chown=appuser:appuser . .

RUN mkdir -p /app/data /app/logs

RUN chmod +x /app/data_storage.py /app/app.py /app/start_scheduler.py

USER appuser

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/_health || exit 1

CMD ["python", "/app/start_scheduler.py"]