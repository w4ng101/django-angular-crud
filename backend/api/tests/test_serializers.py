import pytest
from django.contrib.auth.models import User
from api.models import Task
from api.serializers import TaskSerializer, TaskCreateSerializer


@pytest.mark.django_db
class TestTaskSerializer:
    """Test cases for TaskSerializer"""

    def setup_method(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_serializer_contains_expected_fields(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        serializer = TaskSerializer(task)
        expected_fields = {
            'id', 'title', 'description', 'status', 'priority',
            'created_by', 'created_by_username', 'created_by_email',
            'created_by_role', 'created_by_role_display',
            'created_at', 'updated_at', 'due_date', 'completed'
        }
        assert set(serializer.data.keys()) == expected_fields

    def test_serializer_read_only_fields(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        serializer = TaskSerializer(task)
        assert serializer.data['created_by_username'] == 'testuser'
        assert serializer.data['created_by_email'] == 'test@example.com'
        assert serializer.data['created_by_role'] == 3  # default User role
        assert serializer.data['created_by_role_display'] == 'User'

    def test_serializer_default_values(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        serializer = TaskSerializer(task)
        assert serializer.data['status'] == 'TODO'
        assert serializer.data['priority'] == 'MEDIUM'
        assert serializer.data['completed'] is False
        assert serializer.data['description'] == ''

    def test_serializer_with_all_fields(self):
        task = Task.objects.create(
            title='Full Task',
            description='A description',
            status='IN_PROGRESS',
            priority='HIGH',
            completed=False,
            due_date='2026-12-31',
            created_by=self.user
        )
        serializer = TaskSerializer(task)
        assert serializer.data['title'] == 'Full Task'
        assert serializer.data['description'] == 'A description'
        assert serializer.data['status'] == 'IN_PROGRESS'
        assert serializer.data['priority'] == 'HIGH'

    def test_serializer_admin_role_display(self):
        self.user.profile.role = 2
        self.user.profile.save()
        task = Task.objects.create(title='Admin Task', created_by=self.user)
        serializer = TaskSerializer(task)
        assert serializer.data['created_by_role'] == 2
        assert serializer.data['created_by_role_display'] == 'Admin'

    def test_serializer_many(self):
        Task.objects.create(title='Task 1', created_by=self.user)
        Task.objects.create(title='Task 2', created_by=self.user)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        assert len(serializer.data) == 2


@pytest.mark.django_db
class TestTaskCreateSerializer:
    """Test cases for TaskCreateSerializer"""

    def test_serializer_contains_expected_fields(self):
        serializer = TaskCreateSerializer()
        expected_fields = {'title', 'description', 'status', 'priority', 'due_date', 'completed'}
        assert set(serializer.fields.keys()) == expected_fields

    def test_valid_data(self):
        data = {
            'title': 'New Task',
            'description': 'Description',
            'status': 'TODO',
            'priority': 'HIGH',
        }
        serializer = TaskCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_title_required(self):
        data = {'description': 'No title'}
        serializer = TaskCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_invalid_status(self):
        data = {'title': 'Task', 'status': 'INVALID_STATUS'}
        serializer = TaskCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_invalid_priority(self):
        data = {'title': 'Task', 'priority': 'INVALID_PRIORITY'}
        serializer = TaskCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'priority' in serializer.errors

    def test_does_not_include_created_by(self):
        serializer = TaskCreateSerializer()
        assert 'created_by' not in serializer.fields
