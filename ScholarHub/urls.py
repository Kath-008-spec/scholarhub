from django.urls import path

from . import auth_views, views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', auth_views.register_view, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('textbooks/', views.textbooks_view, name='textbooks'),
    path('past-questions/', views.past_questions_view, name='past_questions'),
    path('saved-books/', views.saved_books_view, name='saved_books'),
    path('admin/question-bank/', views.question_bank_admin_view, name='question_bank_admin'),
    path('quiz/<int:course_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:course_id>/', views.quiz_question_view, name='quiz_question'),
    path('quiz/<int:course_id>/save-answer/', views.save_quiz_answer, name='save_quiz_answer'),
    path('quiz/<int:course_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/review/<int:attempt_id>/', views.quiz_review, name='quiz_review'),
    path('quiz/history/', views.quiz_attempt_history, name='quiz_attempt_history'),
    path('api/departments/', views.departments_for_faculty, name='departments_for_faculty'),
    path('api/search/', views.search_api, name='search_api'),
    path('bookmark/textbook/<int:pk>/', views.bookmark_textbook, name='bookmark_textbook'),
    path('bookmark/past-question/<int:pk>/', views.bookmark_past_question, name='bookmark_past_question'),
    path('resources/textbooks/<int:pk>/', views.textbook_detail, name='textbook_detail'),
    path('resources/textbooks/<int:pk>/download/', views.download_textbook, name='download_textbook'),
    path('resources/past-questions/<int:pk>/', views.past_question_detail, name='past_question_detail'),
    path('resources/past-questions/<int:pk>/download/', views.download_past_question, name='download_past_question'),
]

