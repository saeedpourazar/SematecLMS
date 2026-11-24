from django.contrib import admin
from .models import Instructor, Course, Enrollment, Category



admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Category)