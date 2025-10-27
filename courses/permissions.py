from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to SuperAdmins.
    This includes the user you created with 'createsuperuser'.
    """

    def has_permission(self, request, view):
        # request.user is available because we use IsAuthenticated
        return request.user and (
            request.user.is_superuser or 
            request.user.role == 'super_admin'
        )


class IsSchoolAdmin(BasePermission):
    """
    Allows access only to School Admins.
    We also check for SuperAdmin, as they should be able to do anything.
    """

    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or
            request.user.role == 'super_admin' or
            request.user.role == 'school_admin'
        )


class IsTeacher(BasePermission):
    """
    Allows access only to Teachers.
    We also include Admins and SuperAdmins.
    """

    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or
            request.user.role == 'super_admin' or
            request.user.role == 'school_admin' or
            request.user.role == 'teacher'
        )

# Note: We don't need a permission for 'Student' because the default
# behavior will be to deny access unless one of these permissions is met.
# Authenticated students will have a 'student' role but will fail
# these permission checks, which is what we want for Admin endpoints.

