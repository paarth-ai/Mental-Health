"""
Django Admin configuration for Wellness app.
Administrator has full add, update, delete access to all models.
Admin assigns patients to doctors via Patient-Doctor Assignments.
"""
from django.contrib import admin
from .models import (
    SurveyResponse, Question, UserProfile, Psychiatrist, PhysicalActivity,
    ThoughtEntry, UserActivityPreference, DoctorProfile, DoctorSuggestion,
    PatientDoctorAssignment, PatientProfile,
)

# ===== Inline Admin Classes =====

class PatientDoctorAssignmentInline(admin.TabularInline):
    """Inline for assigning patients to a doctor from DoctorProfile admin."""
    model = PatientDoctorAssignment
    can_delete = True
    extra = 1
    raw_id_fields = ('patient',)
    verbose_name = 'Assigned Patient'
    verbose_name_plural = 'Assigned Patients'


class DoctorSuggestionDoctorInline(admin.TabularInline):
    model = DoctorSuggestion
    can_delete = True
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('patient', 'suggestion', 'created_at', 'is_read')
    fk_name = 'doctor'
    raw_id_fields = ('patient',)
    max_num = 5


# ===== Model Admin Classes =====

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country', 'latitude', 'longitude', 'updated_at')
    list_filter = ('country',)
    search_fields = ('user__username', 'city', 'country')
    raw_id_fields = ('user',)
    readonly_fields = ('updated_at',)


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_score', 'risk_level', 'recommendation_short')
    list_filter = ('risk_level', 'created_at')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    list_editable = ('risk_level',)
    date_hierarchy = 'created_at'

    def recommendation_short(self, obj):
        return (obj.recommendation[:80] + '...') if len(obj.recommendation or '') > 80 else (obj.recommendation or '-')
    recommendation_short.short_description = 'Recommendation'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'text_short', 'order', 'reverse')
    list_filter = ('category',)
    list_editable = ('order', 'reverse')
    search_fields = ('text', 'category')
    ordering = ('order', 'id')

    def text_short(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_short.short_description = 'Text'


@admin.register(ThoughtEntry)
class ThoughtEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def content_short(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Content'


@admin.register(Psychiatrist)
class PsychiatristAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'address_display', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'specialty', 'address', 'phone', 'email')
    list_editable = ('is_active',)

    def address_display(self, obj):
        return (obj.address or '')[:40]
    address_display.short_description = 'Address'


@admin.register(PhysicalActivity)
class PhysicalActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'intensity', 'duration_suggestion', 'duration_minutes', 'outdoor', 'icon', 'order')
    list_filter = ('intensity', 'outdoor')
    list_editable = ('order', 'duration_minutes', 'outdoor')
    search_fields = ('name', 'description')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'specialty', 'license_number', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'full_name', 'specialty')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    list_editable = ('is_verified',)
    inlines = [PatientDoctorAssignmentInline, DoctorSuggestionDoctorInline]
    actions = ['verify_doctors', 'delete_selected_doctors']

    def verify_doctors(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} doctor(s) verified.')
    verify_doctors.short_description = 'Verify selected doctors'

    def delete_selected_doctors(self, request, queryset):
        """Delete selected doctors and all their related data."""
        count = queryset.count()
        for doctor_profile in queryset:
            user = doctor_profile.user
            # Delete all doctor-related data first
            doctor_profile.suggestions.all().delete()
            doctor_profile.assigned_patients.all().delete()
            # Delete user profile if exists
            if hasattr(user, 'wellness_profile'):
                user.wellness_profile.delete()
            # Delete the doctor profile
            doctor_profile.delete()
            # Finally delete the user
            user.delete()
        self.message_user(request, f'Successfully deleted {count} doctor(s) and all their related data.')
    delete_selected_doctors.short_description = 'Delete selected doctors and all related data'


@admin.register(PatientDoctorAssignment)
class PatientDoctorAssignmentAdmin(admin.ModelAdmin):
    """Admin assigns patients to doctors here. Doctors then see only their assigned patients."""
    list_display = ('doctor', 'patient', 'assigned_at', 'notes_short')
    list_filter = ('doctor', 'assigned_at')
    search_fields = ('doctor__full_name', 'doctor__user__username', 'patient__username')
    raw_id_fields = ('doctor', 'patient')
    readonly_fields = ('assigned_at',)
    date_hierarchy = 'assigned_at'
    ordering = ('-assigned_at',)

    def notes_short(self, obj):
        return (obj.notes[:40] + '...') if len(obj.notes or '') > 40 else (obj.notes or '-')
    notes_short.short_description = 'Notes'


@admin.register(DoctorSuggestion)
class DoctorSuggestionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'suggestion_short', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'doctor')
    search_fields = ('suggestion', 'patient__username', 'doctor__full_name')
    raw_id_fields = ('patient', 'doctor', 'related_thought', 'related_survey')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'

    def suggestion_short(self, obj):
        return (obj.suggestion[:60] + '...') if len(obj.suggestion) > 60 else obj.suggestion
    suggestion_short.short_description = 'Suggestion'


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin view for patients (users without doctor profiles)."""
    list_display = ('username', 'email', 'date_joined', 'is_active', 'survey_count', 'assigned_doctor')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    actions = ['delete_selected_users']

    def get_queryset(self, request):
        """Only show users who are not doctors."""
        qs = super().get_queryset(request)
        return qs.exclude(doctor_profile__isnull=False)

    def survey_count(self, obj):
        return obj.survey_responses.count()
    survey_count.short_description = 'Surveys Taken'

    def assigned_doctor(self, obj):
        assignment = obj.assigned_doctors.first()
        return assignment.doctor.full_name if assignment else 'None'
    assigned_doctor.short_description = 'Assigned Doctor'

    def delete_selected_users(self, request, queryset):
        """Delete selected users and all their related data."""
        count = queryset.count()
        for user in queryset:
            # Delete all related data first
            user.survey_responses.all().delete()
            user.thought_entries.all().delete()
            user.activity_preferences.all().delete()
            user.doctor_suggestions.all().delete()
            # Delete assignments where user is patient
            user.assigned_doctors.all().delete()
            # Delete user profile if exists
            if hasattr(user, 'wellness_profile'):
                user.wellness_profile.delete()
            # Finally delete the user
            user.delete()
        self.message_user(request, f'Successfully deleted {count} user(s) and all their related data.')
    delete_selected_users.short_description = 'Delete selected users and all related data'


@admin.register(UserActivityPreference)
class UserActivityPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'preferred_duration_minutes', 'created_at', 'updated_at')
    list_filter = ('activity', 'updated_at')
    search_fields = ('user__username', 'activity__name')
    raw_id_fields = ('user', 'activity')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('preferred_duration_minutes',)
