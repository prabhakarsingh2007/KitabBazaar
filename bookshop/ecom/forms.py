from django.forms import ModelForm
from .models import Genere, Author, Book

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