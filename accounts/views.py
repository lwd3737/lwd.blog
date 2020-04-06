from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib.auth.views import (LoginView, LogoutView)
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from .forms import LoginForm, SignupForm
from .models import User

class LoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

class LogoutView(LogoutView):
    pass

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            new_user = form.save()
            print('user:',new_user)
            login(request, new_user)
            return redirect('signup_done')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form':form})

@login_required
def signup_done(request):
    return render(request, 'accounts/signup_done.html', {})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {})
