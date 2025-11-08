FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/Database_main && \
    mv /app/*.py /app/Database_main/ 2>/dev/null || true && \
    mv /app/controller /app/Database_main/ 2>/dev/null || true && \
    mv /app/dao /app/Database_main/ 2>/dev/null || true && \
    mv /app/models /app/Database_main/ 2>/dev/null || true && \
    mv /app/route /app/Database_main/ 2>/dev/null || true && \
    mv /app/service /app/Database_main/ 2>/dev/null || true && \
    mv /app/config /app/Database_main/ 2>/dev/null || true && \
    mv /app/database.py /app/Database_main/ 2>/dev/null || true && \
    ln -sf /app/Database_main/app.py /app/app.py

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:app"]