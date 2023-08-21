# tests/test_user.py

from tests.base import BaseTestCase
from app import db
from app.models.user import User

class TestUser(BaseTestCase):
    def test_signup(self):
        response = self.client.post('/signup', json={
            'fullname': 'Test User',
            'email': 'test@example.com',
            'password': 'password',
            'qlik_cloud_tenant_url': 'https://qlikcloud.com',
            'qlik_cloud_api_key': 'eyJhbGciOiJFUzM4NCIsImtpZCI6ImEzMDY5MjhiLWYyN2MtNDhiNS04NjFjLTQ1OWJiODE1NWY4YiIsInR5cCI6IkpXVCJ9.eyJzdWJUeXBlIjoidXNlciIsInRlbmFudElkIjoiWER2STFkazYwVlR1X0NDNV9JODhvQzFJWWF4WlNpTkMiLCJqdGkiOiJhMzA2OTI4Yi1mMjdjLTQ4YjUtODYxYy00NTliYjgxNTVmOGIiLCJhdWQiOiJxbGlrLmFwaSIsImlzcyI6InFsaWsuYXBpL2FwaS1rZXlzIiwic3ViIjoiSWM0WHpmbk5ucU9NejZDTlN3MjdNR1lweGY1UFNtYjIifQ.7edOBDPF5Y6TL5mfuye2Tt-scGsQm3qZmKx-XXyAYIyUsrbpUgxeiWl7CMzF_UIqUHS8iJpcFm-PdT9Y9Au4jLxWhdGeh8IDClcHP6rymWMuNLIdNiHIswoJ8oBOsxrQ'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1)

    def test_generate_api_key(self):
        user = User(
            fullname='Test User',
            email='test@example.com',
            password='password',
            qlik_cloud_tenant_url='https://qlikcloud.com',
            qlik_cloud_api_key='eyJhbGciOiJFUzM4NCIsImtpZCI6ImEzMDY5MjhiLWYyN2MtNDhiNS04NjFjLTQ1OWJiODE1NWY4YiIsInR5cCI6IkpXVCJ9.eyJzdWJUeXBlIjoidXNlciIsInRlbmFudElkIjoiWER2STFkazYwVlR1X0NDNV9JODhvQzFJWWF4WlNpTkMiLCJqdGkiOiJhMzA2OTI4Yi1mMjdjLTQ4YjUtODYxYy00NTliYjgxNTVmOGIiLCJhdWQiOiJxbGlrLmFwaSIsImlzcyI6InFsaWsuYXBpL2FwaS1rZXlzIiwic3ViIjoiSWM0WHpmbk5ucU9NejZDTlN3MjdNR1lweGY1UFNtYjIifQ.7edOBDPF5Y6TL5mfuye2Tt-scGsQm3qZmKx-XXyAYIyUsrbpUgxeiWl7CMzF_UIqUHS8iJpcFm-PdT9Y9Au4jLxWhdGeh8IDClcHP6rymWMuNLIdNiHIswoJ8oBOsxrQ'
        )
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/generate_api_key', json={'email': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['api_key'])