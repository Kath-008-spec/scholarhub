#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from ScholarHub.models import StudentProfile

# Create a test user with a known password
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
user.set_password('testpass123')
user.save()

# Create or get StudentProfile
profile, _ = StudentProfile.objects.get_or_create(user=user)

print('User created/updated:' if created else 'User already exists:')
print(f'  Username: {user.username}')
print(f'  Email: {user.email}')
print(f'  Password: testpass123')
