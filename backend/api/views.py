from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from authentication.permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Tasks
    Follows REST API and Service Oriented Architecture principles
    """
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'completed', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user role:
        - Super Admin & Admin: See all tasks
        - User: See only their own tasks
        """
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_admin:
            # Admins see all tasks
            return Task.objects.all().select_related('created_by__profile')
        # Regular users see only their tasks
        return Task.objects.filter(created_by=user).select_related('created_by__profile')
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Automatically set the created_by field to the authenticated user
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Custom action to mark a task as completed
        """
        task = self.get_object()
        task.completed = True
        task.status = 'DONE'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def uncomplete(self, request, pk=None):
        """
        Custom action to mark a task as not completed
        """
        task = self.get_object()
        task.completed = False
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """
        Get all tasks for the authenticated user
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get task statistics for the authenticated user
        """
        queryset = self.get_queryset()
        total = queryset.count()
        completed = queryset.filter(completed=True).count()
        todo = queryset.filter(status='TODO').count()
        in_progress = queryset.filter(status='IN_PROGRESS').count()
        done = queryset.filter(status='DONE').count()
        
        return Response({
            'total': total,
            'completed': completed,
            'todo': todo,
            'in_progress': in_progress,
            'done': done,
        })
