from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    StudentViewSet, SubjectViewSet, EnrollmentViewSet,
    GradeViewSet, GradeCategoryViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'grade-categories', GradeCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
] 