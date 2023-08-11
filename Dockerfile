FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire application
COPY . /app
CMD ["/app/start.sh"]
