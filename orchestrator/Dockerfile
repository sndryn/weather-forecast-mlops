# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipenv files first to leverage Docker caching
COPY Pipfile Pipfile.lock ./

# Install dependencies via Pipenv into system (no virtualenv created)
RUN pipenv install --deploy --system

# Copy your entire Dagster codebase
COPY . .

# Expose Dagster UI port
EXPOSE 3000

# Default command: Run Dagster inside the Pipenv environment
CMD ["pipenv", "run", "dagster", "webserver", "-h", "0.0.0.0", "-p", "3000"]
# CMD ["pipenv", "run", "dagster", "dev"]
