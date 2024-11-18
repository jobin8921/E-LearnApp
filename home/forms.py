from django import forms
from .models import Course, StaffProfile,Question

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class ApproveStaffForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['is_approved', 'assigned_course']
