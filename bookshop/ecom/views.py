from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
import re 

# Create your views here.

def homepage(req):
    data = {
        "title":"Home",
        "books":Book.objects.select_related('author', 'genere').all()
    }
    return render(req, "home.html", data) 

def filter(req, slug=None):
    if slug is None:
        search_query = req.GET.get("search", "")
        if search_query:
            # if search query is isbn no then direct open book view page
            if re.match(r"^[0-9]{10}(\d{3})?$", search_query):
                try:
                    book = Book.objects.get(isbn=search_query)
                    return render(req, "book_view.html", {
                        "book": book,
                        "related_books": Book.objects.select_related('author', 'genere').filter(genere=book.genere).exclude(slug=book.slug)[:6]
                    })
                except Book.DoesNotExist:
                    pass 
            
        data = {
            "books":Book.objects.select_related('author', 'genere').filter(title__icontains=search_query),
            "title": search_query
        }
        return render(req, "filter.html", data)
    else:
        data = {
            "books":Book.objects.select_related('author', 'genere').filter(genere__slug=slug),
            "title":Genere.objects.get(slug=slug).title
        }
        return render(req, "filter.html", data)

def book_view(req, slug):
    book = Book.objects.select_related('author', 'genere').get(slug=slug)
    return render(req, "book_view.html", {
        "book": book,
        "related_books": Book.objects.select_related('author', 'genere').filter(genere=book.genere).exclude(slug=slug)[:6]
    })

@login_required
def cart(req):
    cart_items = OrderItem.objects.select_related('book__author', 'book__genere').filter(order__user=req.user, order__payment=None)
    order = Order.objects.filter(user=req.user, payment=None)

    if order.exists():
        order = order[0]

    return render(req, "cart.html", {"cart_items": cart_items, "order": order})   