# Register your models here.
from django.contrib import admin
from .models import School, Class, Subject, Lecture, Attendance

# Register all your new models so they appear in the admin panel
admin.site.register(School)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Lecture)
admin.site.register(Attendance)
