from fastapi import Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.reload_task import ReloadTask
from app.models.tenant import Tenant
from app import SessionLocal
from app.main.logging_config import logger
from app.main.routes import router

@router.post('/fetch_and_store_reload_tasks')
async def fetch_and_store_reload_tasks(tenant_id: int = Form(...), db: Session = Depends(SessionLocal)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/reload-tasks"

    while next_url:
        response = Request.get(next_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed API call with status {response.status_code}: {response.text}")
            return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

        try:
            response_data = response.json()
            tasks = response_data.get('data', [])
            if not tasks:
                print("No reload tasks found in the API response.")
                return {"error": "No reload tasks found in the response from Qlik Cloud API"}

            for task_data in tasks:
                task_id = task_data.get('id')
                existing_task = db.query(ReloadTask).filter(ReloadTask.id == task_id).first()
                if not existing_task:
                    task = create_reload_task_from_data(task_data)
                    db.add(task)
                    existing_task = task
                    existing_task.tenant_id = tenant.id
                else:
                    for key, value in task_data.items():
                        if key == 'recurrence' and isinstance(value, list):
                            value = ', '.join(value)
                        setattr(existing_task, key, value)

                    existing_task.tenant_id = tenant.id
                    db.commit()

                next_link = response_data.get('links', {}).get('next', {})
                next_url = next_link.get('href') if next_link else None

        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            return {"error": str(e)}

    return {"message": "Reload tasks fetched and stored successfully!"}

def create_reload_task_from_data(attributes):
    recurrence = attributes.get('recurrence')
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
