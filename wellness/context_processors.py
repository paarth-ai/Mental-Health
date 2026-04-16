"""Context processors for wellness app."""
from .models import DoctorProfile


def wellness_context(request):
    """Add is_doctor and doctor_profile to template context."""
    is_doctor = False
    doctor_profile = None
    if request.user.is_authenticated:
        try:
            doctor_profile = DoctorProfile.objects.get(user=request.user)
            is_doctor = True
        except DoctorProfile.DoesNotExist:
            pass
    return {'is_doctor': is_doctor, 'doctor_profile': doctor_profile}
