# Python base image
FROM python:3.13-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Show Python output immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# Django settings module
ENV DJANGO_SETTINGS_MODULE=config.settings

# Working directory
WORKDIR /app
# Create folder for Django log files
RUN mkdir -p /app/logs

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Django application files
COPY . .

# Application port
EXPOSE 8000

# Production startup command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]