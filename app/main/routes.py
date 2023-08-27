from flask import request, jsonify, Blueprint, render_template, current_app, redirect, url_for, flash
from app import db
from app.models.qlik_app import QlikApp
from app.models.qlik_user import QlikUser, AssignedGroup, AssignedRole
from app.models.reload_task import ReloadTask
from app.models.user import User
from app.models.tenant import Tenant
from app.models.associations import user_tenants
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from . import main
import requests
import logging

# QLIK_APP_API_ENDPOINT = "https://mm-saas.eu.qlikcloud.com/api/v1/apps"
# QLIK_USERS_API_ENDPOINT = "https://mm-saas.eu.qlikcloud.com/api/v1/users"
# QLIK_RELOAD_TASK_API_ENDPOINT = "https://mm-saas.eu.qlikcloud.com/api/v1/reload-tasks"
# QLIK_RELOAD_TASK_UPDATE_ENDPOINT = "https://mm-saas.eu.qlikcloud.com/api/v1/reload-tasks/{task_id}"

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        user = create_user_from_data(data)
        qlik_cloud_api_key = data.get('qlik_cloud_api_key')

        # Add the user to the session and commit to get the user.id
        db.session.add(user)
        db.session.commit()

        # Validate the provided tenant URL and Qlik Cloud API key
        if not check_tenant(user, qlik_cloud_api_key):
            flash('Invalid tenant URL or Qlik Cloud API key. Please try again.')
            return render_template('signup.html')

        # Generate the API key
        s = Serializer(current_app.config['SECRET_KEY'], '1800')
        user.admin_dashboard_api_key = s.dumps({'user_id': user.id})

        # Fetch and store data for each tenant
        tenants = user.tenants
        for tenant in tenants:
            fetch_and_store_apps(tenant.id)
            fetch_and_store_users(tenant.id)
            fetch_and_store_reload_tasks(tenant.id)

        # Commit the user again to save the admin_dashboard_api_key
        db.session.commit()

        flash('Signup successful. Please login.')
        return jsonify({"message": "Signup successful."}), 200
    return jsonify({"message": "Signup failed."}), 404

def check_quota(user):
    headers = {
        'Authorization': f'Bearer {user.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/quotas", headers=headers)
    return response.status_code == 200  # Return True if the API call was successful, False otherwise

def check_tenant(user, qlik_cloud_api_key):
    headers = {
        'Authorization': f'Bearer {qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
    response_data = response.json()
    tenants = response_data.get('data', [])
    for tenant_data in tenants:
        tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
        tenant = create_tenant_from_data(tenant_data)
        # Check if the association already exists
        if tenant not in user.tenants:
            user.tenants.append(tenant)  # Add the tenant to the user's tenants
    db.session.commit()
    return response.status_code == 200  # Return True if the API call was successful, False otherwise

@main.route('/create_tenant', methods=['GET', 'POST'])
def create_tenant():
    if request.method == 'POST':
        qlik_cloud_tenant_url = request.form.get('qlik_cloud_url')
        qlik_cloud_api_key = request.form.get('qlik_cloud_api_key')
        user = User.query.filter_by(_id=request.form.get('user_id')).first()
        
        headers = {
            'Authorization': f'Bearer {qlik_cloud_api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"https://{qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
        response_data = response.json()
        tenants = response_data.get('data', [])
        for tenant_data in tenants:
            tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
            tenant = create_tenant_from_data(tenant_data)
            # Check if the association already exists
            if tenant not in user.tenants:
                user.tenants.append(tenant)  # Add the tenant to the user's tenants
        db.session.commit()
        if response.status_code == 200:
            return jsonify({"status": 200, "message": "Tenant created successfully"}), 200
        else:
            return jsonify({"status": response.status_code, "message": "API call was not successful"}), response.status_code
    return jsonify({"status": 400, "message": "Invalid request method"}), 400

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            flash('Login successful.')
            return jsonify({"user_id": user.id}), 200 #render_template('login.html')
        else:
            flash('Invalid email or password.')
    return jsonify({"login": 'Failed'}), 404 #render_template('login.html')


@main.route('/app_search/<string:app_name>', methods=['GET', 'POST'])
def app_search(app_name):
    if request.method == 'POST':
        budibase_api_key = 'budibase'
        headers = {
            'x-budibase-api-key': f'{budibase_api_key}',
            'Content-Type': 'application/json'
        }
        data = {"name": app_name}
        response = requests.post(f"http://bbproxy:10000/api/public/v1/applications/search", headers=headers, json=data)
        response_data = response.json()
        apps = response_data.get('data', [])
        for app_data in apps:
            if app_data['status'] == 'published':
                flash('App Found.')
                return jsonify({"_id": app_data['_id']}), 200
        else:
            flash('Application not found.')
    return jsonify({"error": 'applicaiton not found'}), 404


@main.route('/onboard', methods=['GET', 'POST'])
def onboard():
    if request.method == 'POST':
        app_name = 'ShortQliks'
        
        budibase_api_key = 'budibase'
        headers = {
            'x-budibase-api-key': f'{budibase_api_key}',
            'Content-Type': 'application/json'
        }
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        
        response = requests.post('http://web:5000/app_search/{app_name}'.format(app_name=app_name))
        if response.status_code == 200:
            response_data = response.json()
            app_id = response_data.get('_id')
        else:
            flash('Failed to find app.')
        
        data = [{"email": email,"userInfo":{"apps":{ app_id:"BASIC" }}}]
        response = requests.post(f"http://bbproxy:10000/api/global/users/onboard", headers=headers, json=data)
        response_data = response.json()
        users = response_data.get('successful', [])
        password = users[0]['password']
        for user_data in users:
            user = create_user_onboarding(user_data)
            # Add the user to the session and commit to get the user.id
            db.session.add(user)
            db.session.commit()
            
            update_data = {"firstName": firstName, "lastName": lastName, "forceResetPassword": False, "roles":{ app_id:"BASIC" }}
            response = requests.put('http://bbproxy:10000/api/public/v1/users/{_id}'.format(_id=user_data['_id']), headers=headers, json=update_data)
            # response_update = response.json()
            if response.status_code == 200:
                flash('Updated user.')
            else:
                flash('Failed to update user.')
            
            return jsonify({"user_id": user.id, "password": password}), 200
        else:
            flash('Onboarding Failed')
    return jsonify({"onboarding": 'Failed'}), 404


@main.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get(user_id)
    if not user.admin_dashboard_api_key:
        response = requests.post('http://web:5000' + url_for('main.generate_api_key'), json={'email': user.email})
        if response.status_code == 200:
            user.admin_dashboard_api_key = response.json()['api_key']
            db.session.commit()
        else:
            flash('Failed to generate API key.')
    return render_template('dashboard.html', user=user, tenants=user.tenants)


@main.route('/generate_api_key', methods=['POST'])
def generate_api_key():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        s = Serializer(current_app.config['SECRET_KEY'], '1800')
        user.admin_dashboard_api_key = s.dumps({'user_id': user.id})
        db.session.commit()
        return jsonify({"message": "API key generated successfully!", "api_key": user.admin_dashboard_api_key}), 200
    return jsonify({"message": "Email not found"}), 404

@main.route('/list_tasks')
def list_tasks():
    return render_template('list_tasks.html')

@main.route('/get_all_reload_tasks', methods=['GET'])
def get_all_reload_tasks():
    tasks = ReloadTask.query.all()
    return jsonify([task.to_dict() for task in tasks])

@main.route('/update_task_page/<task_id>')
def update_task_page(task_id):
    return render_template('update_task.html', task_id=task_id)

@main.route('/get_reload_task/<task_id>', methods=['GET'])
def get_reload_task(task_id):
    task = ReloadTask.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())  # Assuming you have a to_dict() method in your ReloadTask model


@main.route('/fetch_and_store_apps/<tenant_id>', methods=['POST'])
def fetch_and_store_apps(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"message": "Tenant not found"}), 404

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/apps"
    while next_url:
        response = requests.get(next_url, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

        response_data = response.json()
        apps = response_data.get('data', [])
        for app_data in apps:
            attributes = app_data.get('attributes', {})
            app = create_app_from_data(attributes)
            app.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
            db.session.merge(app)
        db.session.commit()

        next_link = response_data.get('links', {}).get('next')
        next_url = next_link.get('href') if next_link else None

    return jsonify({"message": "Apps fetched and stored successfully!"})

@main.route('/fetch_and_store_users/<tenant_id>', methods=['POST'])
def fetch_and_store_users(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"message": "Tenant not found"}), 404

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/users"
    while next_url:
        response = requests.get(next_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed API call with status {response.status_code}: {response.text}")
            return jsonify({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

        try:
            response_data = response.json()
            users = response_data.get('data', [])
            if not users:
                print("No users found in the API response.")
                return jsonify({"error": "No users found in the response from Qlik Cloud API"}), 500

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
                existing_user = QlikUser.query.get(user_id)
                if not existing_user:
                    existing_user = QlikUser(id=user_id)
                    db.session.add(existing_user)

                # Update the existing user's attributes
                for key, value in attributes.items():
                    setattr(existing_user, key, value)

                # Manage user groups
                for group_data in user_data.get('assignedGroups', []):
                    group = AssignedGroup.query.get(group_data['id']) or AssignedGroup(id=group_data['id'], name=group_data['name'])
                    existing_user.groups.append(group)
                    db.session.merge(group)

                # Manage user roles
                for role_data in user_data.get('assignedRoles', []):
                    role = AssignedRole.query.get(role_data['id']) or AssignedRole(
                        id=role_data['id'],
                        name=role_data['name'],
                        type=role_data['type'],
                        level=role_data['level'],
                        permissions=",".join(role_data.get('permissions', []))
                    )
                    existing_user.roles.append(role)
                    db.session.merge(role)

            # Check if there's a next page to fetch
            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            return jsonify({"error": str(e)}), 500

    db.session.commit()
    return jsonify({"message": "Users fetched and stored successfully!"})

@main.route('/fetch_and_store_reload_tasks/<tenant_id>', methods=['POST'])
def fetch_and_store_reload_tasks(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"message": "Tenant not found"}), 404

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
            return jsonify({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

        try:
            response_data = response.json()
            tasks = response_data.get('data', [])
            if not tasks:
                print("No reload tasks found in the API response.")
                return jsonify({"error": "No reload tasks found in the response from Qlik Cloud API"}), 500

            for task_data in tasks:
                task_id = task_data.get('id')
                existing_task = ReloadTask.query.get(task_id)
                if not existing_task:
                    task = create_reload_task_from_data(task_data)
                    db.session.add(task)
                    existing_task = task  # Set existing_task to the newly created task
                    existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                else:
                    for key, value in task_data.items():
                        if key == 'recurrence' and isinstance(value, str):  # Convert comma-separated string to list
                            value = value.split(',')
                        setattr(existing_task, key, value)

                existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                
                # Commit the changes to the database
                db.session.commit()

            # Check if there's a next page to fetch
            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Reload tasks fetched and stored successfully!"})

@main.route('/update_reload_task/<task_id>', methods=['PUT'])
def update_reload_task(task_id):
    api_key = request.headers.get('X-API-Key')
    user = User.query.filter_by(admin_dashboard_api_key=api_key).first()
    if not user:
        return jsonify({"message": "Invalid API key"}), 401

    try:
        data = request.json

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
        current_app.logger.info(f"Request body for task {task_id}: {data}")

        task = ReloadTask.query.get(task_id)
        if not task:
            return jsonify({"message": "Task not found"}), 404

        # Get the tenant associated with the task
        tenant = Tenant.query.get(task.tenant_id)
        if not tenant:
            return jsonify({"message": "Tenant not found"}), 404

        headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
        }
        
        # Update local database
        for key, value in data.items():
            setattr(task, key, value)
        db.session.commit()
        
        if not data['recurrence']:
            # Option 2: Provide a default value (uncomment the line below if you want to use this option)
            data['recurrence'] = None  # Replace DEFAULT_VALUE with a valid recurrence value

        hostname = tenant.hostnames.split(',')[-1]
        QLIK_RELOAD_TASK_UPDATE_ENDPOINT = f"https://{hostname}/api/v1/reload-tasks/{task_id}"
        response = requests.put(QLIK_RELOAD_TASK_UPDATE_ENDPOINT.format(task_id=task_id), headers=headers, json=data)

        if response.status_code != 200:
            current_app.logger.error(f"Error updating task {task_id} in Qlik Cloud: {response.text}")
            return jsonify({"message": f"Error updating task in Qlik Cloud: {response.text}"}), 500

        # After successful update, return a JSON response with the URL to redirect to
        return jsonify({"message": "Task updated successfully in both local database and Qlik Cloud!", "redirect_url": url_for('main.list_tasks')})
    except Exception as e:
        current_app.logger.error(f"Error updating task {task_id}: {str(e)}")  # Log the error
        return jsonify({"message": f"Error: {str(e)}"}), 500

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
    return ReloadTask(
        id=attributes.get('id'),
        appId=attributes.get('appId'),
        partial=attributes.get('partial'),
        timeZone=attributes.get('timeZone'),
        autoReload=attributes.get('autoReload'),
        recurrence=attributes.get('recurrence', []),
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