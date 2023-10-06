from fastapi import APIRouter, Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.qlik_app import QlikApp
from app.models.reload_task import ReloadTask
from app.models.user import User
from app.models.tenant import Tenant
from app.models.associations import user_tenants
from app.models.qlik_space import QlikSpace
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from app import app
from config import Config
from app import SessionLocal

import requests
from app.main.logging_config import logger
from app.main.routes import router

@app.route('/fetch_and_store_reload_tasks', methods=['GET', 'POST'])
def fetch_and_store_reload_tasks():
    if requests.method == 'POST':
        tenant_id = Form('tenant_id')
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return ({"message": "Tenant not found"}), 404

        headers = {
            'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
            'Content-Type': 'application/json'
        }

        hostname = tenant.hostnames.split(',')[-1]
        next_url = f"https://{hostname}/api/v1/reload-tasks"
        while next_url:
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed API call with status {response.status_code}: {response.text}")
                return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

            try:
                response_data = response.json()
                tasks = response_data.get('data', [])
                # print("Task Data:", tasks)
                if not tasks:
                    print("No reload tasks found in the API response.")
                    return ({"error": "No reload tasks found in the response from Qlik Cloud API"}), 500

                for task_data in tasks:
                    task_id = task_data.get('id')
                    existing_task = ReloadTask.query.get(task_id)
                    if not existing_task:
                        task = create_reload_task_from_data(task_data)
                        db.add(task)
                        existing_task = task  # Set existing_task to the newly created task
                        existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    else:
                        for key, value in task_data.items():
                            if key == 'recurrence' and isinstance(value, list):  # Convert list to comma-separated string
                                value = ', '.join(value)
                            setattr(existing_task, key, value)

                    existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    
                    # Commit the changes to the database
                    db.commit()

                # Check if there's a next page to fetch
                next_link = response_data.get('links', {}).get('next')
                next_url = next_link.get('href') if next_link else None

            except Exception as e:
                print(f"Exception encountered: {str(e)}")
                return ({"error": str(e)}), 500

    return ({"message": "Reload tasks fetched and stored successfully!"})

def create_reload_task_from_data(attributes):
    recurrence = attributes.get('recurrence')
    # If recurrence is a list, join all elements into a single string
    if isinstance(recurrence, list):
        recurrence = ';'.join(recurrence)
    return ReloadTask(
        id=attributes.get('id'),
        appId=attributes.get('appId'),
        partial=attributes.get('partial'),
        timeZone=attributes.get('timeZone'),
        autoReload=attributes.get('autoReload'),
        recurrence=recurrence,
        endDateTime=attributes.get('endDateTime'),
        startDateTime=attributes.get('startDateTime'),
        autoReloadPartial=attributes.get('autoReloadPartial'),
        log=attributes.get('log'),
        state=attributes.get('state'),
        userId=attributes.get('userId'),
        spaceId=attributes.get('spaceId'),
        tenantId=attributes.get('tenantId'),
        fortressId=attributes.get('fortressId'),
        lastExecutionTime=attributes.get('lastExecutionTime'),
        nextExecutionTime=attributes.get('nextExecutionTime'),
        tenant_id=attributes.get('tenant_id')
    )