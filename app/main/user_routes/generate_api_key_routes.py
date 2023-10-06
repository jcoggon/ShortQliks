

@app.route('/generate_api_key', methods=['POST'])
def generate_api_key():
    data = requests.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        s = Serializer(Config['SECRET_KEY'], '1800')
        user.admin_dashboard_api_key = s.dumps({'user_id': user.id})
        db.commit()
        return ({"message": "API key generated successfully!", "api_key": user.admin_dashboard_api_key}), 200
    return ({"message": "Email not found"}), 404