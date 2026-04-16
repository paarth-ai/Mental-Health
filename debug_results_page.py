#!/usr/bin/env python
"""Check what's actually in the results page HTML."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from wellness.models import SurveyResponse

User = get_user_model()

# Create test user
username = 'test_results_debug'
password = 'pass123'
User.objects.filter(username=username).delete()
user = User.objects.create_user(username=username, password=password)
client = Client()
client.login(username=username, password=password)

# Submit survey
survey_data = {
    'q0': '0', 'q1': '1', 'q2': '2', 'q3': '3',
    'q4': '0', 'q5': '1', 'q6': '2', 'q7': '3',
    'q8': '0', 'q9': '1', 'q10': '2', 'q11': '3',
}
response = client.post('/survey/', survey_data)

# Get the survey response
survey_response = SurveyResponse.objects.filter(user=user).latest('created_at')

# Get results page
results_url = f'/results/{survey_response.id}/'
response = client.get(results_url)
html = response.content.decode('utf-8')

print("=== RESULTS PAGE HTML ANALYSIS ===\n")

# Check for key elements
print("Score elements:")
print(f"  'Total score': {'✓' if 'Total score' in html else '✗'}")
print(f"  '{{ response.total_score }}': {'✓' if '{{ response.total_score }}' in html else '✗'}")
print(f"  Actual score in HTML: {'✓' if f'{survey_response.total_score}' in html else '✗'}")
print(f"  Risk label in HTML: {'✓' if 'Moderately Severe' in html else '✗'}")

print("\nCategory scores:")
print(f"  'By area': {'✓' if 'By area' in html else '✗'}")
print(f"  'Mood:': {'✓' if 'Mood:' in html else '✗'}")
print(f"  'Anxiety:': {'✓' if 'Anxiety:' in html else '✗'}")

print("\nCharts:")
print(f"  'radarChart': {'✓' if 'radarChart' in html else '✗'}")
print(f"  'barChart': {'✓' if 'barChart' in html else '✗'}")
print(f"  'Chart.js': {'✓' if 'Chart.js' in html else '✗'}")

# Check for template variables not being rendered
print("\nTemplate variable checks:")
print(f"  Contains '{{': {'✓ (unrendered template)' if '{{' in html else '✗ (all rendered)'}")

# Extract snippet around score
if '<span class="score-value">' in html:
    start = html.find('<span class="score-value">')
    end = html.find('</span>', start) + 7
    snippet = html[start:end]
    print(f"\nScore snippet: {snippet}")

# Cleanup
User.objects.filter(username=username).delete()
