from rest_framework import serializers
from .models import Student, Subject, Enrollment, Grade, GradeCategory

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'address', 'phone_number', 'is_active']
        read_only_fields = ['id']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_code', 'subject_name', 'department', 'credits', 'instructor']
        read_only_fields = ['id']

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'student_name', 'subject_name', 'grade_type', 'title', 'score', 'max_score', 'percentage', 'date_given', 'remarks']
        read_only_fields = ['id']

    def get_student_name(self, obj):
        return f"{obj.enrollment.student.first_name} {obj.enrollment.student.last_name}"

    def get_subject_name(self, obj):
        return obj.enrollment.subject.subject_name

    def get_percentage(self, obj):
        if obj.max_score:
            return round((obj.score / obj.max_score) * 100, 2)
        return None

class GradeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeCategory
        fields = ['id', 'subject', 'category_type', 'weight', 'description']

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    grades = GradeSerializer(many=True, read_only=True)
    final_grade = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'enrollment_date', 'status', 'grades', 'final_grade']
        read_only_fields = ['id', 'enrollment_date']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_subject_name(self, obj):
        return obj.subject.subject_name

    def get_final_grade(self, obj):
        grades = obj.grades.all()
        if not grades:
            return None

        # Get grade categories for the subject
        categories = GradeCategory.objects.filter(subject=obj.subject)
        if not categories:
            return None

        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0

        for category in categories:
            category_grades = grades.filter(grade_type=category.category_type)
            if category_grades:
                category_avg = sum(grade.percentage for grade in category_grades) / len(category_grades)
                weighted_sum += category_avg * category.weight
                total_weight += category.weight

        if total_weight == 0:
            return None

        return weighted_sum / total_weight 