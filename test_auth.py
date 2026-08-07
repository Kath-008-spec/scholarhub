#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print('USERNAME_FIELD:', User.USERNAME_FIELD)
print()

user = User.objects.get(username='testuser')
print('Test user:')
print(f'  Username: {user.username}')
print(f'  Email: {user.email}')
print(f'  Password correct: {user.check_password("testpass123")}')
print()

# Test authentication
auth_user = authenticate(username='testuser', password='testpass123')
print(f'authenticate(username="testuser", password="testpass123"): {auth_user}')

# Try with email
auth_user2 = authenticate(username='testuser@example.com', password='testpass123')
print(f'authenticate(username="testuser@example.com", password="testpass123"): {auth_user2}')
