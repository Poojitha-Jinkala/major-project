from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import VoterProfile, Vote, Candidate


class VoterRegistrationForm(UserCreationForm):
    """Registration form for new voters."""
    STATE_CHOICES = VoterProfile.STATE_CHOICES

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-control'}),
        label="Full Name"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'}),
    )
    voter_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. AP1234567890', 'class': 'form-control'}),
        label="Voter ID"
    )
    age = forms.IntegerField(
        min_value=18, max_value=120,
        widget=forms.NumberInput(attrs={'placeholder': 'Age (min 18)', 'class': 'form-control'}),
    )
    gender = forms.ChoiceField(
        choices=VoterProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    district = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'District (optional)', 'class': 'form-control'}),
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number (optional)', 'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['placeholder'] = (
                'Create password' if field_name == 'password1' else 'Confirm password'
            )

    def clean_voter_id(self):
        voter_id = self.cleaned_data.get('voter_id', '').strip().upper()
        if VoterProfile.objects.filter(voter_id=voter_id).exists():
            raise forms.ValidationError("This Voter ID is already registered in the system.")
        return voter_id

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already associated with an account.")
        return email

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register as a voter.")
        return age

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            VoterProfile.objects.create(
                user=user,
                voter_id=self.cleaned_data['voter_id'],
                full_name=self.cleaned_data['full_name'],
                age=self.cleaned_data['age'],
                gender=self.cleaned_data['gender'],
                state=self.cleaned_data['state'],
                district=self.cleaned_data.get('district', ''),
                phone=self.cleaned_data.get('phone', ''),
                is_verified=True,
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )


class VoteForm(forms.Form):
    """Dynamic form to select a candidate for an election."""
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'candidate-radio'}),
        empty_label=None,
        label=""
    )

    def __init__(self, election, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['candidate'].queryset = Candidate.objects.filter(election=election)
