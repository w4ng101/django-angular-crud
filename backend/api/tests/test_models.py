import pytest
from django.contrib.auth.models import User
from api.models import Task
from datetime import date


@pytest.mark.django_db
class TestTaskModel:
    """Test cases for Task model"""

    def setup_method(self):
        """Create test users"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.admin.profile.role = 2
        self.admin.profile.save()

    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            status='TODO',
            priority='HIGH',
            due_date='2026-02-25',
            created_by=self.user
        )
        
        assert task.title == 'Test Task'
        assert task.description == 'Test Description'
        assert task.status == 'TODO'
        assert task.priority == 'HIGH'
        assert task.completed is False
        assert task.created_by == self.user

    def test_task_str_representation(self):
        """Test string representation of task"""
        task = Task.objects.create(
            title='My Task',
            description='Description',
            created_by=self.user
        )
        
        assert str(task) == 'My Task'

    def test_task_default_values(self):
        """Test default values for task fields"""
        task = Task.objects.create(
            title='Simple Task',
            created_by=self.user
        )
        
        assert task.description == ''
        assert task.status == 'TODO'
        assert task.priority == 'MEDIUM'
        assert task.completed is False
        assert task.due_date is None

    def test_task_status_choices(self):
        """Test different task status values"""
        statuses = ['TODO', 'IN_PROGRESS', 'DONE']
        
        for status in statuses:
            task = Task.objects.create(
                title=f'Task {status}',
                status=status,
                created_by=self.user
            )
            assert task.status == status

    def test_task_priority_choices(self):
        """Test different task priority values"""
        priorities = ['LOW', 'MEDIUM', 'HIGH']
        
        for priority in priorities:
            task = Task.objects.create(
                title=f'Task {priority}',
                priority=priority,
                created_by=self.user
            )
            assert task.priority == priority

    def test_task_completion(self):
        """Test marking task as completed"""
        task = Task.objects.create(
            title='Test Task',
            status='TODO',
            created_by=self.user
        )
        
        assert task.completed is False
        
        task.completed = True
        task.status = 'DONE'
        task.save()
        
        assert task.completed is True
        assert task.status == 'DONE'

    def test_task_with_due_date(self):
        """Test task with due date"""
        due_date = date(2026, 3, 1)
        task = Task.objects.create(
            title='Task with deadline',
            due_date=due_date,
            created_by=self.user
        )
        
        assert task.due_date == due_date

    def test_multiple_tasks_same_user(self):
        """Test creating multiple tasks for same user"""
        Task.objects.create(
            title='Task 1',
            created_by=self.user
        )
        Task.objects.create(
            title='Task 2',
            created_by=self.user
        )
        
        user_tasks = Task.objects.filter(created_by=self.user)
        assert user_tasks.count() == 2

    def test_task_deletion_cascade(self):
        """Test that tasks are deleted when user is deleted"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user
        )
        
        user_id = self.user.id
        self.user.delete()
        
        # Task should be deleted due to CASCADE
        with pytest.raises(Task.DoesNotExist):
            Task.objects.get(id=task.id)

    def test_task_timestamps(self):
        """Test that timestamps are set correctly"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user
        )
        
        assert task.created_at is not None
        assert task.updated_at is not None
        # Timestamps should be very close (within 1 second)
        time_diff = abs((task.updated_at - task.created_at).total_seconds())
        assert time_diff < 1
        
        # Update task
        original_created_at = task.created_at
        task.title = 'Updated Title'
        task.save()
        
        assert task.created_at == original_created_at
        assert task.updated_at > task.created_at
