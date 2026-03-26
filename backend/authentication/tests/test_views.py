import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test cases for Authentication API endpoints"""

    def setup_method(self):
        """Set up test client and create test users"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/profile/'

    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert response.data['user']['email'] == 'newuser@example.com'
        
        # Verify user was created in database
        user = User.objects.get(username='newuser')
        assert user is not None
        assert user.profile.role == 3  # Default role

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_duplicate_username(self):
        """Test registration with existing username"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login(self):
        """Test user login endpoint"""
        # Create a test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'testuser'
        assert response.data['user']['email'] == 'test@example.com'

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_authenticated(self):
        """Test getting profile for authenticated user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate the user
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert 'profile' in response.data

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_authenticated(self):
        """Test logout endpoint with authenticated user"""
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/auth/logout/', {}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Logout successful'

    def test_logout_unauthenticated(self):
        """Test logout endpoint without authentication"""
        response = self.client.post('/api/auth/logout/', {}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self):
        """Test changing password with correct old password"""
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='OldPass123!'
        )
        self.client.force_authenticate(user=user)

        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password changed successfully'
        user.refresh_from_db()
        assert user.check_password('NewPass456!')

    def test_change_password_wrong_old_password(self):
        """Test changing password with incorrect old password"""
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='OldPass123!'
        )
        self.client.force_authenticate(user=user)

        data = {
            'old_password': 'WrongPass!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_change_password_mismatched_new_passwords(self):
        """Test changing password when new passwords don't match"""
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='OldPass123!'
        )
        self.client.force_authenticate(user=user)

        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password2': 'Different456!',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self):
        """Test change password endpoint without authentication"""
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
