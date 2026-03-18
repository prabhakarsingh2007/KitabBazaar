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

def filter(request, slug=None):
    if slug is None:
        search_query = request.GET.get("search", "")
        data = {
            'genres': Genere.objects.all(),
            'books': Book.objects.filter(tittle__icontains=search_query),
           'tittle': search_query,  
        }
        return render(request, "filter.html", data)
    else:
        genre = Genere.objects.get(slug=slug)
        data = {
            'genres': Genere.objects.all(),
            'books': Book.objects.filter(genere__slug=slug),  
            'tittle': genre.tittle,  
        }
        return render(request, "filter.html", data)
        


def book_view(request, slug ):
    pass