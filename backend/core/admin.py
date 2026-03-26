from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.contrib.auth.models import User
from api.models import Task


class CustomAdminSite(admin.AdminSite):
    site_header = 'Django Angular CRUD Administration'
    site_title = 'Admin Portal'
    index_title = 'Dashboard Overview'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='custom_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Custom dashboard view with statistics"""
        context = {
            **self.each_context(request),
            'total_users': User.objects.count(),
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(completed=True).count(),
            'pending_tasks': Task.objects.filter(completed=False).count(),
            'tasks_by_status': {
                'todo': Task.objects.filter(status='TODO').count(),
                'in_progress': Task.objects.filter(status='IN_PROGRESS').count(),
                'done': Task.objects.filter(status='DONE').count(),
            },
            'recent_tasks': Task.objects.select_related('created_by').order_by('-created_at')[:10],
            'recent_users': User.objects.order_by('-date_joined')[:10],
        }
        return render(request, 'admin/custom_dashboard.html', context)


# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')
