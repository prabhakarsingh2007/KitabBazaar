from django.shortcuts import render
import re

from .models import *
import re
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
        if search_query:
            # if search query
            if re.match(r"[0-9]{10}(\d{3})?$", search_query):
                try:
                    book = Book.objects.get(isbn=search_query)
                    return render(request, "book_view.html", {
                        "book": book,
                        "genres": Genere.objects.all(),
                        "related_book": Book.objects.filter(genere=book.genere).exclude(slug=book.slug)[:6]
                    })
                except Book.DoesNotExist:
                    pass
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
        


def book_view(request, slug):
    return render(request, "book_view.html", {
        "book": Book.objects.get(slug=slug),
        "genres": Genere.objects.all(),
        "related_books": Book.objects.filter(genere=Book.objects.get(slug=slug).genere).exclude(slug=slug)[:6]
    })