from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupFormStep1, SignupFormStep2
from .models import Product, Cart, CartItem, Supermarket
from collections import defaultdict

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignupFormStep1(request.POST)
        if form.is_valid():
            request.session['signup_email'] = form.cleaned_data['email']
            return redirect('signup_step2')
    else:
        form = SignupFormStep1()
    return render(request, 'registration/signup.html', {'form': form})

def signup_step2(request):
    if 'signup_email' not in request.session:
        return redirect('signup')

    if request.method == 'POST':
        form = SignupFormStep2(request.POST)
        if form.is_valid():
            email = request.session.pop('signup_email')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']

            user = User.objects.create_user(username=username, email=email, password=password)
            user.profile.address = address
            user.profile.save()

            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('supermarkets')
    else:
        form = SignupFormStep2()
    return render(request, 'registration/signup_step2.html', {'form': form})