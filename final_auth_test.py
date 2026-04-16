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
print("COMPREHENSIVE AUTHENTICATION TEST SUITE")
print("=" * 70)

# Clean up test users
User.objects.filter(username__startswith='final').delete()

client = Client()

tests_passed = 0
tests_failed = 0

def test(name, condition, error_msg=""):
    global tests_passed, tests_failed
    if condition:
        print(f"✓ {name}")
        tests_passed += 1
    else:
        print(f"✗ {name}" + (f" - {error_msg}" if error_msg else ""))
        tests_failed += 1

# TEST 1: User Signup
print("\n[TEST 1] User Signup")
print("-" * 70)

signup_data = {
    'username': 'finaluser',
    'password1': 'FinalPass123!',
    'password2': 'FinalPass123!',
}

response = client.post(reverse('wellness:signup'), signup_data, follow=True)
test("User signup returns 200 status", response.status_code == 200)

user_exists = User.objects.filter(username='finaluser').exists()
test("User was created in database", user_exists)

if user_exists:
    user = User.objects.get(username='finaluser')
    test("User password is set correctly", user.check_password('FinalPass123!'))

# TEST 2: User Login
print("\n[TEST 2] User Login")
print("-" * 70)

# Create a fresh client for login
login_client = Client()
login_data = {
    'username': 'finaluser',
    'password': 'FinalPass123!',
}

response = login_client.post(reverse('wellness:login'), login_data, follow=True)
test("User login returns 200 status", response.status_code == 200)
test("User is authenticated after login", response.wsgi_request.user.is_authenticated)
test("Authenticated user has correct username", response.wsgi_request.user.username == 'finaluser')

# TEST 3: Doctor Signup
print("\n[TEST 3] Doctor Signup")
print("-" * 70)

doctor_data = {
    'username': 'finaldoctor',
    'password1': 'FinalDocPass123!',
    'password2': 'FinalDocPass123!',
    'full_name': 'Dr. Final Test',
    'specialty': 'Psychiatry',
    'license_number': 'FINAL001',
}

response = client.post(reverse('wellness:doctor_signup'), doctor_data, follow=True)
test("Doctor signup returns 200 status", response.status_code == 200)

doctor_user_exists = User.objects.filter(username='finaldoctor').exists()
test("Doctor user was created in database", doctor_user_exists)

if doctor_user_exists:
    doctor_user = User.objects.get(username='finaldoctor')
    test("Doctor user password is set correctly", doctor_user.check_password('FinalDocPass123!'))
    
    from wellness.models import DoctorProfile
    doctor_profile_exists = DoctorProfile.objects.filter(user=doctor_user).exists()
    test("Doctor profile was created", doctor_profile_exists)
    
    if doctor_profile_exists:
        profile = DoctorProfile.objects.get(user=doctor_user)
        test("Doctor profile has correct full name", profile.full_name == 'Dr. Final Test')
        test("Doctor profile has correct specialty", profile.specialty == 'Psychiatry')
        test("Doctor profile has correct license number", profile.license_number == 'FINAL001')

# TEST 4: Doctor Login
print("\n[TEST 4] Doctor Login")
print("-" * 70)

doctor_login_client = Client()
doctor_login_data = {
    'username': 'finaldoctor',
    'password': 'FinalDocPass123!',
}

response = doctor_login_client.post(reverse('wellness:doctor_login'), doctor_login_data, follow=True)
test("Doctor login returns 200 status", response.status_code == 200)
test("Doctor is authenticated after login", response.wsgi_request.user.is_authenticated)
test("Authenticated doctor has correct username", response.wsgi_request.user.username == 'finaldoctor')

# TEST 5: Form Validation
print("\n[TEST 5] Form Validation")
print("-" * 70)

# Test password mismatch
invalid_signup = {
    'username': 'invaliduser',
    'password1': 'Password123!',
    'password2': 'DifferentPass123!',
}

response = client.post(reverse('wellness:signup'), invalid_signup, follow=False)
test("Password mismatch returns form (not redirect)", response.status_code == 200)

# Test duplicate username
duplicate_data = {
    'username': 'finaluser',  # Already exists
    'password1': 'NewPass123!',
    'password2': 'NewPass123!',
}

response = client.post(reverse('wellness:signup'), duplicate_data, follow=False)
test("Duplicate username is rejected", response.status_code == 200)

# TEST 6: Login with Wrong Credentials
print("\n[TEST 6] Login with Wrong Credentials")
print("-" * 70)

wrong_login = Client()
wrong_data = {
    'username': 'finaluser',
    'password': 'WrongPassword123!',
}

response = wrong_login.post(reverse('wellness:login'), wrong_data, follow=False)
test("Wrong password returns 200 (form reload)", response.status_code == 200)
test("User is not authenticated with wrong password", not response.wsgi_request.user.is_authenticated)

# SUMMARY
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests:  {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n✓ ALL TESTS PASSED - Authentication system is working correctly!")
else:
    print(f"\n✗ {tests_failed} TEST(S) FAILED - Review the failures above")

print("=" * 70)
