from django.contrib import admin
from django.utils.html import format_html
from .models import Task
from core.admin import admin_site


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by_link', 'status_badge', 'priority_badge', 'completed_icon', 'due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'completed', 'created_at', 'created_by')
    search_fields = ('title', 'description', 'created_by__username', 'created_by__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'created_by_details')
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'completed', 'due_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by_details'),
            'classes': ('collapse',)
        }),
    )
    
    def created_by_link(self, obj):
        """Display created_by username as a clickable link"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse('admin:auth_user_change', args=[obj.created_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.created_by.username)
    created_by_link.short_description = 'Created By'
    created_by_link.admin_order_field = 'created_by__username'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'TODO': '#2196F3',
            'IN_PROGRESS': '#9C27B0',
            'DONE': '#4CAF50'
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def priority_badge(self, obj):
        """Display priority with color badge"""
        colors = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#F44336'
        }
        color = colors.get(obj.priority, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.priority
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def completed_icon(self, obj):
        """Display completed status as icon"""
        if obj.completed:
            return format_html('<span style="color: green; font-size: 18px;">✓</span>')
        return format_html('<span style="color: red; font-size: 18px;">✗</span>')
    completed_icon.short_description = 'Completed'
    completed_icon.admin_order_field = 'completed'
    
    def created_by_details(self, obj):
        """Display detailed information about the creator"""
        user = obj.created_by
        return format_html(
            '<strong>Username:</strong> {}<br>'
            '<strong>Email:</strong> {}<br>'
            '<strong>Full Name:</strong> {} {}<br>'
            '<strong>Total Tasks:</strong> {}',
            user.username,
            user.email or 'N/A',
            user.first_name or '',
            user.last_name or '',
            user.tasks.count()
        )
    created_by_details.short_description = 'Creator Details'
    
    def get_queryset(self, request):
        """Optimize queryset by selecting related user data"""
        qs = super().get_queryset(request)
        return qs.select_related('created_by')
    
    actions = ['mark_as_todo', 'mark_as_in_progress', 'mark_as_done', 'mark_as_completed']
    
    def mark_as_todo(self, request, queryset):
        updated = queryset.update(status='TODO')
        self.message_user(request, f'{updated} task(s) marked as TODO.')
    mark_as_todo.short_description = 'Mark selected tasks as TODO'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} task(s) marked as IN PROGRESS.')
    mark_as_in_progress.short_description = 'Mark selected tasks as IN PROGRESS'
    
    def mark_as_done(self, request, queryset):
        updated = queryset.update(status='DONE', completed=True)
        self.message_user(request, f'{updated} task(s) marked as DONE.')
    mark_as_done.short_description = 'Mark selected tasks as DONE'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(completed=True)
        self.message_user(request, f'{updated} task(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected tasks as completed'


# Register with custom admin site
admin_site.register(Task, TaskAdmin)

