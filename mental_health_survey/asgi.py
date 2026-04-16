"""
ASGI config for mental health survey project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_survey.settings')
application = get_asgi_application()
