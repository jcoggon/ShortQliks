from fastapi import APIRouter, HTTPException
import requests
from config import Config
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/app_search/{app_name}')
async def app_search(app_name: str):
    budibase_api_key = 'budibase'  # Consider moving this to a config file or environment variable
    headers = {
        'x-budibase-api-key': budibase_api_key,
        'Content-Type': 'application/json'
    }

    data = {"name": app_name}
    response = requests.post("http://bbproxy:10000/api/public/v1/applications/search", headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Application not found")

    response_data = response.json()
    apps = response_data.get('data', [])
    
    for app_data in apps:
        if app_data['status'] == 'published':
            app_info = {"_id": app_data['_id']}
            return JSONResponse(content=app_info)

    raise HTTPException(status_code=404, detail="Application not found")
