"""
Forms for the mental wellness survey.
Questions come from Django admin (Question model) when available, else default list.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm, AuthenticationForm as DjangoAuthenticationForm
from .indicators import get_survey_items
from .models import DoctorProfile

User = get_user_model()


CHOICES = [
    (0, 'Never'),
    (1, 'Rarely'),
    (2, 'Sometimes'),
    (3, 'Often'),
    (4, 'Always'),
]


class WellnessSurveyForm(forms.Form):
    """
    Dynamic form with one field per survey item (0–3 scale).
    Uses get_survey_items() so admin-managed questions are reflected.
    """
    def __init__(self, *args, **kwargs):
        self._items = kwargs.pop('items', None) or get_survey_items()
        super().__init__(*args, **kwargs)
        for i, item in enumerate(self._items):
            self.fields[f'q{i}'] = forms.TypedChoiceField(
                choices=CHOICES,
                coerce=int,
                label=item.text,
                widget=forms.RadioSelect(attrs={'class': 'survey-radio'}),
                required=True,
            )

    def get_items(self):
        return self._items

    def get_answers(self):
        """Return list of integer answers in order of survey items."""
        answers = []
        for i in range(len(self._items)):
            key = f'q{i}'
            answers.append(self.cleaned_data.get(key, 0))
        return answers


class UserCreationForm(DjangoUserCreationForm):
    """Custom UserCreationForm with CSS classes for styling."""
    full_name = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'class': 'auth-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'auth-input'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'auth-input', 'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all form fields
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ in ['PasswordInput', 'TextInput', 'Textarea']:
                field.widget.attrs.update({'class': 'auth-input'})
            field.help_text = ''

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data.get('full_name', '')
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.save()
        return user


class AuthenticationForm(DjangoAuthenticationForm):
    """Custom AuthenticationForm with CSS classes for styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all form fields
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ in ['PasswordInput', 'TextInput', 'Textarea']:
                field.widget.attrs.update({'class': 'auth-input'})


class DoctorSignupForm(forms.Form):
    """Doctor registration: User fields + DoctorProfile fields."""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'auth-input'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input'}), label='Confirm Password')
    full_name = forms.CharField(max_length=128, label='Full Name', widget=forms.TextInput(attrs={'class': 'auth-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'auth-input'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'auth-input', 'rows': 3}), required=False)
    specialty = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'class': 'auth-input'}))
    license_number = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'class': 'auth-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return p2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )
        # Create UserProfile for additional details
        from .models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.full_name = self.cleaned_data['full_name']
        user_profile.phone_number = self.cleaned_data.get('phone_number', '')
        user_profile.address = self.cleaned_data.get('address', '')
        user_profile.save()

        # Create DoctorProfile
        profile = DoctorProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            specialty=self.cleaned_data.get('specialty', '') or '',
            license_number=self.cleaned_data.get('license_number', '') or '',
        )
        return user

