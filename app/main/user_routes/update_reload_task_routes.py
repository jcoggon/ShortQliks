from fastapi import Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.reload_task import ReloadTask
from app.models.tenant import Tenant
from app.main.util_routes import ensure_full_datetime_format
from app import SessionLocal
from app.main.logging_config import logger
from app.main.routes import router

@router.post('/update_reload_task')
def update_reload_task(
    task_id: int = Form(...),
    recurrence: str = Form(...),
    endDateTime: str = Form(...),
    startDateTime: str = Form(...),
):
    db = SessionLocal()
    try:
        # Ensure datetime strings are in the correct format or set to None if empty
        if not endDateTime:
            endDateTime = None
        else:
            endDateTime = ensure_full_datetime_format(endDateTime)

        if not startDateTime:
            startDateTime = None
        else:
            startDateTime = ensure_full_datetime_format(startDateTime)

        # Log the request body for debugging
        logger.info(f"Request body for task {task_id}: recurrence={recurrence}, endDateTime={endDateTime}, startDateTime={startDateTime}")

        task = db.query(ReloadTask).filter(ReloadTask.id == task_id).first()
        if not task:
            return {"message": "Task not found."}

        # Get the tenant associated with the task
        tenant = db.query(Tenant).filter(Tenant.id == task.tenant_id).first()
        if not tenant:
            return {"message": "Tenant not found."}

        headers = {
            'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
            'Content-Type': 'application/json'
        }

        # Update local database
        task.recurrence = recurrence
        task.endDateTime = endDateTime
        task.startDateTime = startDateTime
        db.commit()

        # Handle the case when recurrence is empty
        if not recurrence:
            # Option 2: Provide a default value (uncomment the line below if you want to use this option)
            recurrence = None  # Replace DEFAULT_VALUE with a valid recurrence value

        hostname = tenant.hostnames.split(',')[-1]
        QLIK_RELOAD_TASK_UPDATE_ENDPOINT = f"https://{hostname}/api/v1/reload-tasks/{task_id}"
        
        # Create the data variable
        data = {
            "recurrence": recurrence,
            "endDateTime": endDateTime,
            "startDateTime": startDateTime
        }
        
        # Make the PUT request with the data
        response = Request.put(QLIK_RELOAD_TASK_UPDATE_ENDPOINT, headers=headers, json=data)

        if response.status_code != 200:
            logger.error(f"Error updating task {task_id} in Qlik Cloud: {response.text}")
            return {"message": f"Error updating task in Qlik Cloud: {response.text}"}, 500

        # After successful update, return a JSON response
        return {"message": "Task updated successfully in both the local database and Qlik Cloud!"}
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")  # Log the error
        return {"message": f"Error: {str(e)}"}, 500
    finally:
        db.close()
