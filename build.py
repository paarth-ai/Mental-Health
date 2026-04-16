#!/usr/bin/env python
"""Build script for Vercel deployment - runs migrations and collects static files"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
django.setup()

# Run migrations
print("Running Django migrations...")
from django.core.management import call_command
try:
    call_command('migrate', verbosity=2)
    print("✓ Migrations completed successfully")
except Exception as e:
    print(f"⚠ Migration warning: {e}")
    # Continue even if migrations fail

# Create superuser if needed (for development)
if os.environ.get('VERCEL'):
    print("\nNote: Using SQLite on Vercel (ephemeral). For production, set up Vercel Postgres:")
    print("  1. Go to Vercel Dashboard > Storage")
    print("  2. Create PostgreSQL database")
    print("  3. Add DATABASE_URL to environment variables")

# Collect static files
print("\nCollecting static files...")
try:
    call_command('collectstatic', '--noinput', verbosity=2)
    print("✓ Static files collected successfully")
except Exception as e:
    print(f"⚠ Static files warning: {e}")

