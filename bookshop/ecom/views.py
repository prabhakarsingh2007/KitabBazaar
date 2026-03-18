from django.shortcuts import render

from .models import *
# Create your views here.


def home(request):
    data = {
        'tittle': 'home',
        'genres': Genere.objects.all(),
        'books': Book.objects.all(),
    }
    return render(request, 'home.html', data)

def filter(request):
    pass


def book_view(request, slug ):
    pass