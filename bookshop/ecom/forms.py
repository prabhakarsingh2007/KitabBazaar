from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# pyrefly: ignore [missing-import]
from .models import Genere, Author, Book, Coupon, Address

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
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["last_name", "first_name", "username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(render_value=False),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            user = User(
                username=self.data.get("username"),
                email=self.data.get("email"),
                first_name=self.data.get("first_name"),
                last_name=self.data.get("last_name")
            )
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise forms.ValidationError(list(e.messages))
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

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