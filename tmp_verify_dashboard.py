import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_analyzer.settings')
django.setup()
from django.contrib.auth.models import User
from django.test import Client

username = 'test_company_user'
user, created = User.objects.get_or_create(username=username)
if created:
    user.set_password('TestPass123!')
    user.save()
    print('created user')
else:
    print('user exists')

profile = user.profile
profile.user_type = 'company'
profile.company_name = 'TestCorp'
profile.save()

client = Client()
client.force_login(user)
resp = client.get('/company/dashboard/')
print('status', resp.status_code)
if resp.status_code in (301, 302):
    print('redirect', resp.url)
elif resp.status_code == 200:
    print('page ok')
    print(resp.content.decode('utf-8')[:500])
else:
    print('unexpected status')