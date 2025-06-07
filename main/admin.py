from django.contrib import admin
from .models import Student, Subject, Enrollment, Grade, GradeCategory, FacultyAdviser

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'email', 'major', 'faculty_adviser', 'is_active')
    list_filter = ('major', 'is_active', 'faculty_adviser')
    search_fields = ('first_name', 'last_name', 'student_id', 'email')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'instructor', 'credits', 'capacity')
    list_filter = ('instructor', 'credits')
    search_fields = ('subject_code', 'subject_name', 'instructor')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'enrollment_date', 'created_at')
    list_filter = ('subject__subject_name', 'enrollment_date')
    search_fields = ('student__first_name', 'student__last_name', 'subject__subject_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'grade_type', 'title', 'score', 'max_score', 'percentage', 'date_given')
    list_filter = ('grade_type', 'date_given')
    search_fields = ('enrollment__student__first_name', 'enrollment__student__last_name', 'enrollment__subject__subject_name', 'title')
    readonly_fields = ('percentage',)

@admin.register(GradeCategory)
class GradeCategoryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'category_type', 'weight')
    list_filter = ('category_type', 'subject')
    search_fields = ('subject__subject_name', 'description')

@admin.register(FacultyAdviser)
class FacultyAdviserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'office_location')
    search_fields = ('name', 'email')
