from django.urls import path
from .views import (
    home_view,
    course_list_view,
    instructor_list_view,
    course_detail_view,
    signup_view,
    login_view,
    logout_view,
    enroll_course_view,
    my_courses_view,
    dashboard_view,
    staff_dashboard_view,
    course_management_view,
    add_course_view,
    edit_course_view,
    delete_course_view,
    student_management_view,
    instructor_management_view,
    reports_view,
    add_instructor_view,
    edit_instructor_view,
    delete_instructor_view,
    export_instructors_view,
    export_instructor_courses_view,
    export_courses_view,
    export_students_view,
)
urlpatterns = [
    path('', home_view, name='home'),

    path('courses/', course_list_view, name='course_list'),
    path('courses/<int:pk>/', course_detail_view, name='course_detail'),

    path(
        'instructors/',
        instructor_list_view,
        name='instructor_list'
    ),

    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path(
        'courses/<int:pk>/enroll/',
        enroll_course_view,
        name='enroll_course'
    ),

    path('my-courses/', my_courses_view, name='my_courses'),


    path(
        'dashboard/',
        dashboard_view,
        name='dashboard'
    ),
    path('staff-dashboard/', staff_dashboard_view, name='staff_dashboard'),
    path(
        'staff/courses/',
        course_management_view,
        name='course_management'
    ),
    path(
        'staff/courses/add/',
        add_course_view,
        name='add_course'
    ),
    path(
        'staff/courses/<int:pk>/edit/',
        edit_course_view,
        name='edit_course'
    ),
    path(
        'staff/courses/<int:pk>/delete/',
        delete_course_view,
        name='delete_course'
    ),
    path(
        'staff/students/',
        student_management_view,
        name='student_management'
    ),
    path(
        'staff/instructors/',
        instructor_management_view,
        name='instructor_management'
    ),
    path(
        'staff/reports/',
        reports_view,
        name='reports'
    ),
    path(
        'staff/instructors/add/',
        add_instructor_view,
        name='add_instructor'
    ),
    path(
        'staff/instructors/<int:pk>/edit/',
        edit_instructor_view,
        name='edit_instructor'
    ),
    path(
        'staff/instructors/<int:pk>/delete/',
        delete_instructor_view,
        name='delete_instructor'
    ),
    path(
        'staff/export/instructors/',
        export_instructors_view,
        name='export_instructors'
    ),
    path(
        'staff/export/instructors/<int:pk>/courses/',
        export_instructor_courses_view,
        name='export_instructor_courses'
    ),
    path(
        'staff/export/courses/',
        export_courses_view,
        name='export_courses'
    ),
    path(
        'staff/export/students/',
        export_students_view,
        name='export_students'
    ),
]