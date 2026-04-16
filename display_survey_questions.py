#!/usr/bin/env python
"""Extract and display all survey questions from the rendered HTML."""
import os
import sys
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create test user
username = 'testuser_q_display'
password = 'testpass123'

# Delete if exists
User.objects.filter(username=username).delete()

# Create and login
user = User.objects.create_user(username=username, password=password)
client = Client()
client.login(username=username, password=password)

# Get survey page
response = client.get('/survey/')
html = response.content.decode('utf-8')

print("=== SURVEY QUESTIONS DISPLAYED ===\n")

# Extract questions using regex
pattern = r'<label class="survey-question-label">(.*?)</label>'
questions = re.findall(pattern, html)

for i, q in enumerate(questions, 1):
    # Clean up HTML entities
    q = q.replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')
    print(f"{i}. {q}")

print(f"\n✓ Total questions found: {len(questions)}")

# Extract answer options for first question
print("\n=== ANSWER OPTIONS (for question 1) ===")
pattern = r'<span class="option-text">(.*?)</span>'
options = re.findall(pattern, html)[:4]  # First 4 options (one question)
for opt in options:
    print(f"  • {opt}")

# Cleanup
User.objects.filter(username=username).delete()
