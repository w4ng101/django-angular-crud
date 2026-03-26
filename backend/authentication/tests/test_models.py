import pytest
from django.contrib.auth.models import User
from authentication.models import UserProfile


@pytest.mark.django_db
class TestUserProfileModel:
    """Test cases for UserProfile model"""

    def test_create_user_profile(self):
        """Test that a UserProfile is created when a User is created"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert hasattr(user, 'profile')
        assert user.profile.role == 3  # Default role is User
        assert user.profile.user == user

    def test_user_profile_str(self):
        """Test the string representation of UserProfile"""
        user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='testpass123'
        )
        
        expected = "johndoe - User"
        assert str(user.profile) == expected

    def test_is_super_admin(self):
        """Test is_super_admin property"""
        user = User.objects.create_user(
            username='superadmin',
            email='super@example.com',
            password='testpass123'
        )
        user.profile.role = 1
        user.profile.save()
        
        assert user.profile.is_super_admin is True
        assert user.profile.is_admin is True
        assert user.profile.is_user is False

    def test_is_admin(self):
        """Test is_admin property"""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        user.profile.role = 2
        user.profile.save()
        
        assert user.profile.is_super_admin is False
        assert user.profile.is_admin is True
        assert user.profile.is_user is False

    def test_is_user(self):
        """Test is_user property"""
        user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123'
        )
        user.profile.role = 3
        user.profile.save()
        
        assert user.profile.is_super_admin is False
        assert user.profile.is_admin is False
        assert user.profile.is_user is True

    def test_get_role_display(self):
        """Test get_role_display method"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test Super Admin
        user.profile.role = 1
        user.profile.save()
        assert user.profile.get_role_display() == 'Super Admin'
        
        # Test Admin
        user.profile.role = 2
        user.profile.save()
        assert user.profile.get_role_display() == 'Admin'
        
        # Test User
        user.profile.role = 3
        user.profile.save()
        assert user.profile.get_role_display() == 'User'

    def test_profile_optional_fields(self):
        """Test optional fields in UserProfile"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Update profile with optional fields
        user.profile.phone = '+1234567890'
        user.profile.address = '123 Test Street'
        user.profile.save()
        
        assert user.profile.phone == '+1234567890'
        assert user.profile.address == '123 Test Street'

    def test_multiple_users_different_roles(self):
        """Test creating multiple users with different roles"""
        super_admin = User.objects.create_user(
            username='superadmin',
            email='super@example.com',
            password='testpass123'
        )
        super_admin.profile.role = 1
        super_admin.profile.save()
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin.profile.role = 2
        admin.profile.save()
        
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        # Default role is 3
        
        assert UserProfile.objects.count() == 3
        assert super_admin.profile.is_super_admin is True
        assert admin.profile.is_admin is True
        assert user.profile.is_user is True
