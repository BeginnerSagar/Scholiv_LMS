from rest_framework import permissions
from users.models import Role # Import our new Role class

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to SuperAdmin users.
    """
    message = 'You must be a Super Admin to perform this action.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Role.SUPER_ADMIN or request.user.is_superuser
        )

class IsSchoolAdmin(permissions.BasePermission):
    """
    Allows access only to SchoolAdmin users or SuperAdmins.
    """
    message = 'You must be a School Admin to perform this action.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Role.SCHOOL_ADMIN or 
            request.user.is_superuser
        )

class IsTeacher(permissions.BasePermission):
    """
    Allows access only to Teacher users, SchoolAdmins, or SuperAdmins.
    """
    message = 'You must be a Teacher to perform this action.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Role.TEACHER or
            request.user.role == Role.SCHOOL_ADMIN or
            request.user.is_superuser
        )