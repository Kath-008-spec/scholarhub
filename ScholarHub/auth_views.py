from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegisterForm
from .models import get_or_create_student_profile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user, _ = form.save()
            login(request, user)
            messages.success(request, 'Welcome to ScholarHub. Your profile has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'ScholarHub/register.html', {'form': form})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        remember = request.POST.get('remember_me')
        if not remember:
            request.session.set_expiry(0)
        return redirect(next_url or 'dashboard')

    return render(request, 'ScholarHub/login.html', {'form': form, 'next': next_url})


@login_required
def profile_view(request):
    profile = get_or_create_student_profile(request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, profile=profile)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, 'Your profile was updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(profile=profile)

    return render(request, 'ScholarHub/profile.html', {'form': form, 'profile': profile})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
