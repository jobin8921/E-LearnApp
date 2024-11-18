from django.contrib import admin
from .models import Course, Staff, Exam, Question


admin.site.register(Course)
admin.site.register(Staff)
admin.site.register(Exam)
admin.site.register(Question)
