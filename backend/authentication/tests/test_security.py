"""
VAPT Security Tests — Authentication Layer
Covers: OWASP Top 10 vulnerabilities for auth endpoints
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestBrokenAuthentication:
    """A2: Broken Authentication — login, registration, token security"""

    def setup_method(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.register_url = '/api/auth/register/'

    def test_login_with_nonexistent_user(self):
        """Login with nonexistent username must return 401, not expose user existence"""
        response = self.client.post(
            self.login_url,
            {'username': 'ghost_user', 'password': 'AnyPassword123!'},
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # Must not reveal whether the user exists
        assert 'password' not in str(response.data).lower()
        assert 'user' not in str(response.data).lower() or 'error' in str(response.data).lower()

    def test_login_with_wrong_password(self):
        """Login with wrong password must return same 401 as nonexistent user"""
        User.objects.create_user(username='realuser', password='CorrectPass123!')
        response = self.client.post(
            self.login_url,
            {'username': 'realuser', 'password': 'WrongPassword!'},
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_empty_credentials(self):
        """Login with empty credentials must be rejected"""
        response = self.client.post(
            self.login_url, {'username': '', 'password': ''}, format='json'
        )
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED
        ]

    def test_login_response_contains_token(self):
        """Successful login must return JWT access and refresh tokens"""
        User.objects.create_user(username='validuser', password='ValidPass123!')
        response = self.client.post(
            self.login_url,
            {'username': 'validuser', 'password': 'ValidPass123!'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_response_does_not_expose_password(self):
        """Login response must never return the user's password"""
        User.objects.create_user(username='validuser', password='ValidPass123!')
        response = self.client.post(
            self.login_url,
            {'username': 'validuser', 'password': 'ValidPass123!'},
            format='json'
        )
        response_str = str(response.data)
        assert 'ValidPass123!' not in response_str
        assert 'password' not in response_str.lower() or 'pbkdf2' not in response_str

    def test_sql_injection_in_login(self):
        """SQL injection in login fields must not cause 500 or bypass auth"""
        sql_payloads = [
            ("' OR '1'='1", "anything"),
            ("admin'--", "anything"),
            ("' OR 1=1;--", "' OR 1=1;--"),
        ]
        for username, password in sql_payloads:
            response = self.client.post(
                self.login_url,
                {'username': username, 'password': password},
                format='json'
            )
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED
            ], f"SQL injection may have bypassed auth: {username}"
            assert response.status_code != status.HTTP_200_OK

    def test_xss_payload_in_login(self):
        """XSS payloads in login must not cause 500 errors"""
        response = self.client.post(
            self.login_url,
            {'username': '<script>alert(1)</script>', 'password': 'pass'},
            format='json'
        )
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestRegistrationSecurity:
    """Registration endpoint security — input validation, role protection"""

    def setup_method(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_registration_without_password_confirmation(self):
        """Registration must fail without password2"""
        response = self.client.post(
            self.register_url,
            {'username': 'newuser', 'email': 'new@e.com', 'password': 'Pass123!'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_short_password(self):
        """Short passwords must be rejected by Django validators"""
        response = self.client.post(
            self.register_url,
            {'username': 'newuser', 'email': 'new@e.com', 'password': '123', 'password2': '123'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_response_no_password_hash(self):
        """Registration response must not expose the hashed password"""
        response = self.client.post(
            self.register_url,
            {
                'username': 'newuser', 'email': 'new@e.com',
                'password': 'SecurePass123!', 'password2': 'SecurePass123!'
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_str = str(response.data)
        assert 'pbkdf2' not in response_str.lower()

    def test_unauthenticated_cannot_create_super_admin(self):
        """An unauthenticated request must not be able to register a super admin"""
        response = self.client.post(
            self.register_url,
            {
                'username': 'hacker_admin',
                'email': 'hack@e.com',
                'password': 'SecurePass123!',
                'password2': 'SecurePass123!',
                'role': 1,
            },
            format='json'
        )
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(username='hacker_admin')
            assert user.profile.role == 3  # forced to regular user

    def test_xss_payload_in_username(self):
        """XSS in username must not cause 500"""
        response = self.client.post(
            self.register_url,
            {
                'username': '<script>alert(1)</script>',
                'email': 'xss@e.com',
                'password': 'SecurePass123!',
                'password2': 'SecurePass123!'
            },
            format='json'
        )
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestTokenSecurity:
    """JWT token security — tampering, expiry, blacklisting"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!'
        )

    def test_blacklisted_token_rejected_after_logout(self):
        """After logout the refresh token must be blacklisted"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(
            '/api/auth/logout/',
            {'refresh_token': str(refresh)},
            format='json'
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # Attempt to use the same refresh token after logout
        refresh_response = self.client.post(
            '/api/auth/token/refresh/',
            {'refresh': str(refresh)},
            format='json'
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_arbitrary_token_rejected(self):
        """A completely arbitrary JWT string must be rejected"""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo'
        )
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_with_modified_user_id_rejected(self):
        """A token with tampered user_id claim must be rejected"""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
            '.eyJ1c2VyX2lkIjo5OTk5fQ.INVALID_SIGNATURE'
        )
        response = self.client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPrivilegeEscalation:
    """A5: Broken Access Control — privilege escalation via API"""

    def setup_method(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username='regularuser', email='regular@e.com', password='pass123'
        )
        self.admin = User.objects.create_user(
            username='adminuser', email='admin@e.com', password='pass123'
        )
        self.admin.profile.role = 2
        self.admin.profile.save()

    def test_regular_user_cannot_access_admin_profile(self):
        """Regular user profile endpoint must not expose admin-only data"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/auth/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'regularuser'

    def test_regular_user_cannot_update_own_role_to_admin(self):
        """Users must not be able to elevate their own role via profile update"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(
            '/api/auth/profile/',
            {'profile': {'role': 1}},
            format='json'
        )
        self.regular_user.profile.refresh_from_db()
        assert self.regular_user.profile.role == 3  # must remain regular user

    def test_unauthenticated_change_password_blocked(self):
        """Unauthenticated password change must be rejected"""
        response = self.client.post(
            '/api/auth/change-password/',
            {'old_password': 'pass123', 'new_password': 'newpass', 'new_password2': 'newpass'},
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_change_another_users_password(self):
        """A user must only be able to change their own password"""
        self.client.force_authenticate(user=self.regular_user)
        # ChangePasswordView always uses request.user, so this test confirms
        # there's no way to target another user's password
        response = self.client.post(
            '/api/auth/change-password/',
            {
                'old_password': 'pass123',
                'new_password': 'NewSecurePass!',
                'new_password2': 'NewSecurePass!'
            },
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        self.admin.refresh_from_db()
        # Admin password unchanged
        assert self.admin.check_password('pass123')
