from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Directory
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/checkin/', views.attendance_checkin, name='attendance_checkin'),
    path('attendance/mark/<int:employee_id>/', views.attendance_mark, name='attendance_mark'),

    # Leave management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/request/', views.leave_request_create, name='leave_request_create'),
    path('leaves/<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('leaves/<int:pk>/reject/', views.leave_reject, name='leave_reject'),
]
