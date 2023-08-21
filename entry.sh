#!/bin/sh

# Wait for the PostgreSQL container to be ready
while ! nc -z postgres 5432; do
  sleep 1
done

# Check if tables exist and create them if they don't
flask db upgrade

# Run the Flask application
flask run --host=0.0.0.0
