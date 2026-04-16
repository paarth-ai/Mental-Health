#!/usr/bin/env python
"""
Seed default survey questions into the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

from wellness.models import Question
from wellness.indicators import DEFAULT_SURVEY_ITEMS

# Clear existing questions
Question.objects.all().delete()

# Seed default questions
for order, item in enumerate(DEFAULT_SURVEY_ITEMS, start=1):
    Question.objects.create(
        category=item.category,
        text=item.text,
        reverse=item.reverse,
        order=order
    )

print(f"✓ Created {Question.objects.count()} questions:")
for q in Question.objects.all():
    print(f"  {q.id}. [{q.get_category_display()}] {q.text}")
