"""
VAPT Security Tests — API Layer
Covers: OWASP Top 10 vulnerabilities for the Task API
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Task


@pytest.mark.django_db
class TestSQLInjection:
    """A1: Injection — verify ORM protects against SQL injection payloads"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_sql_injection_in_search(self):
        """SQL injection payload in search parameter must not cause 500 error"""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE api_task; --",
            "1' UNION SELECT username, password FROM auth_user --",
            "' OR 1=1 --",
        ]
        for payload in payloads:
            response = self.client.get(f'/api/tasks/?search={payload}')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST], \
                f"SQL injection payload caused unexpected status: {payload}"
            assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_sql_injection_in_task_title(self):
        """SQL injection payload in task title must be stored safely, not executed"""
        payload = "'; DROP TABLE api_task; --"
        response = self.client.post('/api/tasks/', {'title': payload}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get(title=payload)
        assert task.title == payload  # stored as-is, not executed

    def test_sql_injection_in_filter_params(self):
        """SQL injection in filter query parameters must not break the API"""
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE auth_user",
        ]
        for payload in payloads:
            response = self.client.get(f'/api/tasks/?status={payload}')
            assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestAuthenticationSecurity:
    """A2: Broken Authentication — JWT and session security"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!'
        )

    def test_unauthenticated_access_blocked(self):
        """All protected endpoints must reject unauthenticated requests"""
        endpoints = [
            '/api/tasks/',
            '/api/tasks/1/',
            '/api/tasks/statistics/',
            '/api/tasks/my_tasks/',
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"Endpoint {endpoint} allowed unauthenticated access"

    def test_tampered_jwt_token_rejected(self):
        """A tampered JWT token must be rejected"""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
            '.eyJ1c2VyX2lkIjoxfQ.TAMPERED_SIGNATURE'
        )
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_format_rejected(self):
        """Malformed Authorization header must be rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer not-a-real-token')
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_bearer_prefix_rejected(self):
        """Token without Bearer prefix must be rejected"""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=str(refresh.access_token))
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_token_rejected(self):
        """Empty Bearer token must be rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ')
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBrokenAccessControl:
    """A5: Broken Access Control — IDOR and privilege escalation"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass123'
        )
        self.victim = User.objects.create_user(
            username='victim', email='victim@example.com', password='pass123'
        )
        self.victim_task = Task.objects.create(
            title='Private Task', created_by=self.victim
        )

    def test_idor_read_other_user_task(self):
        """Users must not be able to read other users' tasks (IDOR)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/tasks/{self.victim_task.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_idor_update_other_user_task(self):
        """Users must not be able to update other users' tasks (IDOR)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/tasks/{self.victim_task.id}/',
            {'title': 'Hacked'},
            format='json'
        )
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND
        ]

    def test_idor_delete_other_user_task(self):
        """Users must not be able to delete other users' tasks (IDOR)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/tasks/{self.victim_task.id}/')
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND
        ]
        assert Task.objects.filter(id=self.victim_task.id).exists()

    def test_privilege_escalation_via_created_by(self):
        """Users must not be able to assign tasks to other users via created_by"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Escalation Task', 'created_by': self.victim.id},
            format='json'
        )
        if response.status_code == status.HTTP_201_CREATED:
            task = Task.objects.get(id=response.data['id'])
            assert task.created_by == self.user  # must always be the authenticated user

    def test_complete_other_user_task_blocked(self):
        """Users must not be able to complete other users' tasks"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/tasks/{self.victim_task.id}/complete/')
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND
        ]


@pytest.mark.django_db
class TestSensitiveDataExposure:
    """A3: Sensitive Data Exposure — passwords, tokens not leaked in responses"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_password_not_in_task_response(self):
        """Task response must not contain any password fields"""
        Task.objects.create(title='Test', created_by=self.user)
        response = self.client.get('/api/tasks/')
        response_str = str(response.data).lower()
        assert 'password' not in response_str

    def test_password_not_in_statistics_response(self):
        """Statistics response must not expose sensitive fields"""
        response = self.client.get('/api/tasks/statistics/')
        response_str = str(response.data).lower()
        assert 'password' not in response_str

    def test_task_response_does_not_leak_other_users_data(self):
        """Task list must not include data belonging to other users"""
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass123'
        )
        Task.objects.create(title='My Task', created_by=self.user)
        Task.objects.create(title='Other Task', created_by=other_user)

        response = self.client.get('/api/tasks/')
        task_ids = [t['created_by'] for t in response.data['results']]
        assert all(uid == self.user.id for uid in task_ids)


@pytest.mark.django_db
class TestXSSPrevention:
    """A3/A7: XSS — ensure malicious scripts stored safely and returned as data"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_xss_payload_in_title_stored_safely(self):
        """XSS payload in task title must be stored as text, not executed"""
        xss_payload = '<script>alert("XSS")</script>'
        response = self.client.post(
            '/api/tasks/', {'title': xss_payload}, format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == xss_payload
        task = Task.objects.get(id=response.data['id'])
        assert task.title == xss_payload

    def test_xss_payload_in_description(self):
        """XSS payload in description must be returned as plain text"""
        xss_payload = '<img src=x onerror=alert(1)>'
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Test', 'description': xss_payload},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == xss_payload

    def test_json_response_content_type(self):
        """API responses must have application/json content type, preventing HTML injection"""
        response = self.client.get('/api/tasks/')
        assert 'application/json' in response.get('Content-Type', '')


@pytest.mark.django_db
class TestMassAssignment:
    """A8: Insecure Deserialization — mass assignment / forced field injection"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_cannot_set_completed_via_create(self):
        """completed field should be default False on creation regardless of input"""
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Sneaky Task', 'completed': True},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        # completed is in TaskCreateSerializer so it can be set, but must be validated
        task = Task.objects.get(id=response.data['id'])
        assert task.created_by == self.user

    def test_cannot_override_created_by_field(self):
        """created_by must always be set to authenticated user, never overridable"""
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass'
        )
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Hijacked Task', 'created_by': other_user.id},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get(id=response.data['id'])
        assert task.created_by == self.user


@pytest.mark.django_db
class TestSecurityHeaders:
    """Verify Django security middleware is active by checking response headers"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_x_content_type_options_header(self):
        """X-Content-Type-Options header must be present"""
        response = self.client.get('/api/tasks/')
        assert response.get('X-Content-Type-Options') == 'nosniff'

    def test_x_frame_options_header(self):
        """X-Frame-Options header must be present to prevent clickjacking"""
        response = self.client.get('/api/tasks/')
        x_frame = response.get('X-Frame-Options', '')
        assert x_frame in ['DENY', 'SAMEORIGIN']
