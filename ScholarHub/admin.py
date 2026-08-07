from django.contrib import admin

from .models import (
    Announcement,
    Course,
    Department,
    Faculty,
    LandingBackground,
    LandingPanelImage,
    PastQuestion,
    Question,
    QuizAttempt,
    StudentAnswer,
    StudentProfile,
    Textbook,
)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'level', 'semester', 'units')
    list_filter = ('department', 'level', 'semester')
    search_fields = ('code', 'title')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'matric_number', 'faculty', 'department', 'level')
    list_filter = ('faculty', 'department', 'level')
    search_fields = ('user__first_name', 'user__last_name', 'matric_number')


@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'course', 'faculty', 'department', 'level', 'semester', 'is_active')
    list_filter = ('faculty', 'department', 'level', 'semester', 'is_active')
    search_fields = ('title', 'author', 'course__code')
    fieldsets = (
        ('Basic details', {'fields': ('title', 'author', 'faculty', 'department', 'course', 'level', 'semester', 'edition', 'cover_image', 'description', 'content', 'is_active')}),
    )


@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'department', 'level', 'semester', 'academic_session')
    list_filter = ('faculty', 'department', 'level', 'semester')
    search_fields = ('course__code', 'academic_session')
    fieldsets = (
        ('Basic details', {'fields': ('course', 'faculty', 'department', 'level', 'semester', 'academic_session', 'description')}),
        ('PDF Upload', {'fields': ('pdf',), 'description': 'Upload the past question PDF file here.'}),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'department', 'level', 'semester', 'correct_answer', 'created_at')
    list_filter = ('faculty', 'department', 'level', 'semester', 'course')
    search_fields = ('text', 'course__code', 'course__title')


@admin.register(LandingBackground)
class LandingBackgroundAdmin(admin.ModelAdmin):
    list_display = ('caption', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('caption',)


@admin.register(LandingPanelImage)
class LandingPanelImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('caption',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'score', 'percentage', 'correct_answers', 'wrong_answers', 'date_completed', 'auto_submitted')
    list_filter = ('course', 'auto_submitted', 'date_completed')
    search_fields = ('student__user__username', 'course__code', 'course__title')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'selected_answer', 'correct_answer', 'is_correct')
    list_filter = ('is_correct', 'quiz_attempt__course')
    search_fields = ('question__text',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
