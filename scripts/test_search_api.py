import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory
from ScholarHub import views

factory = RequestFactory()
req = factory.get('/api/search/', {'q':'Mechanics'})
resp = views.search_api(req)
print(resp.content.decode())
