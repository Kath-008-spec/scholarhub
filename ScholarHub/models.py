from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


LEVEL_CHOICES = [
    ('100', '100 Level'),
    ('200', '200 Level'),
    ('300', '300 Level'),
    ('400', '400 Level'),
    ('500', '500 Level'),
]

SEMESTER_CHOICES = [
    ('First Semester', 'First Semester'),
    ('Second Semester', 'Second Semester'),
]


class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        unique_together = ('faculty', 'name')

    def __str__(self):
        return self.name


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=30, choices=SEMESTER_CHOICES)
    units = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    quiz_time_limit = models.PositiveIntegerField(blank=True, null=True, help_text='Optional quiz timer in minutes.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        if self.code:
            return f'{self.code} - {self.title}'
        return self.title


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    matric_number = models.CharField(max_length=50, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='100')
    semester = models.CharField(max_length=30, choices=SEMESTER_CHOICES, default='First Semester')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    courses = models.ManyToManyField(Course, blank=True, related_name='students')
    elective_courses = models.ManyToManyField(Course, blank=True, related_name='elective_students')
    saved_textbooks = models.ManyToManyField('Textbook', blank=True, related_name='saved_by_students')
    saved_past_questions = models.ManyToManyField('PastQuestion', blank=True, related_name='saved_by_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('user__first_name',)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"


def get_or_create_student_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


class Textbook(models.Model):
    title = models.CharField(max_length=220)
    author = models.CharField(max_length=200, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='textbooks')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='textbooks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='textbooks')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=30, choices=SEMESTER_CHOICES)
    edition = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, help_text='Short summary shown on the cards.')
    content = models.TextField(blank=True, default='', help_text='Full note content typed from the admin panel.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class PastQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='past_questions')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='past_questions')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='past_questions')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=30, choices=SEMESTER_CHOICES)
    academic_session = models.CharField(max_length=20)
    pdf = models.FileField(upload_to='past_questions/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.course.code} {self.academic_session}'


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='questions')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='questions')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=30, choices=SEMESTER_CHOICES)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('course__code', 'text')

    def __str__(self):
        return f'{self.course.code} - {self.text[:60]}'

    def get_options(self):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }


class QuizAttempt(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='quiz_attempts')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    time_taken = models.PositiveIntegerField(default=0)
    time_limit = models.PositiveIntegerField(blank=True, null=True)
    auto_submitted = models.BooleanField(default=False)
    date_completed = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_completed',)

    def __str__(self):
        return f'{self.student.user.username} - {self.course.code}'


class StudentAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_answer = models.CharField(max_length=1, blank=True)
    correct_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('question__text',)

    def __str__(self):
        return f'{self.quiz_attempt} - {self.question_id}'


class Announcement(models.Model):
    title = models.CharField(max_length=220)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class LandingBackground(models.Model):
    image = models.ImageField(upload_to='landing_backgrounds/')
    caption = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order', '-created_at')

    def __str__(self):
        return self.caption or f'Background {self.pk}'


class LandingPanelImage(models.Model):
    image = models.ImageField(upload_to='landing_panels/')
    caption = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order', '-created_at')

    def __str__(self):
        return self.caption or f'Panel image {self.pk}'


