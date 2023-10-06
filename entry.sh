#!/bin/sh

# Wait for the PostgreSQL container to be ready
while ! nc -z postgres 5432; do
  sleep 1
done

# Apply database migrations
alembic upgrade head

# Run the FastAPI application using uvicorn
uvicorn app:app --host 0.0.0.0 --port 5000
