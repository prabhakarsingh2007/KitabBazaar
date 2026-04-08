from django import forms
from django.forms import ModelForm
from .models import Genere, Author, Book, Coupon, Address
from django.contrib.auth.models import User


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        exclude = ["slug"]


class GenereForm(ModelForm):
    class Meta:
        model = Genere
        exclude = ["slug"]


class BookForm(ModelForm):
    class Meta:
        model = Book
        exclude = ["slug"]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        # valid_from and valid_to fields should be in the form of date time picker. 
        # so we will use widgets to make it a date time picker
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "Enter Coupon Code"}),
            "valid_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "valid_to": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        fields = ["code", "discount_amount", "valid_from", "valid_to","active"]

class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ["last_name", "first_name", "username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(render_value=False),
        }

class AddressForm(ModelForm):
    class Meta:
        model = Address
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter Your Name"}),
            "contact": forms.TextInput(attrs={"placeholder": "Enter Your Contact Number"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter Your Email"}),
            "address_line1": forms.TextInput(attrs={"placeholder": "Enter Address Line 1"}),
            "address_line2": forms.TextInput(attrs={"placeholder": "Enter Address Line 2"}),
            "city": forms.TextInput(attrs={"placeholder": "Enter City"}),
            "state": forms.TextInput(attrs={"placeholder": "Enter State"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Enter Postal Code"}),
        }
        fields = ["name","contact", "email","address_line1", "address_line2", "city", "state", "postal_code"]