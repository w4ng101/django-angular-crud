import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Task


@pytest.mark.django_db
class TestTaskAPI:
    """Test cases for Task API endpoints"""

    def setup_method(self):
        """Set up test client and create test users"""
        self.client = APIClient()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.admin.profile.role = 2
        self.admin.profile.save()
        
        self.tasks_url = '/api/tasks/'

    def test_create_task_authenticated(self):
        """Test creating a task as authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'status': 'TODO',
            'priority': 'HIGH',
            'due_date': '2026-02-25'
        }
        
        response = self.client.post(self.tasks_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert Task.objects.count() == 1
        # Verify the task was created by the authenticated user
        task = Task.objects.first()
        assert task.created_by == self.user

    def test_create_task_unauthenticated(self):
        """Test creating a task without authentication"""
        data = {
            'title': 'New Task',
            'description': 'Task description'
        }
        
        response = self.client.post(self.tasks_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks_user_sees_own_only(self):
        """Test that regular users only see their own tasks"""
        # Create tasks for different users
        Task.objects.create(
            title='User Task 1',
            created_by=self.user
        )
        Task.objects.create(
            title='User Task 2',
            created_by=self.user
        )
        Task.objects.create(
            title='Admin Task',
            created_by=self.admin
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.tasks_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert all(
            task['created_by'] == self.user.id 
            for task in response.data['results']
        )

    def test_list_tasks_admin_sees_all(self):
        """Test that admin users see all tasks"""
        Task.objects.create(
            title='User Task',
            created_by=self.user
        )
        Task.objects.create(
            title='Admin Task',
            created_by=self.admin
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.tasks_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_retrieve_task(self):
        """Test retrieving a specific task"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Task'
        assert response.data['description'] == 'Test Description'

    def test_update_own_task(self):
        """Test updating own task"""
        task = Task.objects.create(
            title='Original Title',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'status': 'IN_PROGRESS',
            'priority': 'LOW'
        }
        
        response = self.client.put(
            f'{self.tasks_url}{task.id}/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        
        task.refresh_from_db()
        assert task.title == 'Updated Title'
        assert task.status == 'IN_PROGRESS'

    def test_update_other_user_task_forbidden(self):
        """Test that users cannot update other users' tasks"""
        other_user_task = Task.objects.create(
            title='Other User Task',
            created_by=self.admin
        )
        
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Hacked Title'}
        response = self.client.put(
            f'{self.tasks_url}{other_user_task.id}/',
            data,
            format='json'
        )
        
        # Returns 404 because user can't see other users' tasks in the queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_own_task(self):
        """Test deleting own task"""
        task = Task.objects.create(
            title='Task to Delete',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.tasks_url}{task.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Task.objects.count() == 0

    def test_delete_other_user_task_forbidden(self):
        """Test that users cannot delete other users' tasks"""
        other_user_task = Task.objects.create(
            title='Other User Task',
            created_by=self.admin
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.tasks_url}{other_user_task.id}/')
        
        # Returns 404 because user can't see other users' tasks in the queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.count() == 1

    def test_admin_can_update_any_task(self):
        """Test that admin can update any task"""
        user_task = Task.objects.create(
            title='User Task',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'title': 'Admin Updated Title',
            'status': 'DONE',
            'priority': 'HIGH'
        }
        
        response = self.client.put(
            f'{self.tasks_url}{user_task.id}/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Admin Updated Title'

    def test_complete_task(self):
        """Test marking task as complete"""
        task = Task.objects.create(
            title='Task to Complete',
            status='TODO',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'{self.tasks_url}{task.id}/complete/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completed'] is True
        assert response.data['status'] == 'DONE'

    def test_uncomplete_task(self):
        """Test marking task as incomplete"""
        task = Task.objects.create(
            title='Completed Task',
            status='DONE',
            completed=True,
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'{self.tasks_url}{task.id}/uncomplete/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completed'] is False

    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        Task.objects.create(
            title='Todo Task',
            status='TODO',
            created_by=self.user
        )
        Task.objects.create(
            title='In Progress Task',
            status='IN_PROGRESS',
            created_by=self.user
        )
        Task.objects.create(
            title='Done Task',
            status='DONE',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}?status=TODO')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['status'] == 'TODO'

    def test_filter_tasks_by_priority(self):
        """Test filtering tasks by priority"""
        Task.objects.create(
            title='High Priority',
            priority='HIGH',
            created_by=self.user
        )
        Task.objects.create(
            title='Low Priority',
            priority='LOW',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}?priority=HIGH')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['priority'] == 'HIGH'

    def test_my_tasks_returns_only_own_tasks(self):
        """Test my_tasks endpoint returns only the authenticated user's tasks"""
        Task.objects.create(title='My Task', created_by=self.user)
        Task.objects.create(title='Admin Task', created_by=self.admin)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}my_tasks/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'My Task'

    def test_statistics_returns_correct_counts(self):
        """Test statistics endpoint returns correct task counts"""
        Task.objects.create(title='Todo', status='TODO', created_by=self.user)
        Task.objects.create(title='In Progress', status='IN_PROGRESS', created_by=self.user)
        Task.objects.create(title='Done', status='DONE', completed=True, created_by=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}statistics/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 3
        assert response.data['todo'] == 1
        assert response.data['in_progress'] == 1
        assert response.data['done'] == 1
        assert response.data['completed'] == 1

    def test_statistics_admin_sees_all(self):
        """Test statistics for admin includes all users' tasks"""
        Task.objects.create(title='User Task', status='TODO', created_by=self.user)
        Task.objects.create(title='Admin Task', status='TODO', created_by=self.admin)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'{self.tasks_url}statistics/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 2

    def test_search_tasks_by_title(self):
        """Test searching tasks by title"""
        Task.objects.create(title='Fix login bug', created_by=self.user)
        Task.objects.create(title='Add dashboard', created_by=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.tasks_url}?search=login')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Fix login bug'
