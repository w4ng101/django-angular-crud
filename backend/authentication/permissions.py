from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Permission class to check if user is a super admin (role = 1)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.is_super_admin


class IsAdmin(permissions.BasePermission):
    """Permission class to check if user is an admin or super admin (role = 1 or 2)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission class to check if user is the owner of the object or an admin"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins to access any object
        if hasattr(request.user, 'profile') and request.user.profile.is_admin:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsUser(permissions.BasePermission):
    """Permission class to check if user has at least basic user role (role = 3)"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
