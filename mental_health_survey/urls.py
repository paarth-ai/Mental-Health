"""
URL configuration for mental health survey project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Mental Wellness Admin'
admin.site.site_title = 'Mental Wellness Admin'
admin.site.index_title = 'Administrator Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wellness.urls')),
]
