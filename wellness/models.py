"""
Models for mental wellness survey and psychological indicators.
"""
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    """
    User location and preferences. Created/updated on login or signup when location is provided.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wellness_profile',
    )
    full_name = models.CharField(max_length=128, blank=True, help_text='Full name of the patient')
    phone_number = models.CharField(max_length=20, blank=True, help_text='Phone number')
    address = models.TextField(blank=True, help_text='Full address')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.city or 'No location'}"


class SurveyResponse(models.Model):
    """
    One completed survey submission. Stores aggregate scores and risk level.
    Linked to user when logged in so results are saved per user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='survey_responses',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Aggregate scores (0–3 scale per item, summed)
    mood_score = models.PositiveSmallIntegerField(default=0)   # depression/low mood
    anxiety_score = models.PositiveSmallIntegerField(default=0)
    sleep_score = models.PositiveSmallIntegerField(default=0)
    energy_score = models.PositiveSmallIntegerField(default=0)
    concentration_score = models.PositiveSmallIntegerField(default=0)
    hopelessness_score = models.PositiveSmallIntegerField(default=0)
    support_score = models.PositiveSmallIntegerField(default=0)  # reverse: higher = less support

    total_score = models.PositiveSmallIntegerField(default=0)
    risk_level = models.CharField(max_length=32, blank=True)  # minimal, mild, moderate, severe
    recommendation = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Survey {self.id} — {self.risk_level} ({self.created_at.date()})"


class Psychiatrist(models.Model):
    """
    Mental health professional for nearby consultation suggestions.
    """
    name = models.CharField(max_length=128)
    specialty = models.CharField(max_length=128, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PhysicalActivity(models.Model):
    """
    Outdoor physical activities suggested based on user's survey results.
    """
    INTENSITY_CHOICES = [
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('vigorous', 'Vigorous'),
    ]
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    intensity = models.CharField(max_length=16, choices=INTENSITY_CHOICES, default='moderate')
    duration_suggestion = models.CharField(max_length=64, blank=True)  # e.g. "20–30 min"
    duration_minutes = models.PositiveSmallIntegerField(default=30, help_text='Suggested duration in minutes (for timer)')
    outdoor = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    image_url = models.URLField(blank=True, help_text='Optional image URL for display')
    icon = models.CharField(max_length=32, blank=True, help_text='Emoji or icon, e.g. 🚶 🌳 🏃')

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Physical activities'

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Survey question for psychological indicators. Managed in Django admin;
    survey uses these when available, else falls back to code-defined items.
    """
    CATEGORY_CHOICES = [
        ('mood', 'Mood / Depression'),
        ('anxiety', 'Anxiety'),
        ('sleep', 'Sleep'),
        ('energy', 'Energy'),
        ('concentration', 'Concentration'),
        ('hopelessness', 'Hopelessness'),
        ('support', 'Social/Emotional Support'),
    ]
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    reverse = models.BooleanField(
        default=False,
        help_text='If True, higher raw score = better (e.g. support questions)',
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.get_category_display()}: {self.text[:50]}..."


class ThoughtEntry(models.Model):
    """
    User's written thoughts / journal entries. Stored in history for later reading.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thought_entries',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Thought entries'

    def __str__(self):
        return f"{self.user.username} — {self.created_at.date()}"


class DoctorProfile(models.Model):
    """
    Doctor/mental health professional who can view patients and provide suggestions.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
    )
    full_name = models.CharField(max_length=128)
    specialty = models.CharField(max_length=128, blank=True)
    license_number = models.CharField(max_length=64, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.full_name}"


class PatientDoctorAssignment(models.Model):
    """
    Admin-assigned link between a patient and a doctor. Only assigned patients
    appear in the doctor's dashboard. Admin can add, update, or delete assignments.
    """
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='assigned_patients',
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_doctors',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text='Optional admin notes about this assignment')

    class Meta:
        unique_together = ('doctor', 'patient')
        verbose_name = 'Patient-Doctor Assignment'
        verbose_name_plural = 'Patient-Doctor Assignments'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.patient.username} -> Dr. {self.doctor.full_name}"


class DoctorSuggestion(models.Model):
    """
    Doctor's suggestion/recommendation for a patient's recovery.
    """
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='suggestions',
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_suggestions',
    )
    suggestion = models.TextField()
    related_thought = models.ForeignKey(
        ThoughtEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_suggestions',
    )
    related_survey = models.ForeignKey(
        SurveyResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_suggestions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text='Patient has read this suggestion')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion for {self.patient.username} by Dr. {self.doctor.full_name}"


class PatientProfile(User):
    """
    Proxy model for patients (users without doctor profiles) to separate them in admin.
    """
    class Meta:
        proxy = True
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"Patient: {self.username}"


class UserActivityPreference(models.Model):
    """
    Store user-customized activity preferences, including preferred timer duration.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_preferences',
    )
    activity = models.ForeignKey(
        PhysicalActivity,
        on_delete=models.CASCADE,
        related_name='user_preferences',
    )
    preferred_duration_minutes = models.PositiveSmallIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'activity')
        verbose_name_plural = 'User activity preferences'

    def __str__(self):
        return f"{self.user.username} — {self.activity.name} ({self.preferred_duration_minutes}min)"


class MedicalResult(models.Model):
    """
    Medical test results, treatment plans, and medical details added by doctors for patients.
    """
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='medical_results',
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_results',
    )
    test_name = models.CharField(max_length=200, help_text='Name of the test or examination')
    result = models.TextField(help_text='Test results or findings')
    treatment_plan = models.TextField(blank=True, help_text='Recommended treatment or next steps')
    medical_notes = models.TextField(blank=True, help_text='Additional medical notes or observations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medical Result'
        verbose_name_plural = 'Medical Results'

    def __str__(self):
        return f"{self.patient.username} — {self.test_name} by Dr. {self.doctor.full_name}"
