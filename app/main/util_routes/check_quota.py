def check_quota(user):
    headers = {
        'Authorization': f'Bearer {user.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/quotas", headers=headers)
    return response.status_code == 200  # Return True if the API call was successful, False otherwise