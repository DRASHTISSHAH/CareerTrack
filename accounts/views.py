from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm


def signup_view(request):
    """
    GET  → show blank signup form
    POST → validate, create user (password auto-hashed), login, redirect home
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # Saves user with hashed password
            login(request, user)        # Creates session immediately (no need to re-login)
            messages.success(request, f'Welcome to CareerTrack, {user.username}! 🎉')
            return redirect('home')
        # If form invalid, fall through to render with errors
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """
    GET  → show login form
    POST → authenticate credentials, create session, redirect
    
    AuthenticationForm does the credential check and puts errors in form.non_field_errors.
    Django internally calls check_password() which compares hashed passwords.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Respect ?next= parameter set by @login_required redirect
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        # Invalid credentials → form.non_field_errors contains the error message
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    POST only → destroys session, redirects to login.
    We use POST (not GET) so a simple link can't log someone out (CSRF protection).
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You\'ve been signed out. See you soon!')
        return redirect('login')
    return redirect('home')
