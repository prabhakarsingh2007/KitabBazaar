from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout 



def login(req):
    # checking if the user is already logged in
    if req.user.is_authenticated:
        return redirect("home")
    form = LoginForm(req.POST or None)
    if form.is_valid(): 
       username = form.cleaned_data.get("username")
       password = form.cleaned_data.get("password")
       # login redirect to homepage
       login_user = authenticate(username=username, password=password)
       if login_user is not None:
           auth_login(req, login_user)
           return redirect("home")
       
       form.add_error(None, "Invalid username or password")   
    return render(req, "auth/login.html", {"form": form})

def register(req):
    form = RegisterForm(req.POST or None)
    if form.is_valid():
        password = form.cleaned_data.get("password")    
        # encoding the password
        data = form.save(commit=False)
        data.set_password(password)
        data.save()
        return redirect("login")    
    return render(req, "auth/register.html", {"form": form})

def logout(req):
    auth_logout(req)
    return redirect("login")