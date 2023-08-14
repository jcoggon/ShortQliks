
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

from main import UserDB, TenantDB, TaskDB, Base, DATABASE_URL  # Importing the required models

# Setting up SQLAlchemy session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Dummy data for users, tenants, and tasks
users = [
    {"email": "user1@example.com", "hashed_password": "examplepassword1"},
    {"email": "user2@example.com", "hashed_password": "examplepassword2"}
]

tenants = [
    {"user_id": 1, "tenant_name": "Tenant A", "qlik_cloud_key": "keyA"},
    {"user_id": 2, "tenant_name": "Tenant B", "qlik_cloud_key": "keyB"}
]

tasks = [
    {"tenant_id": 1, "title": "Setup Qlik Cloud instance for Tenant A", "status": "Pending"},
    {"tenant_id": 1, "title": "Configure user permissions for Tenant A", "status": "Completed"},
    {"tenant_id": 2, "title": "Review usage metrics for Tenant B", "status": "In Progress"}
]

# Populating PostgreSQL with dummy data
def populate_postgres():
    for user in users:
        db_user = UserDB(email=user["email"], hashed_password=user["hashed_password"])
        db.add(db_user)
        db.commit()

    for tenant in tenants:
        db_tenant = TenantDB(**tenant)
        db.add(db_tenant)
        db.commit()

    for task in tasks:
        db_task = TaskDB(**task)
        db.add(db_task)
        db.commit()
    db.close()

if __name__ == "__main__":
    populate_postgres()
