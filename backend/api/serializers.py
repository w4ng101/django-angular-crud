from rest_framework import serializers
from .models import Task
from authentication.serializers import UserProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    created_by_role = serializers.IntegerField(source='created_by.profile.role', read_only=True)
    created_by_role_display = serializers.CharField(source='created_by.profile.get_role_display', read_only=True)
    
    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'priority',
            'created_by',
            'created_by_username',
            'created_by_email',
            'created_by_role',
            'created_by_role_display',
            'created_at',
            'updated_at',
            'due_date',
            'completed'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'created_by_username', 'created_by_email', 'created_by_role', 'created_by_role_display')


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Task
    """
    class Meta:
        model = Task
        fields = (
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'completed'
        )
