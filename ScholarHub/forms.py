import random

from django import forms
from django.contrib.auth.models import User
from .models import Course, Department, Faculty, LEVEL_CHOICES, SEMESTER_CHOICES, Question, StudentProfile, get_or_create_student_profile



class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email')
    matric_number = forms.CharField(max_length=50, required=False, label='Matric Number')
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), label='Faculty')
    department = forms.ModelChoiceField(queryset=Department.objects.none(), label='Department')
    level = forms.ChoiceField(choices=LEVEL_CHOICES, required=True, label='Current Level')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        faculty_id = self.data.get('faculty') or self.initial.get('faculty')
        if faculty_id:
            self.fields['department'].queryset = Department.objects.filter(faculty_id=faculty_id)
        else:
            self.fields['department'].queryset = Department.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The two password fields do not match.')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        profile = StudentProfile.objects.create(
            user=user,
            matric_number=self.cleaned_data.get('matric_number', ''),
            faculty=self.cleaned_data['faculty'],
            department=self.cleaned_data['department'],
            level=self.cleaned_data['level'],
        )
        return user, profile


class QuestionBankFilterForm(forms.Form):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), required=False, label='Faculty')
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False, label='Department')
    level = forms.ChoiceField(choices=[('', 'All Levels')] + LEVEL_CHOICES, required=False, label='Level')
    semester = forms.ChoiceField(choices=[('', 'All Semesters')] + SEMESTER_CHOICES, required=False, label='Semester')
    course = forms.ModelChoiceField(queryset=Course.objects.none(), required=False, label='Course')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        faculty_id = self.data.get('faculty') or self.initial.get('faculty')
        if faculty_id:
            self.fields['department'].queryset = Department.objects.filter(faculty_id=faculty_id)
        else:
            self.fields['department'].queryset = Department.objects.none()

        course_id = self.data.get('course') or self.initial.get('course')
        if course_id:
            self.fields['course'].queryset = Course.objects.filter(pk=course_id)
        else:
            self.fields['course'].queryset = Course.objects.none()


class QuestionForm(forms.ModelForm):
    quiz_time_limit = forms.IntegerField(required=False, min_value=0, label='Quiz Time Limit (minutes)')

    class Meta:
        model = Question
        fields = ['course', 'faculty', 'department', 'level', 'semester', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.select_related('department').order_by('department__name', 'code')
        self.fields['faculty'].queryset = Faculty.objects.order_by('name')
        self.fields['department'].queryset = Department.objects.order_by('name')

        initial_faculty = self.data.get('faculty') or self.initial.get('faculty')
        if initial_faculty:
            self.fields['department'].queryset = Department.objects.filter(faculty_id=initial_faculty)

        initial_course = self.data.get('course') or self.initial.get('course')
        if initial_course:
            self.fields['course'].queryset = Course.objects.filter(pk=initial_course)

        if self.instance and self.instance.pk and self.instance.course:
            self.fields['quiz_time_limit'].initial = self.instance.course.quiz_time_limit or 0
        else:
            course_id = self.data.get('course') or self.initial.get('course')
            if course_id:
                course = Course.objects.filter(pk=course_id).first()
                if course:
                    self.fields['quiz_time_limit'].initial = course.quiz_time_limit or 0

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        faculty = cleaned_data.get('faculty')
        department = cleaned_data.get('department')
        level = cleaned_data.get('level')
        semester = cleaned_data.get('semester')

        if course:
            if faculty and course.department.faculty_id != faculty.id:
                raise forms.ValidationError('The selected course does not belong to the selected faculty.')
            if department and course.department_id != department.id:
                raise forms.ValidationError('The selected course does not belong to the selected department.')
            if level and course.level != level:
                raise forms.ValidationError('The selected course does not match the selected level.')
            if semester and course.semester != semester:
                raise forms.ValidationError('The selected course does not match the selected semester.')
        return cleaned_data

    def save(self, commit=True):
        question = super().save(commit=False)
        if question.course:
            question.course.quiz_time_limit = self.cleaned_data.get('quiz_time_limit') or None
            question.course.save(update_fields=['quiz_time_limit'])
        if commit:
            question.save()
        return question


class ProfileUpdateForm(forms.Form):
    profile_picture = forms.ImageField(required=False, label='Profile Picture')
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number', widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))
    level = forms.ChoiceField(choices=LEVEL_CHOICES, required=True, label='Level')
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, required=True, label='Semester')
    elective_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.select_related('department').order_by('department__name', 'code'),
        required=False,
        label='Elective Courses',
        widget=forms.CheckboxSelectMultiple,
    )
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label='New Password')
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirm New Password')

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if self.profile:
            self.fields['level'].initial = self.profile.level
            self.fields['semester'].initial = self.profile.semester
            self.fields['phone_number'].initial = self.profile.phone_number
            self.fields['elective_courses'].initial = self.profile.elective_courses.all()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'The new passwords do not match.')
        return cleaned_data

    def save(self, user):
        profile = self.profile or get_or_create_student_profile(user)
        if self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data['profile_picture']
        profile.phone_number = self.cleaned_data.get('phone_number', '')
        profile.level = self.cleaned_data['level']
        profile.semester = self.cleaned_data['semester']
        profile.save()
        profile.elective_courses.set(self.cleaned_data.get('elective_courses', []))
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
            user.save()
        return profile
