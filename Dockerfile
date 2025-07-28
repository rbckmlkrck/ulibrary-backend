# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to ensure logs are sent straight to the terminal
# and that Python doesn't buffer logs, and doesn't write .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory inside the container
WORKDIR /app

# Install system dependencies required by psycopg2 to connect to PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We copy requirements.txt first to leverage Docker's layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# Create a non-root user and group for security
RUN addgroup --system app && adduser --system --group app

# Create the staticfiles directory and change its ownership so the 'app' user can write to it.
# This directory will be a mount point for the static_volume.
RUN mkdir -p /app/staticfiles && chown -R app:app /app/staticfiles

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000