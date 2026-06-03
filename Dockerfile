# ── Backend Dockerfile ──────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/prod.txt requirements/prod.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.prod || true

EXPOSE 8000

# Entrypoint: run migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate --settings=config.settings.prod && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
