# authentication/views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from . import forms

def logout_user(request):
    
    logout(request)
    return redirect('login')
    
def login_page(request):
    ...
from django.contrib.auth import login, authenticate
# Create your views here.
# authentication/views.py

def logout_user(request):
    
    logout(request)
    return redirect('login')

def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                message = f'Hello, {user.username}! you are connected.'
            else:
                message = 'Credentials not valid'
    return render(
        request, 'authentication/login.html', context={'form': form, 'message': message})