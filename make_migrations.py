#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

from django.core.management import call_command
call_command('makemigrations', 'wellness', verbosity=2)
