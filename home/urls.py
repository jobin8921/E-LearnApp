from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [   
    path('', views.home, name='home'),  

    path('student_register/', views.student_register, name='student_register'),
    path('student_login/', views.student_login, name='student_login'),
    path('choose_course/', views.choose_course, name='choose_course'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('submit_exam/<int:exam_id>/', views.submit_exam, name='submit_exam'),
    path('add_questions/<int:exam_id>/', views.add_questions, name='add_questions'),


    path('add-subject/', views.add_subject, name='add_subject'),
    path('take_exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),  
    path('staff_register/', views.staff_register, name='staff_register'),  
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_login/', views.staff_login, name='staff_login'),  
    path('admin_register/', views.admin_register, name='admin_register'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'), 
    path('approve_student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('approve_student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject_student/<int:student_id>/', views.reject_student, name='reject_student'),
    path('approve_student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject_student/<int:student_id>/', views.reject_student, name='reject_student'),
    path('approve_staff/<int:staff_id>/', views.approve_staff, name='approve_staff'),
    path('reject_staff/<int:staff_id>/', views.reject_staff, name='reject_staff'),
    path('add_course/', views.add_course, name='add_course'),
    path('start_exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('exam_results/<int:exam_id>/', views.exam_results, name='exam_results'),


]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,doumenty_root=settings.STATIC_ROOT)