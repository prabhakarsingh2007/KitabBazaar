
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden
from ecom.models import Genere, Author, Book, Coupon, Address, Order
from ecom.forms import GenereForm, BookForm, AuthorForm, CouponForm, LoginForm, RegisterForm
from functools import wraps
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.text import slugify
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



@superuser_required
def dashboard(req):
    data = {
        "total_books": Book.objects.count(),
        "total_authors": Author.objects.count(),
        "total_generes": Genere.objects.count(),
        "total_users": User.objects.count(),
        "total_orders": Order.objects.count(),
        "recent_orders": Order.objects.select_related('user').order_by('-order_date')[:5]
    }
    return render(req, "admin/dashboard.html", data) 


@superuser_required
def manageGenere(req):
    data = {}
    form = GenereForm(req.POST or None) 
    generes = Genere.objects.all()

    # pagination work
    paginator = Paginator(generes, 10)
    page_number = req.GET.get("page")
    generes_obj = paginator.get_page(page_number)
    data["generes"] = generes_obj
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.title)
            data.save()
            return redirect("admin_manage_genere")
    return render(req, "admin/manage_genere.html", data)

@superuser_required
def insertBook(req):
    data = {}
    form = BookForm(req.POST or None, req.FILES or None)
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.title)
            data.save()
            return redirect("admin_manage_book")
    return render(req, "admin/insert_book.html",data)



@superuser_required
def manageBooks(req):
    data = {}
    
    books = Book.objects.all()
    # pagination work
    paginator = Paginator(books, 5)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    data["books"] = page_obj
    return render(req,"admin/manage_book.html",data)


@superuser_required
def editBook(req, id):
    book = get_object_or_404(Book, id=id)
    form = BookForm(req.POST or None, req.FILES or None, instance=book)

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.title)
            data.save()
            return redirect("admin_manage_book")
    return render(req, "admin/edit_book.html",{"form":form}) 

@superuser_required
def editGenere(req, id):
    genere = get_object_or_404(Genere, id=id)
    form = GenereForm(req.POST or None, instance=genere)

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.title)
            data.save()
            return redirect("admin_manage_genere")
    return render(req, "admin/edit_genere.html",{"form": form})

@superuser_required
def editAuthor(req, id):
    author = get_object_or_404(Author, id=id)
    form = AuthorForm(req.POST or None, instance=author)

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.name)
            data.save()
            return redirect("admin_manage_author")
    return render(req, "admin/edit_author.html", {"form":form})


@superuser_required
def deleteGenere(req, id):
    if req.method == "POST":
        get_object_or_404(Genere, id=id).delete()
    return redirect("admin_manage_genere") 

@superuser_required
def deleteAuthor(req, id):
    if req.method == "POST":
        get_object_or_404(Author, id=id).delete()
    return redirect("admin_manage_author") 

@superuser_required
def deleteBook(req, id):
    if req.method == "POST":
        get_object_or_404(Book, id=id).delete()
    return redirect("admin_manage_book") 

@superuser_required
def manageAuthor(req):
    data = {}
    form = AuthorForm(req.POST or None)
    authors = Author.objects.all()

    #pagination work

    paginator = Paginator(authors, 10)
    page_number = req.GET.get("page")
    author_obj = paginator.get_page(page_number)
    data["authors"] = author_obj
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.slug = slugify(data.name)
            data.save()
            return redirect("admin_manage_author")
    return render(req, "admin/manage_author.html",data)

@superuser_required
def manageCoupons(req):
    data = {}
    form = CouponForm(req.POST or None)
    coupons = Coupon.objects.all()

    #pagination work

    paginator = Paginator(coupons, 10)
    page_number = req.GET.get("page")
    coupon_obj = paginator.get_page(page_number)
    data["coupons"] = coupon_obj
    data["form"] = form

    if req.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("admin_manage_coupon")
    return render(req, "admin/manage_coupons.html",data)

@superuser_required
def editCoupon(req, id):
    coupon = get_object_or_404(Coupon, id=id)
    form = CouponForm(req.POST or None, instance=coupon)

    if req.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("admin_manage_coupon")
    return render(req, "admin/edit_coupon.html", {"form":form})

@superuser_required
def deleteCoupon(req, id):
    if req.method == "POST":
        get_object_or_404(Coupon, id=id).delete()
    return redirect("admin_manage_coupon")


def login(req):
    if req.user.is_authenticated:
        return redirect("home")

    form = LoginForm(req.POST or None)
    if req.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(req, username=username, password=password)
        if user is not None:
            auth_login(req, user)
            return redirect("home")
        else:
            form.add_error(None, "Invalid username or password.")

    return render(req, "auth/login.html", {"form": form})


def register(req):
    if req.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(req.POST or None)
    if req.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(req, user)
        return redirect("home")

    return render(req, "auth/register.html", {"form": form})


def logout(req):
    auth_logout(req)
    return redirect("home")
