from django import forms
from .models import Student, Subject, Enrollment, Grade, FacultyAdviser, Department

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'student_id', 'email', 'date_of_birth', 'phone_number', 'major', 'is_active', 'faculty_adviser']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),

        }

class SubjectForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_name', 'instructor', 'credits', 'capacity', 'department']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'subject']
        widgets = {
            
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['enrollment', 'grade_type', 'title', 'score', 'max_score', 'date_given', 'remarks']
        widgets = {
            'enrollment': forms.Select(attrs={'class': 'form-select'}),
            'grade_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Quiz 1, Final Exam'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Enter score'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Enter maximum score'}),
            'date_given': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks about the grade'}),
        }

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
        if student_id:
            self.fields['enrollment'].queryset = Enrollment.objects.filter(student_id=student_id) 

class FacultyAdviserForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = FacultyAdviser
        fields = ['name', 'email', 'phone_number', 'office_location', 'department']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +1 123-456-7890'}),
            'office_location': forms.TextInput(attrs={'placeholder': 'e.g., Building A, Room 101'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Computer Science'}),
        }