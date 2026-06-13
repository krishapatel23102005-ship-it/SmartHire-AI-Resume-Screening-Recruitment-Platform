from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Job

class StudentSignUpForm(UserCreationForm):
    """
    Form to handle Student user signups.
    """
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # The signal automatically creates the Profile, so we just set user_type
            user.profile.user_type = 'student'
            user.profile.save()
        return user


class CompanySignUpForm(UserCreationForm):
    """
    Form to handle Company user signups.
    """
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True, label="Company Name")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.user_type = 'company'
            user.profile.company_name = self.cleaned_data['company_name']
            user.profile.save()
        return user


class JobForm(forms.ModelForm):
    """
    Form for posting and editing jobs. Converts comma-separated skill keywords into a JSON list.
    """
    required_skills_raw = forms.CharField(
        max_length=500, 
        required=True, 
        label="Required Skills (Comma separated)",
        help_text="e.g. Python, Django, SQL, REST API",
        widget=forms.TextInput(attrs={'placeholder': 'Python, Django, SQL'})
    )

    class Meta:
        model = Job
        fields = ['title', 'description', 'min_score', 'experience_required']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the job role and responsibilities...'}),
            'min_score': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'experience_required': forms.TextInput(attrs={'placeholder': 'e.g. 1-3 years'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing job, pre-populate the raw skills input with comma-joined tags
        if self.instance and self.instance.pk:
            self.fields['required_skills_raw'].initial = ", ".join(self.instance.required_skills)

    def clean_required_skills_raw(self):
        raw_skills = self.cleaned_data['required_skills_raw']
        # Split by comma, trim whitespace, and discard empty tags
        skill_list = [s.strip() for s in raw_skills.split(',') if s.strip()]
        if not skill_list:
            raise forms.ValidationError("You must enter at least one required skill tag.")
        return skill_list

    def save(self, commit=True):
        job = super().save(commit=False)
        # Copy the cleaned list into the actual JSONField
        job.required_skills = self.cleaned_data['required_skills_raw']
        if commit:
            job.save()
        return job
