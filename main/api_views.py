from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Student, Subject, Enrollment, Grade
from .serializers import StudentSerializer, SubjectSerializer, EnrollmentSerializer, GradeSerializer

class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing students
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Student.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                student_id__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        return queryset

class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing subjects
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                subject_code__icontains=search
            ) | queryset.filter(
                subject_name__icontains=search
            )
        return queryset

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing enrollments
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        subject_id = self.request.query_params.get('subject_id', None)
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset

class GradeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing grades
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Grade.objects.all()
        enrollment_id = self.request.query_params.get('enrollment_id', None)
        student_id = self.request.query_params.get('student_id', None)
        
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        return queryset 