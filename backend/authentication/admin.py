from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.admin import admin_site
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'address')


class TaskInline(admin.TabularInline):
    """Inline admin for displaying user's tasks"""
    from api.models import Task
    model = Task
    extra = 0
    fields = ('title', 'status', 'priority', 'completed', 'due_date', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with tasks inline"""
    inlines = [UserProfileInline, TaskInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'role_display', 'is_staff', 'is_active', 'date_joined', 'task_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    def role_display(self, obj):
        """Display user's role"""
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return 'N/A'
    role_display.short_description = 'Role'
    role_display.admin_order_field = 'profile__role'
    
    def task_count(self, obj):
        """Display the number of tasks for each user"""
        return obj.tasks.count()
    task_count.short_description = 'Total Tasks'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


# Register with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile)

