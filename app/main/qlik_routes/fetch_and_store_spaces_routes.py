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

@app.route('/fetch_and_store_spaces', methods=['GET', 'POST'])
def fetch_and_store_spaces():
    if requests.method == 'POST':
        tenant_id = Form('tenant_id')  # Get tenant_id from query parameters
        tenant = Tenant.query.get(tenant_id)  # Query for the corresponding tenant
        if not tenant:
            return ({"message": "Tenant not found"}), 404

        headers = {
            'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',  # Use the API key from the tenant object
        }

        hostname = tenant.hostnames.split(',')[-1]
        next_url = f"https://{hostname}/api/v1/spaces"
        
        while next_url:
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed API call with status {response.status_code}: {response.text}")
                return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

            try:
                response_data = response.json()
                spaces = response_data.get('data', [])
                if not spaces:
                    print("No spaces found in the API response.")
                    return ({"error": "No spaces found in the response from Qlik Cloud API"}), 500

                if response.status_code == 200:
                    for space_data in spaces:
                        space_id = space_data.get('id')
                        existing_space = QlikSpace.query.get(space_id)
                        if not existing_space:
                            space = create_space_from_data(space_data)
                            db.add(space)
                            existing_space = space  # Set existing_task to the newly created task
                            existing_space.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                        db.commit()

                    # Check if there's a next page to fetch
                    next_link = response_data.get('links', {}).get('next', {})
                    next_url = next_link.get('href') if next_link else None

            except Exception as e:
                print(f"Exception encountered: {str(e)}")
                return ({"error": str(e)}), 500

        return ({"message": "Spaces fetched and stored successfully!"})
    else:
        return ({"message": "Failed to fetch spaces", "error": response.text}), response.status_code
    
    
# Helper function to create a new QlikSpace object from given attributes
def create_space_from_data(attributes):
    return QlikSpace(
        id=attributes.get('id'),
        name=attributes.get('name'),
        type=attributes.get('type'),
        owner_id=attributes.get('ownerId'),
        tenant_id=attributes.get('tenantId'),
        created_at=attributes.get('createdAt'),
        updated_at=attributes.get('updatedAt'),
        description=attributes.get('description'),
        meta=attributes.get('meta'),
        links=attributes.get('links')
    )