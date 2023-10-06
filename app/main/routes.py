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

router = APIRouter()

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if requests.method == 'POST':
#         data = Form
#         user = create_user_from_data(data)
#         qlik_cloud_api_key = data.get('qlik_cloud_api_key')

#         # Add the user to the session and commit to get the user.id
#         db.add(user)
#         db.commit()

#         # Validate the provided tenant URL and Qlik Cloud API key
#         if not check_tenant(user, qlik_cloud_api_key):
#             # # flash('Invalid tenant URL or Qlik Cloud API key. Please try again.')
#             return logger.info('Invalid tenant URL or Qlik Cloud API key. Please try again.')

#         # Generate the API key
#         s = Serializer(Config['SECRET_KEY'], '1800')
#         user.admin_dashboard_api_key = s.dumps({'user_id': user.id})

#         # Fetch and store data for each tenant
#         tenants = user.tenants
#         for tenant in tenants:
#             fetch_and_store_apps(tenant.id)
#             fetch_and_store_users(tenant.id)
#             fetch_and_store_reload_tasks(tenant.id)
#             fetch_and_store_spaces(tenant.id)

#         # Commit the user again to save the admin_dashboard_api_key
#         db.commit()

#         # # flash('Signup successful. Please login.')
#         return ({"message": "Signup successful."}), 200
#     return ({"message": "Signup failed."}), 404

# def check_quota(user):
#     headers = {
#         'Authorization': f'Bearer {user.qlik_cloud_api_key}',
#         'Content-Type': 'application/json'
#     }
#     response = requests.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/quotas", headers=headers)
#     return response.status_code == 200  # Return True if the API call was successful, False otherwise

# def check_tenant(user, qlik_cloud_api_key):
#     headers = {
#         'Authorization': f'Bearer {qlik_cloud_api_key}',
#         'Content-Type': 'application/json'
#     }
#     response = requests.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
#     response_data = response.json()
#     tenants = response_data.get('data', [])
#     for tenant_data in tenants:
#         tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
#         tenant = create_tenant_from_data(tenant_data)
#         # Check if the association already exists
#         if tenant not in user.tenants:
#             user.tenants.append(tenant)  # Add the tenant to the user's tenants
#     db.commit()
#     return response.status_code == 200  # Return True if the API call was successful, False otherwise

# @app.route('/create_tenant', methods=['GET', 'POST'])
# def create_tenant():
#     if requests.method == 'POST':
#         qlik_cloud_tenant_url = Form('qlik_cloud_url')
#         qlik_cloud_api_key = Form('qlik_cloud_api_key')
#         user = User.query.filter_by(_id=Form('user_id')).first()
#         request_data = Form
#         print(request_data)
#         headers = {
#             'Authorization': f'Bearer {qlik_cloud_api_key}',
#             'Content-Type': 'application/json'
#         }
#         response = requests.get(f"https://{qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
#         response_data = response.json()
#         tenants = response_data.get('data', [])
#         for tenant_data in tenants:
#             tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
#             tenant = create_tenant_from_data(tenant_data)
#             # Check if the association already exists
#             if tenant not in user.tenants:
#                 user.tenants.append(tenant)  # Add the tenant to the user's tenants
#         db.commit()
#         tenant_id = tenant.id
#         if response.status_code == 200:
#             return ({"status": 200, "message": "Tenant created successfully", "tenant_id": tenant_id}), 200
#         else:
#             return ({"status": response.status_code, "message": "API call was not successful"}), response.status_code
#     return ({"status": 400, "message": "Invalid request method"}), 400

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if requests.method == 'POST':
#         data = Form
#         user = User.query.filter_by(email=Form('email')).first()
#         if user and user.check_password(Form('password')):
#             # # flash('Login successful.')
#             return ({"user_id": user.id}), 200 #render_template('login.html')
#         else:
#             # # flash('Invalid email or password.')
#             return ({"login": 'Failed'}), 404 #render_template('login.html')


# @app.route('/app_search/<string:app_name>', methods=['GET', 'POST'])
# def app_search(app_name):
#     if requests.method == 'POST':
#         budibase_api_key = 'budibase'
#         headers = {
#             'x-budibase-api-key': f'{budibase_api_key}',
#             'Content-Type': 'application/json'
#         }
#         data = {"name": app_name}
#         response = requests.post(f"http://bbproxy:10000/api/public/v1/applications/search", headers=headers, json=data)
#         response_data = response.json()
#         apps = response_data.get('data', [])
#         for app_data in apps:
#             if app_data['status'] == 'published':
#                 # # flash('App Found.')
#                 return ({"_id": app_data['_id']}), 200
#         else:
#             # # flash('Application not found.')
#             return ({"error": 'applicaiton not found'}), 404


# @app.route('/onboard', methods=['GET', 'POST'])
# def onboard():
#     if requests.method == 'POST':
#         app_name = 'ShortQliks'
        
#         budibase_api_key = 'budibase'
#         headers = {
#             'x-budibase-api-key': f'{budibase_api_key}',
#             'Content-Type': 'application/json'
#         }
#         email = Form('email')
#         firstName = Form('firstName')
#         lastName = Form('lastName')
        
#         response = requests.post('http://web:5000/app_search/{app_name}'.format(app_name=app_name))
#         if response.status_code == 200:
#             response_data = response.json()
#             app_id = response_data.get('_id')
#         else:
#             # # flash('Failed to find app.')
        
#             data = [{"email": email,"userInfo":{"apps":{ app_id:"BASIC" }}}]
#             response = requests.post(f"http://bbproxy:10000/api/global/users/onboard", headers=headers, json=data)
#             response_data = response.json()
#             users = response_data.get('successful', [])
#             password = users[0]['password']
#             for user_data in users:
#                 user = create_user_onboarding(user_data)
#                 # Add the user to the session and commit to get the user.id
#                 db.add(user)
#                 db.commit()
                
#                 update_data = {"firstName": firstName, "lastName": lastName, "forceResetPassword": False, "roles":{ app_id:"BASIC" }}
#                 response = requests.put('http://bbproxy:10000/api/public/v1/users/{_id}'.format(_id=user_data['_id']), headers=headers, json=update_data)
#                 # response_update = response.json()
#                 if response.status_code == 200:
#                     print('Updated user.')
#                 else:
#                     print('Failed to update user.')
                
#                 return ({"user_id": user.id, "password": password}), 200
#             else:
#                 # # flash('Onboarding Failed')
#                 return ({"onboarding": 'Failed'}), 404


# @app.route('/generate_api_key', methods=['POST'])
# def generate_api_key():
#     data = requests.get_json()
#     user = User.query.filter_by(email=data['email']).first()
#     if user:
#         s = Serializer(Config['SECRET_KEY'], '1800')
#         user.admin_dashboard_api_key = s.dumps({'user_id': user.id})
#         db.commit()
#         return ({"message": "API key generated successfully!", "api_key": user.admin_dashboard_api_key}), 200
#     return ({"message": "Email not found"}), 404


# @app.route('/get_reload_task/<task_id>', methods=['GET'])
# def get_reload_task(task_id):
#     task = ReloadTask.query.get(task_id)
#     if not task:
#         return ({"error": "Task not found"}), 404
#     return task.to_dict()  # Assuming you have a to_dict() method in your ReloadTask model


# @app.route('/fetch_and_store_apps', methods=['GET', 'POST'])
# def fetch_and_store_apps():
#     if requests.method == 'POST':
#         tenant_id = Form('tenant_id')
#         tenant = Tenant.query.get(tenant_id)
#         if not tenant:
#             return ({"message": "Tenant not found"}), 404

#         headers = {
#             'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
#             'Content-Type': 'application/json'
#         }

#         hostname = tenant.hostnames.split(',')[-1]
#         next_url = f"https://{hostname}/api/v1/apps"
#         while next_url:
#             response = requests.get(next_url, headers=headers)
#             if response.status_code != 200:
#                 return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

#             response_data = response.json()
#             apps = response_data.get('data', [])
#             for app_data in apps:
#                 attributes = app_data.get('attributes', {})
#                 app = create_app_from_data(attributes)
#                 app.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
#                 db.session.merge(app)
#             db.commit()

#             next_link = response_data.get('links', {}).get('next')
#             next_url = next_link.get('href') if next_link else None

#     return ({"message": "Apps fetched and stored successfully!"}), 200

@router.post('/fetch_and_store_users')
async def fetch_and_store_users(
    tenant_id: int = Form(...),
    db: Session = Depends(SessionLocal)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/users"
    try:
        while next_url:
            response = Request.get(next_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed API call with status {response.status_code}: {response.text}")
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            try:
                response_data = response.json()
                users = response_data.get('data', [])
                if not users:
                    print("No users found in the API response.")
                    return {"error": "No users found in the response from Qlik Cloud API"}

                for user_data in users:
                    user_id = user_data.get('id')
                    qlik_app_link = user_data.get('links', {}).get('self', {}).get('href')
                    attributes = {
                        'name': user_data.get('name'),
                        'email': user_data.get('email', 'N/A'),
                        'tenantId': user_data.get('tenantId'),
                        'status': user_data.get('status'),
                        'created': user_data.get('created'),
                        'lastUpdated': user_data.get('lastUpdated'),
                        'qlik_app_link': qlik_app_link
                    }

                    # Check if user already exists
                    existing_user = db.query(QlikUser).filter(QlikUser.id == user_id).first()
                    if not existing_user:
                        existing_user = QlikUser(id=user_id)
                        db.add(existing_user)

                    # Update the existing user's attributes
                    for key, value in attributes.items():
                        setattr(existing_user, key, value)

                    # Manage user groups
                    for group_data in user_data.get('assignedGroups', []):
                        group = db.query(AssignedGroup).filter(AssignedGroup.id == group_data['id']).first() or AssignedGroup(
                            id=group_data['id'],
                            name=group_data['name']
                        )
                        existing_user.groups.append(group)
                        db.merge(group)

                    # Manage user roles
                    for role_data in user_data.get('assignedRoles', []):
                        role = db.query(AssignedRole).filter(AssignedRole.id == role_data['id']).first() or AssignedRole(
                            id=role_data['id'],
                            name=role_data['name'],
                            type=role_data['type'],
                            level=role_data['level'],
                            permissions=",".join(role_data.get('permissions', []))
                        )
                        existing_user.roles.append(role)
                        db.merge(role)

                # Check if there's a next page to fetch
                next_link = response_data.get('links', {}).get('next')
                next_url = next_link.get('href') if next_link else None

            except Exception as e:
                print(f"Exception encountered: {str(e)}")
                return {"error": str(e)}

        db.commit()
    finally:
        # Always close the session to return it to the pool
        db.close()

    return {"message": "Users fetched and stored successfully!"}

# @app.route('/fetch_and_store_reload_tasks', methods=['GET', 'POST'])
# def fetch_and_store_reload_tasks():
#     if requests.method == 'POST':
#         tenant_id = Form('tenant_id')
#         tenant = Tenant.query.get(tenant_id)
#         if not tenant:
#             return ({"message": "Tenant not found"}), 404

#         headers = {
#             'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
#             'Content-Type': 'application/json'
#         }

#         hostname = tenant.hostnames.split(',')[-1]
#         next_url = f"https://{hostname}/api/v1/reload-tasks"
#         while next_url:
#             response = requests.get(next_url, headers=headers)
#             if response.status_code != 200:
#                 print(f"Failed API call with status {response.status_code}: {response.text}")
#                 return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

#             try:
#                 response_data = response.json()
#                 tasks = response_data.get('data', [])
#                 # print("Task Data:", tasks)
#                 if not tasks:
#                     print("No reload tasks found in the API response.")
#                     return ({"error": "No reload tasks found in the response from Qlik Cloud API"}), 500

#                 for task_data in tasks:
#                     task_id = task_data.get('id')
#                     existing_task = ReloadTask.query.get(task_id)
#                     if not existing_task:
#                         task = create_reload_task_from_data(task_data)
#                         db.add(task)
#                         existing_task = task  # Set existing_task to the newly created task
#                         existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
#                     else:
#                         for key, value in task_data.items():
#                             if key == 'recurrence' and isinstance(value, list):  # Convert list to comma-separated string
#                                 value = ', '.join(value)
#                             setattr(existing_task, key, value)

#                     existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    
#                     # Commit the changes to the database
#                     db.commit()

#                 # Check if there's a next page to fetch
#                 next_link = response_data.get('links', {}).get('next')
#                 next_url = next_link.get('href') if next_link else None

#             except Exception as e:
#                 print(f"Exception encountered: {str(e)}")
#                 return ({"error": str(e)}), 500

#     return ({"message": "Reload tasks fetched and stored successfully!"})

# @app.route('/update_reload_task', methods=['POST'])
# def update_reload_task():
#     if requests.method == 'POST':
#         tenant_id = Form('tenant_id')
#         tenant = Tenant.query.get(tenant_id)
#         if not tenant:
#             return ({"message": "Tenant not found"}), 404

#         try:
#             data = Request
            
#             task_id = data.get('task_id')

#             # Ensure datetime strings are in the correct format or set to None if empty
#             if not data.get('endDateTime'):
#                 data['endDateTime'] = None
#             else:
#                 data['endDateTime'] = ensure_full_datetime_format(data['endDateTime'])

#             if not data.get('startDateTime'):
#                 data['startDateTime'] = None
#             else:
#                 data['startDateTime'] = ensure_full_datetime_format(data['startDateTime'])

#             # Log the request body for debugging
#             logger.info(f"Request body for task {task_id}: {data}")

#             task = ReloadTask.query.get(task_id)
#             if not task:
#                 return ({"message": "Task not found"}), 404

#             # Get the tenant associated with the task
#             tenant = Tenant.query.get(task.tenant_id)
#             if not tenant:
#                 return ({"message": "Tenant not found"}), 404

#             headers = {
#             'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
#             'Content-Type': 'application/json'
#             }
            
#             # Update local database
#             for key, value in data.items():
#                 if key == 'recurrence' and isinstance(value, list):  # Convert list to comma-separated string
#                     value = ', '.join(value)
#                 setattr(task, key, value)
#             db.commit()
            
#             if not data['recurrence']:
#                 # Option 2: Provide a default value (uncomment the line below if you want to use this option)
#                 data['recurrence'] = None  # Replace DEFAULT_VALUE with a valid recurrence value

#             hostname = tenant.hostnames.split(',')[-1]
#             QLIK_RELOAD_TASK_UPDATE_ENDPOINT = f"https://{hostname}/api/v1/reload-tasks/{task_id}"
#             response = requests.put(QLIK_RELOAD_TASK_UPDATE_ENDPOINT.format(task_id=task_id), headers=headers, json=data)

#             if response.status_code != 200:
#                 logger.error(f"Error updating task {task_id} in Qlik Cloud: {response.text}")
#                 return ({"message": f"Error updating task in Qlik Cloud: {response.text}"}), 500

#             # After successful update, return a JSON response with the URL to redirect to
#             return ({"message": "Task updated successfully in both local database and Qlik Cloud!"}), 200
#         except Exception as e:
#             logger.error(f"Error updating task {task_id}: {str(e)}")  # Log the error
#             return ({"message": f"Error: {str(e)}"}), 500

# @app.route('/fetch_and_store_spaces', methods=['GET', 'POST'])
# def fetch_and_store_spaces():
#     if requests.method == 'POST':
#         tenant_id = Form('tenant_id')  # Get tenant_id from query parameters
#         tenant = Tenant.query.get(tenant_id)  # Query for the corresponding tenant
#         if not tenant:
#             return ({"message": "Tenant not found"}), 404

#         headers = {
#             'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',  # Use the API key from the tenant object
#         }

#         hostname = tenant.hostnames.split(',')[-1]
#         next_url = f"https://{hostname}/api/v1/spaces"
        
#         while next_url:
#             response = requests.get(next_url, headers=headers)
#             if response.status_code != 200:
#                 print(f"Failed API call with status {response.status_code}: {response.text}")
#                 return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

#             try:
#                 response_data = response.json()
#                 spaces = response_data.get('data', [])
#                 if not spaces:
#                     print("No spaces found in the API response.")
#                     return ({"error": "No spaces found in the response from Qlik Cloud API"}), 500

#                 if response.status_code == 200:
#                     for space_data in spaces:
#                         space_id = space_data.get('id')
#                         existing_space = QlikSpace.query.get(space_id)
#                         if not existing_space:
#                             space = create_space_from_data(space_data)
#                             db.add(space)
#                             existing_space = space  # Set existing_task to the newly created task
#                             existing_space.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
#                         db.commit()

#                     # Check if there's a next page to fetch
#                     next_link = response_data.get('links', {}).get('next', {})
#                     next_url = next_link.get('href') if next_link else None

#             except Exception as e:
#                 print(f"Exception encountered: {str(e)}")
#                 return ({"error": str(e)}), 500

#         return ({"message": "Spaces fetched and stored successfully!"})
#     else:
#         return ({"message": "Failed to fetch spaces", "error": response.text}), response.status_code


def ensure_full_datetime_format(dt_str):
    """Ensure the datetime string is in the format 'YYYY-MM-DDTHH:MM:SS'."""
    if len(dt_str) == 13:  # Format is 'YYYY-MM-DDTHH'
        return dt_str + ":00:00"
    elif len(dt_str) == 16:  # Format is 'YYYY-MM-DDTHH:MM'
        return dt_str + ":00"
    return dt_str

def user_input_to_icalendar_format(data):
    rrule = ""
    freq = data.get('frequency1')
    if freq:
        rrule = f"RRULE:FREQ={freq}"
        interval = data.get('interval1')
        if interval:
            rrule += f";INTERVAL={interval}"
        if freq == "WEEKLY":
            days = data.getlist('byDay1')
            if days:
                rrule += f";BYDAY={','.join(days)}"
        elif freq in ["MONTHLY", "YEARLY"]:
            # Handle specific rules for monthly and yearly recurrence if needed
            pass
        for unit in ['byHour', 'byMinute', 'bySecond']:
            value = data.get(f'{unit}1')
            if value:
                rrule += f";{unit.upper()}={value}"
    return rrule

def create_user_from_data(data):
    return User(
        _id=data['_id'],
        fullname=data['fullname'],
        email=data['email'],
        password=data['password'],
        qlik_cloud_tenant_url=data['qlik_cloud_tenant_url']
    )
    
def create_user_onboarding(data):
    return User(
        _id=data['_id'],
        email=data['email'],
        password=data['password']
    )

def create_tenant_from_data(tenant_data):
    tenant = Tenant.query.get(tenant_data.get('id'))
    if tenant is None:
        tenant = Tenant(
            id=tenant_data.get('id'),
            name=tenant_data.get('name'),
            hostnames=','.join(tenant_data.get('hostnames', [])),
            createdByUser=tenant_data.get('createdByUser'),
            datacenter=tenant_data.get('datacenter'),
            created=tenant_data.get('created'),
            lastUpdated=tenant_data.get('lastUpdated'),
            status=tenant_data.get('status'),
            autoAssignCreateSharedSpacesRoleToProfessionals=tenant_data.get('autoAssignCreateSharedSpacesRoleToProfessionals'),
            autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals=tenant_data.get('autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals'),
            autoAssignDataServicesContributorRoleToProfessionals=tenant_data.get('autoAssignDataServicesContributorRoleToProfessionals'),
            enableAnalyticCreation=tenant_data.get('enableAnalyticCreation'),
            qlik_cloud_api_key=tenant_data.get('qlik_cloud_api_key')
        )
    else:
        tenant.name = tenant_data.get('name')
        tenant.hostnames = ','.join(tenant_data.get('hostnames', []))
        tenant.createdByUser = tenant_data.get('createdByUser')
        tenant.datacenter = tenant_data.get('datacenter')
        tenant.created = tenant_data.get('created')
        tenant.lastUpdated = tenant_data.get('lastUpdated')
        tenant.status = tenant_data.get('status')
        tenant.autoAssignCreateSharedSpacesRoleToProfessionals = tenant_data.get('autoAssignCreateSharedSpacesRoleToProfessionals')
        tenant.autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals = tenant_data.get('autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals')
        tenant.autoAssignDataServicesContributorRoleToProfessionals = tenant_data.get('autoAssignDataServicesContributorRoleToProfessionals')
        tenant.enableAnalyticCreation = tenant_data.get('enableAnalyticCreation')
        tenant.qlik_cloud_api_key = tenant_data.get('qlik_cloud_api_key')
    return tenant

def create_app_from_data(attributes):
    return QlikApp(
        id=attributes.get('id'),
        name=attributes.get('name'),
        owner=attributes.get('owner'),
        usage=attributes.get('usage'),
        ownerId=attributes.get('ownerId'),
        encrypted=attributes.get('encrypted'),
        published=attributes.get('published'),
        thumbnail=attributes.get('thumbnail'),
        createdDate=attributes.get('createdDate'),
        description=attributes.get('description'),
        originAppId=attributes.get('originAppId'),
        publishTime=attributes.get('publishTime'),
        dynamicColor=attributes.get('dynamicColor'),
        modifiedDate=attributes.get('modifiedDate'),
        lastReloadTime=attributes.get('lastReloadTime'),
        hasSectionAccess=attributes.get('hasSectionAccess'),
        isDirectQueryMode=attributes.get('isDirectQueryMode'),
        tenant_id=attributes.get('tenant_id')
    )

def create_qlik_user_from_data(user_id, attributes, qlik_app_link):
    return QlikUser(
        id=user_id,
        name=attributes.get('name'),
        email=attributes.get('email', 'N/A'),  # Default to 'N/A' if email is missing
        tenantId=attributes.get('tenantId'),
        status=attributes.get('status'),
        created=attributes.get('created'),
        lastUpdated=attributes.get('lastUpdated'),
        qlik_app_link=qlik_app_link
    )
    
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