from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm which handles:
      - username validation (unique, alphanumeric)
      - password1 / password2 match check
      - password strength validation (min length, not too common, not numeric)
    
    We add first_name, last_name, and email on top.
    All passwords are hashed with PBKDF2-SHA256 before saving — never plain text.
    """

    first_name = forms.CharField(
        max_length=50,
        required=False,
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'First name (optional)'}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': 'Last name (optional)'}),
    )
    email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        # Field order controls render order if you loop form.fields
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Ensure no two users share the same email address."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()    # Password is hashed automatically by UserCreationForm.save()
        return user
