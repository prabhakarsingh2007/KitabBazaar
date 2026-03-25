from turtle import save
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from ecom.models import *
from ecom.forms import *
from django.core.paginator import Paginator
from functools import wraps 
from django.contrib.auth.models import User


def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You are not authorized to access this page.")
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    


@superuser_required
def dashboard(request):
    data = {
        "total_books": Book.objects.count(),
        "total_authors": Author.objects.count(),
        "total_generes": Genere.objects.count(),
        "total_users": User.objects.count(),
    }
    
    return render(request, 'admin/dashboard.html', data)    


@superuser_required
def manageGenere(req):
    data = {}
    form = GenereFrom(req.POST or None)
    generes = Genere.objects.all()
     # paginator work
    paginator = Paginator(generes,5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    data['generes'] = page_obj
    data["form"] = form
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.tittle.lower().replace(" ","-")
            data.save()
            return redirect("admin_manage_genere")
    return render(req, "admin/manage_genere.html",data)  

@superuser_required     
def insertBook(req):
    data = {}
    form = Bookform(req.POST or None, req.FILES or None)
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.tittle.lower().replace(" ", "-")
            data.save()
            return redirect("admin_manage_book")

    return render(req, "admin/insert_book.html", data)

@superuser_required     
def manageBooks(req):
    data = {}
    books = Book.objects.all()
    # paginator work
    paginator = Paginator(books,5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data['books'] = page_obj
    
    return render(req,"admin/manage_book.html",data)

@superuser_required     
def editBook(req, id):
    book = Book.objects.get(id=id)
    form = Bookform(req.POST or None, req.FILES or None, instance=book)
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.tittle.lower().replace(" ", "-")
            data.save()
            return redirect("admin_manage_book")
    return render(req,'admin/edit_book.html',{"form":form})

@superuser_required
def deleteBook(req, id):
    book = Book.objects.get(id=id)
    book.delete()
    return redirect("admin_manage_book")

@superuser_required
def editGenere(req, id):
    genere = Genere.objects.get(id=id)
    form = GenereFrom(req.POST or None, instance=genere)
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.tittle.lower().replace(" ","-")
            data.save()
            return redirect("admin_manage_genere")
    return render(req,'admin/edit_genere.html',{"form":form})

@superuser_required
def deleteGenere(req, id):
    genere = Genere.objects.get(id=id)
    genere.delete()
    return redirect("admin_manage_genere")

@superuser_required
def editAuthor(req, id):
    author = Author.objects.get(id=id)
    form = AuthorFrom(req.POST or None, instance=author)
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.name.lower().replace(" ","-")
            data.save()
            return redirect("admin_manage_author")
    return render(req, "admin/edit_author.html", {"form": form})

@superuser_required
def deleteAuthor(req, id):
    author = Author.objects.get(id=id)
    author.delete()
    return redirect("admin_manage_author")


@superuser_required
def manageAuthor(req):
    data = {}
    form = AuthorFrom(req.POST or None)
    authors = Author.objects.all()

    #paginator work
    paginator = Paginator(authors, 10)
    page_number = req.GET.get("page")
    author_obj = paginator.get_page(page_number)
    data['authors'] = author_obj
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.name.lower().replace(" ","-")
            data.save()
           
            return redirect("admin_manage_author")
    return render(req,'admin/manage_author.html',data)

