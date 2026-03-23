from django import forms
from django.forms import ModelForm
from .models import Genere, Author, Book
from django.contrib.auth.models import User

class AuthorFrom(ModelForm):
    class Meta:
        model = Author
        exclude = ["slug"]


class GenereFrom(ModelForm):
    class Meta:
        model = Genere
        exclude = ["slug"]


class Bookform(ModelForm):
    class Meta:
        model = Book
        exclude = ['slug']



class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']