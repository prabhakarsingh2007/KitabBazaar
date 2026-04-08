from django.shortcuts import render
from .models import *
import re 

# Create your views here.

def homepage(req):
    data = {
        "title":"Home",
        "generes":Genere.objects.all(),
        "books":Book.objects.all()
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
                        "generes": Genere.objects.all(),
                        "related_books": Book.objects.filter(genere=book.genere).exclude(slug=book.slug)[:6]
                    })
                except Book.DoesNotExist:
                    pass 
            
        data = {
            "generes":Genere.objects.all(),
            "books":Book.objects.filter(title__icontains=search_query),
            "title": search_query
        }
        return render(req, "filter.html", data)
    else:
        data = {
            "generes":Genere.objects.all(),
            "books":Book.objects.filter(genere__slug=slug),
            "title":Genere.objects.get(slug=slug).title
        }
        return render(req, "filter.html", data)

def book_view(req, slug):
    return render(req, "book_view.html", {
        "book": Book.objects.get(slug=slug),
        "generes": Genere.objects.all(),
        "related_books": Book.objects.filter(genere=Book.objects.get(slug=slug).genere).exclude(slug=slug)[:6]
    })

def cart(req):
    cart_items = OrderItem.objects.filter(order_id__user_id=req.user, order_id__payment_id=None)
    order = Order.objects.filter(user_id=req.user, payment_id=None)

    if order.exists():
        order = order[0]

    generes = Genere.objects.all()
    return render(req, "cart.html",{"cart_items":cart_items, "order":order, "generes":generes})   