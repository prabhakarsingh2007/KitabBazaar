from turtle import save
from django.shortcuts import render, redirect
from ecom.models import *
from ecom.forms import *




def dashboard(request):
    return render(request, 'admin/dashboard.html')    


def manageGenere(req):
    data = {}
    form = GenereFrom(req.POST or None)
    data['generes'] = Genere.objects.all()
    data["form"] = form
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.tittle.lower().replace(" ","-")
            data.save()
            return redirect("admin_manage_genere")
    return render(req, "admin/manage_genere.html",data)  
  
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


def manageBooks(req):
    data = {}
    data['books'] = Book.objects.all()
    
    return render(req,"admin/manage_book.html",data)

def manageAuthor(req):
    form = AuthorFrom(req.POST or None)
    data = {}
    data['authors'] = Author.objects.all()
    data["form"] = form
    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = data.name.lower().replace(" ","-")
            data.save()
           
            return redirect("admin_manage_author")
    return render(req,'admin/manage_author.html',data)

