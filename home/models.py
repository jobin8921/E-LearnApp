from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.course.title})"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    courses = models.ManyToManyField(Course, related_name="staff_courses")


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise_area = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    assigned_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='not paid')
    assigned_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Exam(models.Model):
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title



class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200)
    option_4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'question')

    def __str__(self):
        return f"{self.student} - {self.question}"
