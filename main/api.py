from rest_framework import viewsets, permissions
from .models import Student, Subject, Enrollment, Grade, GradeCategory
from .serializers import (
    StudentSerializer, SubjectSerializer, EnrollmentSerializer,
    GradeSerializer, GradeCategorySerializer
)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Student.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                student_id__icontains=search
            )
        return queryset

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                subject_name__icontains=search
            ) | queryset.filter(
                subject_code__icontains=search
            )
        return queryset

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get('student', None)
        subject_id = self.request.query_params.get('subject', None)
        status = self.request.query_params.get('status', None)
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Grade.objects.all()
        enrollment_id = self.request.query_params.get('enrollment', None)
        grade_type = self.request.query_params.get('type', None)
        
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)
        if grade_type:
            queryset = queryset.filter(grade_type=grade_type)
            
        return queryset

class GradeCategoryViewSet(viewsets.ModelViewSet):
    queryset = GradeCategory.objects.all()
    serializer_class = GradeCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = GradeCategory.objects.all()
        subject_id = self.request.query_params.get('subject', None)
        category_type = self.request.query_params.get('type', None)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if category_type:
            queryset = queryset.filter(category_type=category_type)
            
        return queryset 