from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Announcement,
    Course,
    Department,
    Faculty,
    PastQuestion,
    Question,
    QuizAttempt,
    StudentAnswer,
    StudentProfile,
    Textbook,
)


class ScholarHubModelTests(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name='Faculty of Science')
        self.department = Department.objects.create(name='Physics', faculty=self.faculty)
        self.course = Course.objects.create(
            code='PHY201',
            title='Mechanics',
            department=self.department,
            level='200',
            semester='First Semester',
        )
        self.other_course = Course.objects.create(
            code='CSC201',
            title='Data Structures',
            department=Department.objects.create(name='Computer Science', faculty=self.faculty),
            level='200',
            semester='First Semester',
        )
        self.textbook = Textbook.objects.create(
            title='Mechanics Textbook',
            author='Jane Doe',
            course=self.course,
            faculty=self.faculty,
            department=self.department,
            level='200',
            semester='First Semester',
        )
        self.past_question = PastQuestion.objects.create(
            course=self.course,
            faculty=self.faculty,
            department=self.department,
            level='200',
            semester='First Semester',
            academic_session='2023/2024',
        )
        self.user = User.objects.create_user(username='student@example.com', email='student@example.com', password='secret123')
        self.profile = StudentProfile.objects.create(
            user=self.user,
            faculty=self.faculty,
            department=self.department,
            level='200',
        )
        self.profile.courses.add(self.course)
        self.profile.elective_courses.add(self.other_course)
        Announcement.objects.create(title='Welcome', content='Welcome to ScholarHub')

    def test_dashboard_resources_include_student_department_and_electives(self):
        visible_textbooks = Textbook.objects.filter(
            faculty=self.profile.faculty,
            department=self.profile.department,
            level=self.profile.level,
        ) | Textbook.objects.filter(course__in=self.profile.courses.all()) | Textbook.objects.filter(course__in=self.profile.elective_courses.all())
        visible_questions = PastQuestion.objects.filter(
            faculty=self.profile.faculty,
            department=self.profile.department,
            level=self.profile.level,
        ) | PastQuestion.objects.filter(course__in=self.profile.courses.all()) | PastQuestion.objects.filter(course__in=self.profile.elective_courses.all())

        self.assertIn(self.textbook, visible_textbooks)
        self.assertIn(self.past_question, visible_questions)


class QuizAttemptTests(TestCase):
    def test_quiz_submission_creates_attempt_and_answers(self):
        faculty = Faculty.objects.create(name='Faculty of Science')
        department = Department.objects.create(name='Physics', faculty=faculty)
        course = Course.objects.create(
            code='PHY301',
            title='Quantum Mechanics',
            department=department,
            level='300',
            semester='First Semester',
        )
        question = Question.objects.create(
            course=course,
            faculty=faculty,
            department=department,
            level='300',
            semester='First Semester',
            text='What is the SI unit of force?',
            option_a='Newton',
            option_b='Joule',
            option_c='Watt',
            option_d='Pascal',
            correct_answer='A',
            explanation='Newton is the SI unit of force.',
        )
        user = User.objects.create_user(username='quizstudent@example.com', email='quizstudent@example.com', password='secret123')
        profile = StudentProfile.objects.create(user=user, faculty=faculty, department=department, level='300')
        profile.courses.add(course)

        self.client.force_login(user)
        response = self.client.get(reverse('start_quiz', args=[course.pk]))
        self.assertEqual(response.status_code, 200)

        submit_response = self.client.post(
            reverse('submit_quiz', args=[course.pk]),
            {'question_{}'.format(question.pk): 'A'}
        )

        self.assertEqual(submit_response.status_code, 200)
        self.assertTrue(QuizAttempt.objects.filter(student=profile, course=course).exists())
        attempt = QuizAttempt.objects.get(student=profile, course=course)
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.percentage, 100.0)
        self.assertTrue(StudentAnswer.objects.filter(quiz_attempt=attempt, question=question).exists())


class ProfileFallbackTests(TestCase):
    def test_dashboard_creates_missing_profile_for_authenticated_user(self):
        user = User.objects.create_user(username='newstudent@example.com', email='newstudent@example.com', password='secret123')

        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())

    def test_profile_page_loads_for_authenticated_user(self):
        user = User.objects.create_user(username='student@example.com', email='student@example.com', password='secret123')
        StudentProfile.objects.create(user=user)

        self.client.force_login(user)
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit your profile')

    def test_profile_semester_field_exists(self):
        user = User.objects.create_user(username='student@example.com', email='student@example.com', password='secret123')
        profile = StudentProfile.objects.create(user=user, semester='First Semester')

        self.assertEqual(profile.semester, 'First Semester')
        profile.semester = 'Second Semester'
        profile.save()
        
        updated_profile = StudentProfile.objects.get(user=user)
        self.assertEqual(updated_profile.semester, 'Second Semester')

    def test_profile_form_includes_semester_field(self):
        from .forms import ProfileUpdateForm
        from .models import Faculty, Department

        user = User.objects.create_user(username='student@example.com', email='student@example.com', password='secret123')
        faculty = Faculty.objects.create(name='Faculty of Science')
        department = Department.objects.create(name='Physics', faculty=faculty)
        profile = StudentProfile.objects.create(user=user, faculty=faculty, department=department)

        form = ProfileUpdateForm(profile=profile)
        
        self.assertIn('semester', form.fields)
        self.assertEqual(form.fields['semester'].initial, 'First Semester')
