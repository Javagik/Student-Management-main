from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Student, Subject, Enrollment, Grade, FacultyAdviser, Department
from .forms import StudentForm, SubjectForm, EnrollmentForm, GradeForm, FacultyAdviserForm, DepartmentForm
from django.db.models import Avg, FloatField # Import Avg and FloatField
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('main:home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = 'main:login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

login_view = CustomLoginView.as_view()
logout_view = CustomLogoutView.as_view()

def home(request):
    students_count = Student.objects.count()
    subjects_count = Subject.objects.count()
    enrolled_students_count = Student.objects.filter(enrollments__isnull=False).distinct().count()
    faculty_advisers_count = FacultyAdviser.objects.count()

    context = {
        'title': 'Home',
        'students_count': students_count,
        'subjects_count': subjects_count,
        'enrollments_count': enrolled_students_count,
        'faculty_advisers_count': faculty_advisers_count,
    }
    return render(request, 'main/home.html', context)

# Student Views
@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'main/student_list.html', {
        'title': 'Students',
        'students': students
    })

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.all()
    return render(request, 'main/student_detail.html', {
        'title': f'Student: {student}',
        'student': student,
        'enrollments': enrollments
    })

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully!')
            return redirect('main:student_list')
    else:
        form = StudentForm()
    return render(request, 'main/student_form.html', {
        'title': 'Add Student',
        'form': form
    })

@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('main:student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'main/student_form.html', {
        'title': f'Edit Student: {student}',
        'form': form
    })

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('main:student_list')
    return render(request, 'main/student_confirm_delete.html', {
        'title': f'Delete Student: {student}',
        'student': student
    })

def calculate_gpa(percentage):
    if percentage >= 93:
        return 1.00  # Excellent
    elif percentage >= 87:
        return 2.00  # Very Good
    elif percentage >= 80:
        return 3.00  # Good
    elif percentage >= 75:
        return 4.00  # Failed
    else:
        return 5.00  # Drop

def get_letter_grade(percentage):
    if percentage >= 93:
        return 'A'  # 1.00 (Excellent)
    elif percentage >= 87:
        return 'B'  # 2.00 (Very Good)
    elif percentage >= 80:
        return 'C'  # 3.00 (Good)
    elif percentage >= 75:
        return 'D'  # 4.00 (Failed)
    else:
        return 'F'  # 5.00 (Drop)

@login_required
def student_grades(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student)
    
    subjects_data = []
    total_credits = 0
    weighted_gpa_sum = 0
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}  # Added 'F' for grades below 75

    for enrollment in enrollments:
        subject = enrollment.subject
        grades = Grade.objects.filter(enrollment=enrollment)
        
        # Calculate subject average
        if grades.exists():
            total_score = sum(grade.score for grade in grades)
            total_max = sum(grade.max_score for grade in grades)
            subject_average = (total_score / total_max * 100) if total_max > 0 else 0
        else:
            subject_average = 0

        # Update GPA calculation
        credits = subject.credits
        total_credits += credits
        gpa = calculate_gpa(subject_average)
        weighted_gpa_sum += gpa * credits

        # Update grade distribution
        letter_grade = get_letter_grade(subject_average)
        grade_distribution[letter_grade] += 1

        # Group grades by category
        grade_categories = []
        for category_type in Grade.GRADE_TYPES:
            category_grades = grades.filter(grade_type=category_type[0])
            if category_grades.exists():
                grade_categories.append({
                    'name': category_type[1],
                    'grades': category_grades
                })

        subjects_data.append({
            'subject': subject,
            'average': subject_average,
            'gpa': gpa,  # Add GPA to subject data
            'grade_categories': grade_categories
        })

    # Calculate overall GPA - lower is better in the new system
    overall_gpa = weighted_gpa_sum / total_credits if total_credits > 0 else 5.00  # Default to lowest GPA if no credits

    return render(request, 'main/student_grades.html', {
        'title': f'Grades for {student}',
        'student': student,
        'subjects': subjects_data,
        'overall_gpa': overall_gpa,
        'grade_distribution': grade_distribution
    })

@login_required
def student_dashboard(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.all()
    
    # Get all subjects the student is enrolled in
    subjects = Subject.objects.filter(enrollments__student=student).distinct()
    
    # Prepare the data structure for the template
    subjects_data = []
    for subject in subjects:
        # Get the enrollment for this student and subject
        enrollment = Enrollment.objects.get(student=student, subject=subject)
        
        # Get all grades for this enrollment
        grades = Grade.objects.filter(enrollment=enrollment)
        
        # Group grades by category
        categories = {}
        for grade in grades:
            if grade.grade_type not in categories:
                categories[grade.grade_type] = {
                    'name': grade.get_grade_type_display(),
                    'grades': []
                }
            categories[grade.grade_type]['grades'].append(grade)
        
        subjects_data.append({
            'subject': subject,
            'grade_categories': categories.values()
        })
    
    return render(request, 'main/student_dashboard.html', {
        'title': f'Dashboard - {student}',
        'student': student,
        'enrollments': enrollments,
        'subjects': subjects_data
    })

# Subject Views
@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'main/subject_list.html', {
        'title': 'Subjects',
        'subjects': subjects
    })

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    # Fetch enrollments and annotate with average score
    enrollments = Enrollment.objects.filter(subject=subject).annotate(
        average_grade=Avg('grades__score', default=0, output_field=FloatField()) * 100.0 / Avg('grades__max_score', default=1, output_field=FloatField())
    )

    # Handle division by zero for average_grade calculation
    for enrollment in enrollments:
      if Avg('grades__max_score', default=1, output_field=FloatField()) is not None and Avg('grades__max_score', default=1, output_field=FloatField()) != 0: # Check if max_score is not None or zero
        enrollment.average_grade = (Avg('grades__score', default=0, output_field=FloatField()) / Avg('grades__max_score', default=1, output_field=FloatField())) * 100.0
      else:
        enrollment.average_grade = 0 # Set to 0 if no grades or max_score is zero

    return render(request, 'main/subject_detail.html', {
        'title': f'Subject: {subject}',
        'subject': subject,
        'enrollments': enrollments
    })

@login_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('main:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'main/subject_form.html', {
        'title': 'Add Subject',
        'form': form
    })

@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('main:subject_detail', pk=pk)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'main/subject_form.html', {
        'title': f'Edit Subject: {subject}',
        'form': form
    })

@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('main:subject_list')
    return render(request, 'main/subject_confirm_delete.html', {
        'title': f'Delete Subject: {subject}',
        'subject': subject
    })

# Enrollment Views
@login_required
def enrollment_list(request):
    # Get all enrollments with related student and subject data
    enrollments = Enrollment.objects.all().select_related('student', 'subject').prefetch_related('grades')

    # Group enrollments by student and calculate overall GPA and percentage
    student_data_dict = {}
    for enrollment in enrollments:
        student = enrollment.student
        if student.pk not in student_data_dict:
            student_data_dict[student.pk] = {
                'student': student,
                'enrollments': [],
                'total_weighted_score': 0,
                'total_credits': 0,
            }
        student_data_dict[student.pk]['enrollments'].append(enrollment)

        # Calculate subject average for this enrollment
        grades = enrollment.grades.all()
        if grades.exists():
            total_score = sum(grade.score for grade in grades)
            total_max = sum(grade.max_score for grade in grades)
            enrollment.average_grade = (total_score / total_max * 100) if total_max > 0 else 0
        else:
            enrollment.average_grade = 0

        # Accumulate weighted scores and credits for overall calculation
        credits = enrollment.subject.credits if enrollment.subject.credits is not None else 0
        student_data_dict[student.pk]['total_weighted_score'] += enrollment.average_grade * credits
        student_data_dict[student.pk]['total_credits'] += credits

    # Prepare the final list of students with overall GPA and percentage
    students_with_gpa = []
    for student_pk, data in student_data_dict.items():
        overall_percentage = (data['total_weighted_score'] / data['total_credits']) if data['total_credits'] > 0 else 0
        overall_gpa = calculate_gpa(overall_percentage) # Assuming calculate_gpa is defined elsewhere

        students_with_gpa.append({
            'student': data['student'],
            'enrollments': data['enrollments'],
            'overall_gpa': overall_gpa,
            'overall_percentage': overall_percentage,
        })

    return render(request, 'main/enrollment_list.html', {
        'title': 'Enrollments',
        'student_enrollments': students_with_gpa, # Pass the processed data here
    })

@login_required
def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment created successfully!')
            return redirect('main:enrollment_list')
    else:
        form = EnrollmentForm()
    return render(request, 'main/enrollment_form.html', {
        'title': 'Add Enrollment',
        'form': form
    })

@login_required
def enrollment_update(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment updated successfully!')
            return redirect('main:enrollment_list')
    else:
        form = EnrollmentForm(instance=enrollment)
    return render(request, 'main/enrollment_form.html', {
        'title': f'Edit Enrollment: {enrollment}',
        'form': form
    })

@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully!')
        return redirect('main:enrollment_list')
    return render(request, 'main/enrollment_confirm_delete.html', {
        'title': f'Delete Enrollment: {enrollment}',
        'enrollment': enrollment
    })

@login_required
def grade_create(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            messages.success(request, 'Grade added successfully.')
            return redirect('main:student_grades', pk=student_id)
    else:
        # Filter enrollments to only show those for this student
        form = GradeForm()
        form.fields['enrollment'].queryset = Enrollment.objects.filter(student=student)
    
    return render(request, 'main/grade_form.html', {
        'form': form,
        'student': student,
        'title': 'Add Grade'
    })

@login_required
def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    student = grade.enrollment.student
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully.')
            return redirect('main:grade_management', pk=student.id)
    else:
        form = GradeForm(instance=grade)
        form.fields['enrollment'].queryset = Enrollment.objects.filter(student=student)
    
    return render(request, 'main/grade_form.html', {
        'form': form,
        'student': student,
        'title': f'Edit Grade: {grade.title}'
    })

@login_required
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    student = grade.enrollment.student
    
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully.')
        return redirect('main:student_grades', pk=student.id)
    
    return render(request, 'main/grade_confirm_delete.html', {
        'grade': grade,
        'student': student
    })

@login_required
def grade_management(request, pk):
    student = get_object_or_404(Student, pk=pk)
    grades = Grade.objects.filter(enrollment__student=student).select_related('enrollment__subject').order_by('-date_given')
    
    # Calculate GPA and grade distribution
    total_credits = 0
    weighted_gpa_sum = 0
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}  # Added F for grades below 75

    # Group grades by enrollment to calculate subject-level GPAs
    enrollment_grades = {}
    for grade in grades:
        enrollment = grade.enrollment
        if enrollment.id not in enrollment_grades:
            enrollment_grades[enrollment.id] = {
                'subject': enrollment.subject,
                'grades': [],
                'credits': enrollment.subject.credits
            }
        enrollment_grades[enrollment.id]['grades'].append(grade)

    # Calculate GPA for each subject
    for enrollment_data in enrollment_grades.values():
        total_score = sum(grade.score for grade in enrollment_data['grades'])
        total_max = sum(grade.max_score for grade in enrollment_data['grades'])
        subject_average = (total_score / total_max * 100) if total_max > 0 else 0
        
        credits = enrollment_data['credits']
        total_credits += credits
        gpa = calculate_gpa(subject_average)
        weighted_gpa_sum += gpa * credits

        # Update grade distribution
        letter_grade = get_letter_grade(subject_average)
        grade_distribution[letter_grade] += 1

    # Calculate overall GPA - lower is better in the new system
    overall_gpa = weighted_gpa_sum / total_credits if total_credits > 0 else 5.00  # Default to lowest GPA if no credits

    return render(request, 'main/grade_management.html', {
        'title': f'Grade Management - {student}',
        'student': student,
        'grades': grades,
        'overall_gpa': overall_gpa,
        'grade_distribution': grade_distribution
    })

# FacultyAdviser Views
@login_required
def faculty_adviser_list(request):
    advisers = FacultyAdviser.objects.all()
    return render(request, 'main/faculty_adviser_list.html', {
        'title': 'Faculty Advisers',
        'advisers': advisers
    })

@login_required
def faculty_adviser_detail(request, pk):
    adviser = get_object_or_404(FacultyAdviser, pk=pk)
    return render(request, 'main/faculty_adviser_detail.html', {
        'title': f'Adviser: {adviser.name}',
        'adviser': adviser
    })

@login_required
def faculty_adviser_create(request):
    if request.method == 'POST':
        form = FacultyAdviserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty adviser created successfully!')
            return redirect('main:faculty_adviser_list')
    else:
        form = FacultyAdviserForm()
    return render(request, 'main/faculty_adviser_form.html', {
        'title': 'Add Faculty Adviser',
        'form': form
    })

@login_required
def faculty_adviser_update(request, pk):
    adviser = get_object_or_404(FacultyAdviser, pk=pk)
    if request.method == 'POST':
        form = FacultyAdviserForm(request.POST, instance=adviser)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty adviser updated successfully!')
            return redirect('main:faculty_adviser_detail', pk=pk)
    else:
        form = FacultyAdviserForm(instance=adviser)
    return render(request, 'main/faculty_adviser_form.html', {
        'title': f'Edit Faculty Adviser: {adviser.name}',
        'form': form
    })

@login_required
def faculty_adviser_delete(request, pk):
    adviser = get_object_or_404(FacultyAdviser, pk=pk)
    if request.method == 'POST':
        adviser.delete()
        messages.success(request, 'Faculty adviser deleted successfully!')
        return redirect('main:faculty_adviser_list')
    return render(request, 'main/faculty_adviser_confirm_delete.html', {
        'title': f'Delete Faculty Adviser: {adviser.name}',
        'adviser': adviser
    })

# Department Views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'main/department_list.html', {
        'title': 'Departments',
        'departments': departments
    })

@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    # Fetch faculty advisers related to this department using the related_name 'faculty_advisers'
    faculty_advisers = department.faculty_advisers.all()
    return render(request, 'main/department_detail.html', {
        'title': f'Department: {department.name}',
        'department': department,
        'faculty_advisers': faculty_advisers # Pass faculty advisers instead of students
    })

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('main:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'main/department_form.html', {
        'title': 'Add Department',
        'form': form
    })

@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('main:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'main/department_form.html', {
        'title': f'Edit Department: {department.name}',
        'form': form
    })

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('main:department_list')
    return render(request, 'main/department_confirm_delete.html', {
        'title': f'Delete Department: {department.name}',
        'department': department
    })
