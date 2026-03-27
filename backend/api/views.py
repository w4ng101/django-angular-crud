from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.db import transaction

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from authentication.permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task API
    - Clean DRF conventions
    - Optimized QuerySet
    - Scalable filtering
    - SOA-ready design
    """

    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["status", "priority", "completed", "created_by"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority"]
    ordering = ["-created_at"]

    # ----------------------------------------------------
    # SERIALIZER SELECTION
    # ----------------------------------------------------
    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        return TaskSerializer

    # ----------------------------------------------------
    # QUERY OPTIMIZATION
    # ----------------------------------------------------
    def get_queryset(self):
        user = self.request.user

        base_qs = (
            Task.objects
            .select_related("created_by")
            .only(
                "id",
                "title",
                "status",
                "priority",
                "completed",
                "created_at",
                "updated_at",
                "due_date",
                "created_by",
            )
        )

        if getattr(user, "profile", None) and user.profile.is_admin:
            return base_qs

        return base_qs.filter(created_by=user)

    # ----------------------------------------------------
    # PERMISSIONS
    # ----------------------------------------------------
    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()

    # ----------------------------------------------------
    # CREATE HOOK
    # ----------------------------------------------------
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ----------------------------------------------------
    # DOMAIN ACTIONS
    # ----------------------------------------------------
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def complete(self, request, pk=None):
        task = self.get_object()

        task.completed = True
        task.status = Task.Status.DONE
        task.save(update_fields=["completed", "status"])

        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def uncomplete(self, request, pk=None):
        task = self.get_object()

        task.completed = False
        task.status = Task.Status.TODO
        task.save(update_fields=["completed", "status"])

        return Response(self.get_serializer(task).data)

    # ----------------------------------------------------
    # USER TASKS
    # ----------------------------------------------------
    @action(detail=False, methods=["get"])
    def my_tasks(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ----------------------------------------------------
    # STATISTICS (OPTIMIZED)
    # ----------------------------------------------------
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        stats = (
            self.get_queryset()
            .aggregate(
                total=Count("id"),
                completed=Count("id", filter=Q(completed=True)),
                todo=Count("id", filter=Q(status=Task.Status.TODO)),
                inprogress=Count(
                    "id", filter=Q(status=Task.Status.IN_PROGRESS)
                ),
                done=Count("id", filter=Q(status=Task.Status.DONE)),
            )
        )

        return Response(stats)