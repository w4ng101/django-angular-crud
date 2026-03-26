import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from authentication.serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
)


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test cases for UserProfileSerializer"""

    def setup_method(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_contains_expected_fields(self):
        serializer = UserProfileSerializer(self.user.profile)
        expected_fields = {'role', 'role_display', 'phone', 'address', 'created_at', 'updated_at'}
        assert set(serializer.data.keys()) == expected_fields

    def test_role_display_default_user(self):
        serializer = UserProfileSerializer(self.user.profile)
        assert serializer.data['role'] == 3
        assert serializer.data['role_display'] == 'User'

    def test_role_display_admin(self):
        self.user.profile.role = 2
        self.user.profile.save()
        serializer = UserProfileSerializer(self.user.profile)
        assert serializer.data['role_display'] == 'Admin'

    def test_role_display_super_admin(self):
        self.user.profile.role = 1
        self.user.profile.save()
        serializer = UserProfileSerializer(self.user.profile)
        assert serializer.data['role_display'] == 'Super Admin'


@pytest.mark.django_db
class TestUserSerializer:
    """Test cases for UserSerializer"""

    def setup_method(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_contains_expected_fields(self):
        serializer = UserSerializer(self.user)
        # 'role' is write_only so it won't appear in serializer.data
        expected_fields = {'id', 'username', 'email', 'first_name', 'last_name', 'profile'}
        assert set(serializer.data.keys()) == expected_fields

    def test_profile_nested(self):
        serializer = UserSerializer(self.user)
        assert 'role' in serializer.data['profile']
        assert 'role_display' in serializer.data['profile']

    def test_id_is_read_only(self):
        serializer = UserSerializer(self.user)
        assert serializer.data['id'] == self.user.id


@pytest.mark.django_db
class TestRegisterSerializer:
    """Test cases for RegisterSerializer"""

    def test_valid_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'WrongPass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_username_required(self):
        data = {
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_default_role_is_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.profile.role == 3

    def test_non_super_admin_cannot_create_admin(self):
        factory = APIRequestFactory()
        request = factory.post('/')
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='pass123'
        )
        request.user = regular_user

        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 2,
        }
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
        user = serializer.save()
        assert user.profile.role == 3  # forced to User

    def test_super_admin_can_create_admin(self):
        factory = APIRequestFactory()
        request = factory.post('/')
        super_admin = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='pass123'
        )
        super_admin.profile.role = 1
        super_admin.profile.save()
        request.user = super_admin

        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 2,
        }
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
        user = serializer.save()
        assert user.profile.role == 2

    def test_duplicate_username(self):
        User.objects.create_user(username='existing', email='e@e.com', password='pass')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors


class TestChangePasswordSerializer:
    """Test cases for ChangePasswordSerializer"""

    def test_valid_data(self):
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        }
        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_new_password_mismatch(self):
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'new_password2': 'WrongPass123!',
        }
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_old_password_required(self):
        data = {
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        }
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()
        assert 'old_password' in serializer.errors

    def test_new_password_required(self):
        data = {
            'old_password': 'OldPass123!',
            'new_password2': 'NewPass123!',
        }
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
