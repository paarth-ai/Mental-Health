"""
Views for mental wellness survey: home, take survey, results, login, logout, signup.
"""
import math
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import WellnessSurveyForm, UserCreationForm, AuthenticationForm
from .models import (
    SurveyResponse, UserProfile, Psychiatrist, PhysicalActivity, ThoughtEntry,
    UserActivityPreference, DoctorProfile, DoctorSuggestion, PatientDoctorAssignment, MedicalResult,
)
from .indicators import get_survey_items, get_category_indices, compute_total_and_risk


def _haversine_km(lat1, lon1, lat2, lon2):
    """Return distance in km between two (lat, lon) points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


class CustomLoginView(LoginView):
    template_name = 'wellness/login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign In'
        return context

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if _is_doctor(form.get_user()):
            return redirect('wellness:doctor_dashboard')
        lat = self.request.POST.get('lat')
        lng = self.request.POST.get('lng')
        city = (self.request.POST.get('city_name') or '').strip()
        if lat and lng:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=form.get_user())
                profile.latitude = Decimal(lat)
                profile.longitude = Decimal(lng)
                if city:
                    profile.city = city[:128]
                profile.save()
            except (ValueError, TypeError):
                pass
        return redirect(self.get_success_url())


class CustomLogoutView(LogoutView):
    """Log out and always redirect to home. Allows GET requests for better UX."""
    next_page = 'wellness:home'

    def get_next_page(self):
        return reverse('wellness:home')

    def get(self, request, *args, **kwargs):
        """Allow GET requests for logout to prevent 405 errors."""
        return self.post(request, *args, **kwargs)


def signup(request):
    """User registration (sign up). Optionally save location from hidden fields."""
    if request.user.is_authenticated:
        return redirect('wellness:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            lat = request.POST.get('lat')
            lng = request.POST.get('lng')
            city = (request.POST.get('city_name') or '').strip()
            if lat and lng:
                try:
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.latitude = Decimal(lat)
                    profile.longitude = Decimal(lng)
                    if city:
                        profile.city = city[:128]
                    profile.save()
                except (ValueError, TypeError):
                    pass
            return redirect('wellness:home')
    else:
        form = UserCreationForm()
    return render(request, 'wellness/signup.html', {
        'form': form,
        'title': 'Sign Up',
    })


def auth_landing(request):
    """Combined landing page with role selection: User or Doctor."""
    if request.user.is_authenticated:
        if _is_doctor(request.user):
            return redirect('wellness:doctor_dashboard')
        return redirect('wellness:home')
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()
    return render(request, 'wellness/auth_landing.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'title': 'Welcome',
    })


def _is_doctor(user):
    """Check if the user has a doctor profile."""
    return hasattr(user, 'doctor_profile') and DoctorProfile.objects.filter(user=user).exists()


def doctor_signup(request):
    """Doctor registration - creates User + DoctorProfile."""
    if request.user.is_authenticated:
        return redirect('wellness:doctor_dashboard')
    if request.method == 'POST':
        from .forms import DoctorSignupForm
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('wellness:doctor_dashboard')
    else:
        from .forms import DoctorSignupForm
        form = DoctorSignupForm()
    return render(request, 'wellness/doctor_signup.html', {'form': form, 'title': 'Doctor Sign Up'})


class DoctorLoginView(LoginView):
    template_name = 'wellness/doctor_login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Doctor Sign In'
        return context

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        # Refresh user to ensure doctor_profile relationship is available
        user.refresh_from_db()
        if not _is_doctor(user):
            from django.contrib.auth import logout
            logout(self.request)
            messages.error(self.request, 'This account is not registered as a doctor.')
            return redirect('wellness:doctor_login')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('wellness:doctor_dashboard')


@login_required
def doctor_dashboard(request):
    """Doctor dashboard: list of patients assigned by admin to this doctor."""
    if not _is_doctor(request.user):
        return redirect('wellness:home')
    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return redirect('wellness:home')
    # Only show patients assigned to this doctor by admin
    assigned = PatientDoctorAssignment.objects.filter(doctor=doctor_profile).select_related('patient')
    patients = [a.patient for a in assigned]
    patients_data = []
    for p in patients:
        latest_survey = SurveyResponse.objects.filter(user=p).order_by('-created_at').first()
        thought_count = ThoughtEntry.objects.filter(user=p).count()
        suggestion_count = DoctorSuggestion.objects.filter(patient=p).count()
        patients_data.append({
            'user': p,
            'latest_survey': latest_survey,
            'thought_count': thought_count,
            'suggestion_count': suggestion_count,
        })
    # Sort by username
    patients_data.sort(key=lambda x: x['user'].username)
    return render(request, 'wellness/doctor_dashboard.html', {
        'title': 'Doctor Dashboard',
        'patients_data': patients_data,
    })


@login_required
def doctor_patient_detail(request, user_id):
    """Doctor views patient details: surveys, thoughts, and can add suggestions."""
    if not _is_doctor(request.user):
        return redirect('wellness:home')
    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return redirect('wellness:home')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        patient = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('wellness:doctor_dashboard')
    if DoctorProfile.objects.filter(user=patient).exists():
        return redirect('wellness:doctor_dashboard')
    # Ensure this patient is assigned to this doctor by admin
    if not PatientDoctorAssignment.objects.filter(doctor=doctor_profile, patient=patient).exists():
        messages.error(request, 'You do not have access to this patient. Ask the administrator to assign them to you.')
        return redirect('wellness:doctor_dashboard')
    surveys = SurveyResponse.objects.filter(user=patient).order_by('-created_at')[:20]
    thoughts = ThoughtEntry.objects.filter(user=patient).order_by('-created_at')[:50]
    suggestions = DoctorSuggestion.objects.filter(patient=patient).order_by('-created_at')
    medical_results = MedicalResult.objects.filter(patient=patient).order_by('-created_at')
    profile = getattr(patient, 'wellness_profile', None)
    if request.method == 'POST':
        # Handle medical result submission
        test_name = (request.POST.get('test_name') or '').strip()
        result = (request.POST.get('result') or '').strip()
        treatment_plan = (request.POST.get('treatment_plan') or '').strip()
        medical_notes = (request.POST.get('medical_notes') or '').strip()

        if test_name and result:
            MedicalResult.objects.create(
                doctor=doctor_profile,
                patient=patient,
                test_name=test_name,
                result=result,
                treatment_plan=treatment_plan,
                medical_notes=medical_notes,
            )
            messages.success(request, 'Medical result added successfully.')
            return redirect('wellness:doctor_patient_detail', user_id=user_id)

        # Handle suggestion submission
        suggestion_text = (request.POST.get('suggestion') or '').strip()
        if suggestion_text:
            DoctorSuggestion.objects.create(
                doctor=doctor_profile,
                patient=patient,
                suggestion=suggestion_text,
            )
            messages.success(request, 'Suggestion added successfully.')
            return redirect('wellness:doctor_patient_detail', user_id=user_id)
    return render(request, 'wellness/doctor_patient_detail.html', {
        'title': f'Patient: {patient.username}',
        'patient': patient,
        'surveys': surveys,
        'thoughts': thoughts,
        'suggestions': suggestions,
        'medical_results': medical_results,
        'patient_profile': profile,
    })


@login_required
def my_suggestions(request):
    """Patient view: see doctor's suggestions for their treatment."""
    if _is_doctor(request.user):
        return redirect('wellness:doctor_dashboard')
    suggestions = DoctorSuggestion.objects.filter(patient=request.user).order_by('-created_at')
    DoctorSuggestion.objects.filter(patient=request.user).update(is_read=True)
    return render(request, 'wellness/my_suggestions.html', {
        'title': "Doctor's Suggestions",
        'suggestions': suggestions,
    })


@login_required
@require_POST
def save_location(request):
    """Save or update user location (called from home page or after login)."""
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    city = (request.POST.get('city_name') or '').strip()
    if not lat or not lng:
        return JsonResponse({'ok': False, 'error': 'Missing lat/lng'})
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.latitude = Decimal(lat)
        profile.longitude = Decimal(lng)
        if city:
            profile.city = city[:128]
        profile.save()
        return JsonResponse({'ok': True})
    except (ValueError, TypeError) as e:
        return JsonResponse({'ok': False, 'error': str(e)})


def home(request):
    """Home page - personalized dashboard for authenticated users, redirect others to auth."""
    if not request.user.is_authenticated:
        return redirect('wellness:auth')
    if _is_doctor(request.user):
        return redirect('wellness:doctor_dashboard')
    
    # Get user's latest survey and activity preferences
    latest_survey = SurveyResponse.objects.filter(user=request.user).order_by('-created_at').first()
    
    # Get indoor activities for the home page
    indoor_activities = list(PhysicalActivity.objects.filter(outdoor=False))[:6]
    
    user_prefs = {
        p.activity_id: p.preferred_duration_minutes
        for p in UserActivityPreference.objects.filter(user=request.user)
    }
    
    for a in indoor_activities:
        a.timer_duration = user_prefs.get(a.id, a.duration_minutes)
    
    return render(request, 'wellness/home_authenticated.html', {
        'title': 'Home',
        'username': request.user.username,
        'latest_survey': latest_survey,
        'indoor_activities': indoor_activities,
    })


@login_required
def games(request):
    """Mental health games and activities to refresh the mind."""
    return render(request, 'wellness/games.html', {
        'title': 'Mental Health Games',
    })


@login_required
def survey(request):
    """Display survey form and handle submission. Questions from admin when available."""
    if _is_doctor(request.user):
        return redirect('wellness:doctor_dashboard')
    items = get_survey_items()
    if request.method == 'POST':
        form = WellnessSurveyForm(request.POST, items=items)
        if form.is_valid():
            answers = form.get_answers()
            total, risk_level, recommendation, category_scores = compute_total_and_risk(answers, form.get_items())
            response_obj = SurveyResponse(
                user=request.user,
                total_score=total,
                risk_level=risk_level,
                recommendation=recommendation,
                mood_score=category_scores['mood_score'],
                anxiety_score=category_scores['anxiety_score'],
                sleep_score=category_scores['sleep_score'],
                energy_score=category_scores['energy_score'],
                concentration_score=category_scores['concentration_score'],
                hopelessness_score=category_scores['hopelessness_score'],
                support_score=category_scores['support_score'],
            )
            response_obj.save()
            request.session['latest_survey_id'] = response_obj.id
            return redirect('wellness:results', response_id=response_obj.id)
    else:
        form = WellnessSurveyForm(items=items)

    return render(request, 'wellness/survey.html', {
        'form': form,
        'items': items,
        'title': 'Wellness Survey',
    })


@login_required
def survey_history(request):
    """List current user's past survey results."""
    responses = SurveyResponse.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'wellness/survey_history.html', {
        'responses': responses,
        'title': 'My Survey History',
    })


@login_required
def psychiatrists(request):
    """List psychiatrists, ordered by distance from user location if available. Support location search."""
    profile = getattr(request.user, 'wellness_profile', None)
    search_query = (request.GET.get('search') or '').strip()
    
    # Start with all active psychiatrists
    psychiatrists_list = list(Psychiatrist.objects.filter(is_active=True))
    
    # Filter by search query if provided
    if search_query:
        search_lower = search_query.lower()
        psychiatrists_list = [
            p for p in psychiatrists_list
            if search_lower in (p.name or '').lower() or 
               search_lower in (p.address or '').lower() or
               search_lower in (p.specialty or '').lower() or
               search_lower in (p.phone or '').lower() or
               search_lower in (p.email or '').lower()
        ]
    
    # Calculate distances if user has location
    if profile and profile.latitude is not None and profile.longitude is not None:
        user_lat = float(profile.latitude)
        user_lon = float(profile.longitude)
        for p in psychiatrists_list:
            if p.latitude is not None and p.longitude is not None:
                p.distance_km = round(_haversine_km(user_lat, user_lon, float(p.latitude), float(p.longitude)), 1)
            else:
                p.distance_km = None
        psychiatrists_list.sort(key=lambda x: (x.distance_km if x.distance_km is not None else 9999, x.name))
    else:
        for p in psychiatrists_list:
            p.distance_km = None
    
    return render(request, 'wellness/psychiatrists.html', {
        'psychiatrists': psychiatrists_list,
        'has_location': profile and profile.latitude is not None,
        'search_query': search_query,
        'title': 'Nearby Psychiatrists',
    })


@login_required
def thought_journal(request):
    """Write and save a thought entry. Stored in history for later reading."""
    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if content:
            ThoughtEntry.objects.create(user=request.user, content=content)
            return redirect('wellness:thought_history')
    return render(request, 'wellness/thought_journal.html', {
        'title': 'Write Your Thoughts',
    })


@login_required
def thought_history(request):
    """List user's saved thought entries. Can read them later."""
    entries = ThoughtEntry.objects.filter(user=request.user).order_by('-created_at')[:100]
    return render(request, 'wellness/thought_history.html', {
        'entries': entries,
        'title': 'My Thought History',
    })


def activities(request):
    """Outdoor physical activities with suggestions based on latest survey result."""
    activities_list = list(PhysicalActivity.objects.filter(outdoor=True))
    latest = SurveyResponse.objects.filter(user=request.user).order_by('-created_at').first()
    suggested_ids = set()
    
    # Get user preferences if logged in
    user_prefs = {}
    if request.user.is_authenticated:
        user_prefs = {
            p.activity_id: p.preferred_duration_minutes
            for p in UserActivityPreference.objects.filter(user=request.user)
        }
    
    if latest:
        # Suggest by energy: low energy -> light; moderate -> light + moderate; high -> moderate + vigorous
        energy_score = latest.energy_score
        max_energy = 6  # 2 items * 3
        if energy_score <= 2:
            suggested_ids = {a.id for a in activities_list if a.intensity == 'light'}
        elif energy_score <= 4:
            suggested_ids = {a.id for a in activities_list if a.intensity in ('light', 'moderate')}
        else:
            suggested_ids = {a.id for a in activities_list if a.intensity in ('moderate', 'vigorous')}
        if not suggested_ids:
            suggested_ids = {a.id for a in activities_list}
    
    for a in activities_list:
        a.suggested = a.id in suggested_ids
        # Use user preference if exists, otherwise use default
        a.timer_duration = user_prefs.get(a.id, a.duration_minutes)
    
    return render(request, 'wellness/activities.html', {
        'activities': activities_list,
        'has_survey': latest is not None,
        'title': 'Outdoor Physical Activities',
    })


@login_required
def results(request, response_id):
    """Show results and recommendation for a completed survey. Login required."""
    try:
        response_obj = SurveyResponse.objects.get(pk=response_id)
    except SurveyResponse.DoesNotExist:
        return redirect('wellness:home')
    if response_obj.user_id and response_obj.user_id != request.user.id:
        return redirect('wellness:home')

    risk_labels = {
        'minimal': 'Minimal',
        'mild': 'Mild',
        'moderate': 'Moderate',
        'moderately_severe': 'Moderately Severe',
        'severe': 'Severe',
    }
    risk_label = risk_labels.get(response_obj.risk_level, response_obj.risk_level)

    # Numeric ranges used by compute_total_and_risk (kept in sync with indicators)
    items = get_survey_items()
    max_possible = 4 * len(items)
    risk_ranges = {
        'minimal': (0, int(max_possible * 0.12)),
        'mild': (int(max_possible * 0.12) + 1, int(max_possible * 0.26)),
        'moderate': (int(max_possible * 0.26) + 1, int(max_possible * 0.40)),
        'moderately_severe': (int(max_possible * 0.40) + 1, int(max_possible * 0.55)),
        'severe': (int(max_possible * 0.55) + 1, max_possible),
    }

    risk_descriptions = {
        'minimal': 'Minimal signs of distress — continue regular self-care and monitoring.',
        'mild': 'Mild difficulty — consider self-care, rest, and talking to someone you trust.',
        'moderate': 'Moderate distress — consider speaking with a doctor, counselor, or mental health professional.',
        'moderately_severe': 'Significant distress — reaching out to a mental health professional is recommended.',
        'severe': 'Severe distress — please seek professional support promptly; if in crisis, contact emergency services or a crisis line.',
    }

    range_min, range_max = risk_ranges.get(response_obj.risk_level, (None, None))
    score_range_text = f"{range_min}–{range_max}" if range_min is not None else ''
    score_description = risk_descriptions.get(response_obj.risk_level, '')

    # Per-category maximums (from current survey questions so admin changes are reflected)
    category_indices = get_category_indices(items)
    categories = ['mood', 'anxiety', 'sleep', 'energy', 'concentration', 'hopelessness', 'support']
    category_maxes = {cat: 4 * len(category_indices.get(cat, [])) for cat in categories}
    category_percents = {}
    for cat in categories:
        score_val = getattr(response_obj, f"{cat}_score", 0)
        max_val = category_maxes.get(cat) or 0
        pct = round((score_val / max_val) * 100) if max_val else 0
        category_percents[cat] = pct

    return render(request, 'wellness/results.html', {
        'response': response_obj,
        'risk_label': risk_label,
        'score_range': score_range_text,
        'score_description': score_description,
        'category_maxes': category_maxes,
        'category_percents': category_percents,
        'title': 'Your Results',
    })

@login_required
@require_POST
def save_activity_preference(request):
    """Save user's preferred duration for an activity."""
    import json
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        duration_minutes = data.get('duration_minutes')
        
        if not activity_id or not duration_minutes:
            return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)
        
        # Validate duration is a positive integer
        try:
            duration_minutes = int(duration_minutes)
            if duration_minutes <= 0 or duration_minutes > 300:  # Max 5 hours
                return JsonResponse({'success': False, 'error': 'Duration must be between 1-300 minutes'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid duration'}, status=400)
        
        # Check activity exists
        try:
            activity = PhysicalActivity.objects.get(id=activity_id)
        except PhysicalActivity.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Activity not found'}, status=404)
        
        # Save or update preference
        pref, created = UserActivityPreference.objects.update_or_create(
            user=request.user,
            activity=activity,
            defaults={'preferred_duration_minutes': duration_minutes}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Preference saved for {activity.name}',
            'duration': pref.preferred_duration_minutes
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)