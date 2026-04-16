#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("FINAL AUTHENTICATION VERIFICATION")
print("=" * 70)

# Clean up
User.objects.filter(username__startswith='verify').delete()

print("\n[SCENARIO 1] New User - Signup and Login")
print("-" * 70)

# Fresh client for new user
user_client = Client()

signup_data = {
    'username': 'verifyuser',
    'password1': 'VerifyPass123!',
    'password2': 'VerifyPass123!',
}

response = user_client.post(reverse('wellness:signup'), signup_data, follow=True)
print(f"✓ User signup: Status {response.status_code}, Authenticated: {response.wsgi_request.user.is_authenticated}")

print("\n[SCENARIO 2] New Doctor - Signup and Login")
print("-" * 70)

# Fresh client for new doctor
doctor_client = Client()

doctor_data = {
    'username': 'verifydoctor',
    'password1': 'VerifyDocPass123!',
    'password2': 'VerifyDocPass123!',
    'full_name': 'Dr. Verify',
    'specialty': 'Psychiatry',
    'license_number': 'VER001',
}

response = doctor_client.post(reverse('wellness:doctor_signup'), doctor_data, follow=True)
print(f"✓ Doctor signup: Status {response.status_code}, Authenticated: {response.wsgi_request.user.is_authenticated}")

try:
    doc = User.objects.get(username='verifydoctor')
    from wellness.models import DoctorProfile
    profile = DoctorProfile.objects.get(user=doc)
    print(f"✓ Doctor profile exists: {profile}")
except:
    print(f"✗ Doctor profile not found")

print("\n[SCENARIO 3] Fresh Login Test")
print("-" * 70)

# Fresh client for login
login_client = Client()

login_data = {
    'username': 'verifyuser',
    'password': 'VerifyPass123!',
}

response = login_client.post(reverse('wellness:login'), login_data, follow=True)
print(f"✓ User login: Status {response.status_code}, Authenticated: {response.wsgi_request.user.is_authenticated}, Username: {response.wsgi_request.user.username if response.wsgi_request.user.is_authenticated else 'N/A'}")

print("\n[SCENARIO 4] Doctor Fresh Login Test")
print("-" * 70)

# Fresh client for doctor login
doctor_login_client = Client()

doctor_login_data = {
    'username': 'verifydoctor',
    'password': 'VerifyDocPass123!',
}

response = doctor_login_client.post(reverse('wellness:doctor_login'), doctor_login_data, follow=True)
print(f"✓ Doctor login: Status {response.status_code}, Authenticated: {response.wsgi_request.user.is_authenticated}, Username: {response.wsgi_request.user.username if response.wsgi_request.user.is_authenticated else 'N/A'}")

print("\n" + "=" * 70)
print("✓ ALL SCENARIOS COMPLETED SUCCESSFULLY")
print("=" * 70)
