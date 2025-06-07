from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import StudentViewSet, SubjectViewSet, EnrollmentViewSet, GradeViewSet
from django.conf.urls.static import static
from django.conf import settings

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)

app_name = 'main'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # Web interface URLs
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student URLs
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/grades/', views.student_grades, name='student_grades'),
    path('students/<int:pk>/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Enrollment URLs
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/add/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/edit/', views.enrollment_update, name='enrollment_update'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),
    
    # Grade URLs
    path('students/<int:student_id>/grades/add/', views.grade_create, name='grade_create'),
    path('grades/<int:pk>/edit/', views.grade_edit, name='grade_edit'),
    path('grades/<int:pk>/delete/', views.grade_delete, name='grade_delete'),
    path('students/<int:pk>/grades/manage/', views.grade_management, name='grade_management'),

    # FacultyAdviser URLs
    path('advisers/', views.faculty_adviser_list, name='faculty_adviser_list'),
    path('advisers/add/', views.faculty_adviser_create, name='faculty_adviser_create'),
    path('advisers/<int:pk>/', views.faculty_adviser_detail, name='faculty_adviser_detail'),
    path('advisers/<int:pk>/edit/', views.faculty_adviser_update, name='faculty_adviser_update'),
    path('advisers/<int:pk>/delete/', views.faculty_adviser_delete, name='faculty_adviser_delete'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 