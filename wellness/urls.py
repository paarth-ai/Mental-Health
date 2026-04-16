from django.urls import path
from . import views

app_name = 'wellness'

urlpatterns = [
    path('', views.home, name='home'),
    path('survey/', views.survey, name='survey'),
    path('results/<int:response_id>/', views.results, name='results'),
    path('survey-history/', views.survey_history, name='survey_history'),
    path('thought-journal/', views.thought_journal, name='thought_journal'),
    path('thought-history/', views.thought_history, name='thought_history'),
    path('psychiatrists/', views.psychiatrists, name='psychiatrists'),
    path('activities/', views.activities, name='activities'),
    path('api/save-activity-preference/', views.save_activity_preference, name='save_activity_preference'),
    path('games/', views.games, name='games'),
    path('save-location/', views.save_location, name='save_location'),
    path('my-suggestions/', views.my_suggestions, name='my_suggestions'),
    path('auth/', views.auth_landing, name='auth'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('doctor-login/', views.DoctorLoginView.as_view(), name='doctor_login'),
    path('doctor-signup/', views.doctor_signup, name='doctor_signup'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patient/<int:user_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
]
