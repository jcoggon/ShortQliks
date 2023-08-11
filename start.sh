
#!/bin/bash

# Navigate to the application directory
cd /app

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
