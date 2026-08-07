#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ScholarHub.models import PastQuestion, StudentProfile, Course
from django.contrib.auth.models import User

# Get the first past question with a PDF
pq = PastQuestion.objects.filter(pdf__isnull=False).exclude(pdf='').first()
if pq:
    print(f'Past Question ID: {pq.id}')
    print(f'Course: {pq.course} (ID: {pq.course_id})')
    print(f'Faculty: {pq.faculty}')
    print(f'Department: {pq.department}')
    print(f'Level: {pq.level}')
    print()
    
    # Get or create test user
    user = User.objects.get(username='testuser')
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    
    # Update profile with matching faculty/department/level
    profile.faculty = pq.faculty
    profile.department = pq.department
    profile.level = pq.level
    profile.save()
    
    print(f'Updated test user profile:')
    print(f'  Faculty: {profile.faculty}')
    print(f'  Department: {profile.department}')
    print(f'  Level: {profile.level}')
    print()
    
    # Also add the course if the past question is associated with a course
    if pq.course:
        profile.courses.add(pq.course)
        print(f'Added course {pq.course.code} to test user profile')
