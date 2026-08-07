#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from ScholarHub.models import PastQuestion

users = User.objects.all()
print('Total Users:', users.count())
for u in users:
    print(f'  - {u.username} ({u.email})')

pq_with_pdf = PastQuestion.objects.filter(pdf__isnull=False).exclude(pdf='')
print('\nPastQuestions with PDF:', pq_with_pdf.count())
if pq_with_pdf.exists():
    for pq in pq_with_pdf[:3]:
        print(f'  - ID: {pq.id}, Course: {pq.course.code}, PDF: {pq.pdf}')
else:
    print('  No past questions with PDFs found')
