
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
from django.db.models import Count, Q
from django.contrib import messages

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
    
    books = Book.objects.select_related('author', 'genere').all().order_by('-id')
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
    authors = Author.objects.annotate(book_count=Count('books')).all().order_by('-id')

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
            
            # Merge session cart into database cart
            session_cart = req.session.pop('cart', {})
            if session_cart:
                order, created = Order.objects.get_or_create(user=user, payment=None, defaults={"total_price": 0})
                for slug, quantity in session_cart.items():
                    try:
                        book = Book.objects.get(slug=slug)
                        order_item, item_created = OrderItem.objects.get_or_create(
                            order=order, book=book, defaults={"quantity": quantity}
                        )
                        if not item_created:
                            order_item.quantity += quantity
                            order_item.save()
                    except Book.DoesNotExist:
                        pass

            next_url = req.GET.get('next') or req.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            form.add_error(None, "Invalid username or password.")

    next_url = req.GET.get('next', '') or req.POST.get('next', '')
    return render(req, "auth/login.html", {"form": form, "next": next_url})


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


@superuser_required
def manageOrders(req):
    data = {}
    orders = Order.objects.select_related('user', 'payment').filter(payment__isnull=False).order_by('-order_date')
    
    # pagination
    paginator = Paginator(orders, 10)
    page_number = req.GET.get("page")
    orders_obj = paginator.get_page(page_number)
    
    data["orders"] = orders_obj
    return render(req, "admin/manage_orders.html", data)


@superuser_required
def orderDetail(req, id):
    order = get_object_or_404(
        Order.objects.select_related('user', 'payment', 'address', 'coupon').prefetch_related('order_items__book'),
        id=id,
        payment__isnull=False
    )
    
    if req.method == "POST":
        new_status = req.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return redirect("admin_order_detail", id=id)
            
    return render(req, "admin/order_detail.html", {"order": order, "status_choices": Order.STATUS_CHOICES})


@superuser_required
def manageStocks(req):
    if req.method == "POST":
        book_id = req.POST.get("book_id")
        new_stock = req.POST.get("stock")
        if book_id and new_stock is not None:
            try:
                book = get_object_or_404(Book, id=book_id)
                book.stock = int(new_stock)
                book.save()
                messages.success(req, f"Stock for '{book.title}' updated to {book.stock}.")
            except ValueError:
                messages.error(req, "Invalid stock value.")
        return redirect("admin_manage_stocks")

    books = Book.objects.select_related('author', 'genere').order_by('title')
    paginator = Paginator(books, 10)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(req, "admin/manage_stocks.html", {"books": page_obj})


@superuser_required
def manageUsers(req):
    if req.method == "POST":
        user_id = req.POST.get("user_id")
        action = req.POST.get("action")
        user = get_object_or_404(User, id=user_id)
        
        if user == req.user:
            messages.error(req, "You cannot modify your own account status.")
        elif action == "toggle_active":
            user.is_active = not user.is_active
            user.save()
            messages.success(req, f"User '{user.username}' active status updated.")
        elif action == "toggle_staff":
            user.is_staff = not user.is_staff
            user.save()
            messages.success(req, f"User '{user.username}' staff status updated.")
        elif action == "delete":
            username = user.username
            user.delete()
            messages.success(req, f"User '{username}' deleted successfully.")
            
        return redirect("admin_manage_users")

    users = User.objects.annotate(
        order_count=Count('order', filter=Q(order__payment__isnull=False))
    ).order_by('-date_joined')
    
    paginator = Paginator(users, 10)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(req, "admin/manage_users.html", {"users": page_obj})
