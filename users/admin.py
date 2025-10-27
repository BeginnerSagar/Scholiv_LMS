from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# We need to create a custom admin class to show our new fields
class CustomUserAdmin(UserAdmin):
    # This displays all the fields in the user list
    list_display = (
        "username", 
        "email", 
        "first_name", 
        "last_name", 
        "is_staff",
        "role",  # Show our custom role
        "school", # Show the user's school
        "assigned_class" # Show the user's class
    )
    
    # This adds our custom fields to the "edit user" page
    # We must organize them into fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'school', 'assigned_class')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'school', 'assigned_class')}),
    )

# Register your custom User model with your custom admin class
admin.site.register(User, CustomUserAdmin)
