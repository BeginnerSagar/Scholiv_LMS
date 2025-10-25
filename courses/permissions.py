from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow users with role 'admin' or superusers to access an endpoint.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Grant permission if the user is a superuser OR their role is 'admin'
        return request.user.is_superuser or request.user.role == 'admin'

