import pytest
from unittest.mock import MagicMock
from django.contrib.auth.models import User
from authentication.permissions import IsSuperAdmin, IsAdmin, IsOwnerOrAdmin, IsUser
from api.models import Task


def make_request(user):
    request = MagicMock()
    request.user = user
    return request


@pytest.mark.django_db
class TestIsSuperAdmin:
    """Test cases for IsSuperAdmin permission"""

    def setup_method(self):
        self.permission = IsSuperAdmin()

    def test_super_admin_has_permission(self):
        user = User.objects.create_user(username='superadmin', password='pass')
        user.profile.role = 1
        user.profile.save()
        request = make_request(user)
        assert self.permission.has_permission(request, None) is True

    def test_admin_denied(self):
        user = User.objects.create_user(username='admin', password='pass')
        user.profile.role = 2
        user.profile.save()
        request = make_request(user)
        assert self.permission.has_permission(request, None) is False

    def test_regular_user_denied(self):
        user = User.objects.create_user(username='user', password='pass')
        request = make_request(user)
        assert self.permission.has_permission(request, None) is False

    def test_unauthenticated_denied(self):
        request = MagicMock()
        request.user = MagicMock(is_authenticated=False)
        assert self.permission.has_permission(request, None) is False

    def test_no_user_denied(self):
        request = MagicMock()
        request.user = None
        assert not self.permission.has_permission(request, None)


@pytest.mark.django_db
class TestIsAdmin:
    """Test cases for IsAdmin permission"""

    def setup_method(self):
        self.permission = IsAdmin()

    def test_super_admin_has_permission(self):
        user = User.objects.create_user(username='superadmin', password='pass')
        user.profile.role = 1
        user.profile.save()
        request = make_request(user)
        assert self.permission.has_permission(request, None) is True

    def test_admin_has_permission(self):
        user = User.objects.create_user(username='admin', password='pass')
        user.profile.role = 2
        user.profile.save()
        request = make_request(user)
        assert self.permission.has_permission(request, None) is True

    def test_regular_user_denied(self):
        user = User.objects.create_user(username='user', password='pass')
        request = make_request(user)
        assert self.permission.has_permission(request, None) is False

    def test_unauthenticated_denied(self):
        request = MagicMock()
        request.user = MagicMock(is_authenticated=False)
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsOwnerOrAdmin:
    """Test cases for IsOwnerOrAdmin permission"""

    def setup_method(self):
        self.permission = IsOwnerOrAdmin()
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.profile.role = 2
        self.admin.profile.save()
        self.task = Task.objects.create(title='Test Task', created_by=self.owner)

    def test_owner_has_object_permission(self):
        request = make_request(self.owner)
        assert self.permission.has_object_permission(request, None, self.task) is True

    def test_admin_has_object_permission(self):
        request = make_request(self.admin)
        assert self.permission.has_object_permission(request, None, self.task) is True

    def test_other_user_denied(self):
        request = make_request(self.other_user)
        assert self.permission.has_object_permission(request, None, self.task) is False

    def test_unauthenticated_denied(self):
        request = MagicMock()
        request.user = MagicMock(is_authenticated=False)
        assert self.permission.has_object_permission(request, None, self.task) is False

    def test_obj_with_user_field(self):
        obj = MagicMock()
        del obj.created_by
        obj.user = self.owner
        request = make_request(self.owner)
        assert self.permission.has_object_permission(request, None, obj) is True

    def test_obj_is_user_itself(self):
        obj = self.owner
        request = make_request(self.owner)
        assert self.permission.has_object_permission(request, None, obj) is True


@pytest.mark.django_db
class TestIsUser:
    """Test cases for IsUser permission"""

    def setup_method(self):
        self.permission = IsUser()

    def test_authenticated_user_has_permission(self):
        user = User.objects.create_user(username='user', password='pass')
        request = make_request(user)
        assert self.permission.has_permission(request, None) is True

    def test_unauthenticated_denied(self):
        request = MagicMock()
        request.user = MagicMock(is_authenticated=False)
        assert not self.permission.has_permission(request, None)

    def test_no_user_denied(self):
        request = MagicMock()
        request.user = None
        assert not self.permission.has_permission(request, None)
