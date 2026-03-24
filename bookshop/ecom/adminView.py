from turtle import save
from django.shortcuts import render, redirect
from ecom.models import *
from ecom.forms import *
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required(login_url="login")
def dashboard(request):
    return render(request, 'admin/dashboard.html')    


@staff_member_required(login_url="login")
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

@staff_member_required(login_url="login")
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

@staff_member_required(login_url="login")
def manageBooks(req):
    data = {}
    books = Book.objects.all()
    # paginator work
    paginator = Paginator(books,5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data['books'] = page_obj
    
    return render(req,"admin/manage_book.html",data)

@staff_member_required(login_url="login")
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

@staff_member_required(login_url="login")
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

@staff_member_required(login_url="login")
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


@staff_member_required(login_url="login")
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

