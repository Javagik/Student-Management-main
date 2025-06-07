from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class FacultyAdviser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculty_advisers'
    )

    def __str__(self):
        return self.name

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    major = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    faculty_adviser = models.ForeignKey(
        FacultyAdviser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='advised_students'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    class Meta:
        ordering = ['last_name', 'first_name']

class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True, null=True)
    credits = models.PositiveIntegerField()
    instructor = models.ForeignKey(
        'FacultyAdviser',
        on_delete=models.SET_NULL,
        null=True,  # Allow nulls since some subjects might not have an instructor
        blank=True,
        related_name='subjects'
    )
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

    class Meta:
        ordering = ['subject_code']

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ], default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student} - {self.subject}"

class Grade(models.Model):
    GRADE_TYPES = [
        ('activity', 'Activity'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPES)
    title = models.CharField(max_length=200)  # e.g., "Quiz 1", "Final Exam"
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0)]
    )
    date_given = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_given']
        unique_together = ['enrollment', 'grade_type', 'title']

    def __str__(self):
        return f"{self.enrollment} - {self.grade_type} - {self.title}"

    @property
    def percentage(self):
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0

class GradeCategory(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grade_categories')
    category_type = models.CharField(max_length=20, choices=Grade.GRADE_TYPES)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['subject', 'category_type']
        verbose_name_plural = 'Grade Categories'

    def __str__(self):
        return f"{self.subject} - {self.category_type} ({self.weight}%)"

# New Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
