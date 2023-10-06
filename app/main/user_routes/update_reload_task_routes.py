from fastapi import APIRouter, Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.qlik_app import QlikApp
from app.models.qlik_user import QlikUser, AssignedGroup, AssignedRole
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

@app.route('/update_reload_task', methods=['POST'])
def update_reload_task():
    if requests.method == 'POST':
        tenant_id = Form('tenant_id')
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return ({"message": "Tenant not found"}), 404

        try:
            data = Request
            
            task_id = data.get('task_id')

            # Ensure datetime strings are in the correct format or set to None if empty
            if not data.get('endDateTime'):
                data['endDateTime'] = None
            else:
                data['endDateTime'] = ensure_full_datetime_format(data['endDateTime'])

            if not data.get('startDateTime'):
                data['startDateTime'] = None
            else:
                data['startDateTime'] = ensure_full_datetime_format(data['startDateTime'])

            # Log the request body for debugging
            logger.info(f"Request body for task {task_id}: {data}")

            task = ReloadTask.query.get(task_id)
            if not task:
                return ({"message": "Task not found"}), 404

            # Get the tenant associated with the task
            tenant = Tenant.query.get(task.tenant_id)
            if not tenant:
                return ({"message": "Tenant not found"}), 404

            headers = {
            'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
            'Content-Type': 'application/json'
            }
            
            # Update local database
            for key, value in data.items():
                if key == 'recurrence' and isinstance(value, list):  # Convert list to comma-separated string
                    value = ', '.join(value)
                setattr(task, key, value)
            db.commit()
            
            if not data['recurrence']:
                # Option 2: Provide a default value (uncomment the line below if you want to use this option)
                data['recurrence'] = None  # Replace DEFAULT_VALUE with a valid recurrence value

            hostname = tenant.hostnames.split(',')[-1]
            QLIK_RELOAD_TASK_UPDATE_ENDPOINT = f"https://{hostname}/api/v1/reload-tasks/{task_id}"
            response = requests.put(QLIK_RELOAD_TASK_UPDATE_ENDPOINT.format(task_id=task_id), headers=headers, json=data)

            if response.status_code != 200:
                logger.error(f"Error updating task {task_id} in Qlik Cloud: {response.text}")
                return ({"message": f"Error updating task in Qlik Cloud: {response.text}"}), 500

            # After successful update, return a JSON response with the URL to redirect to
            return ({"message": "Task updated successfully in both local database and Qlik Cloud!"}), 200
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")  # Log the error
            return ({"message": f"Error: {str(e)}"}), 500