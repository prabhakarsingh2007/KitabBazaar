from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Genere, Book, Order, OrderItem
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
                book = Book.objects.select_related('author', 'genere').filter(isbn=search_query).first()
                if book:
                    return render(req, "book_view.html", {
                        "book": book,
                        "related_books": Book.objects.select_related('author', 'genere').filter(genere=book.genere).exclude(slug=book.slug)[:6]
                    })
            
        data = {
            "books":Book.objects.select_related('author', 'genere').filter(title__icontains=search_query),
            "title": search_query
        }
        return render(req, "filter.html", data)
    else:
        genere = get_object_or_404(Genere, slug=slug)
        data = {
            "books": Book.objects.select_related('author', 'genere').filter(genere=genere),
            "title": genere.title
        }
        return render(req, "filter.html", data)

def book_view(req, slug):
    book = get_object_or_404(Book.objects.select_related('author', 'genere'), slug=slug)
    return render(req, "book_view.html", {
        "book": book,
        "related_books": Book.objects.select_related('author', 'genere').filter(genere=book.genere).exclude(slug=slug)[:6]
    })

@login_required
def cart(req):
    cart_items = OrderItem.objects.select_related('book__author', 'book__genere').filter(order__user=req.user, order__payment=None)
    order = Order.objects.select_related('coupon').filter(user=req.user, payment=None).first()

    return render(req, "cart.html", {"cart_items": cart_items, "order": order})   