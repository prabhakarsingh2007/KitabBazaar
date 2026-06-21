from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Genere, Book, Order, OrderItem
import re 

# Create your views here.

def homepage(req):
    books_list = Book.objects.select_related('author', 'genere').all().order_by('-id')
    paginator = Paginator(books_list, 12)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(req, "home.html", {"books": page_obj, "title": "Home"}) 

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
            books_list = Book.objects.select_related('author', 'genere').filter(title__icontains=search_query).order_by('title')
        else:
            books_list = Book.objects.select_related('author', 'genere').all().order_by('title')
        title = search_query or "All Books"
    else:
        genere = get_object_or_404(Genere, slug=slug)
        books_list = Book.objects.select_related('author', 'genere').filter(genere=genere).order_by('title')
        title = genere.title

    paginator = Paginator(books_list, 12)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(req, "filter.html", {"books": page_obj, "title": title})

def book_view(req, slug):
    book = get_object_or_404(Book.objects.select_related('author', 'genere'), slug=slug)
    return render(req, "book_view.html", {
        "book": book,
        "related_books": Book.objects.select_related('author', 'genere').filter(genere=book.genere).exclude(slug=slug)[:6]
    })

def cart(req):
    if not req.user.is_authenticated:
        cart = req.session.get('cart', {})
        cart_items = []
        from decimal import Decimal
        from django.utils import timezone
        from .models import Coupon
        total_price = Decimal('0.00')

        for slug, quantity in cart.items():
            book = Book.objects.filter(slug=slug).select_related('author', 'genere').first()
            if book:
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                })
                price = book.discount_price if book.discount_price else book.price
                total_price += price * quantity

        if not cart_items:
            return render(req, "cart.html", {"cart_items": [], "order": None})

        # Fetch and validate coupon from session
        coupon = None
        coupon_code = req.session.get('coupon_code')
        if coupon_code:
            now = timezone.now()
            coupon = Coupon.objects.filter(
                code=coupon_code,
                active=True,
                valid_from__lte=now,
                valid_to__gte=now
            ).first()

        class MockOrder:
            def __init__(self, total, coupon=None):
                self.total = total
                self.coupon = coupon
                self.coupon_id = coupon.id if coupon else None

            def get_total_price(self):
                return round(self.total, 1)

            def get_shipping_charge(self):
                if self.total < Decimal('500.00'):
                    return Decimal('45.00')
                return Decimal('0.00')

            def get_tax_price(self):
                return round(self.total * Decimal('0.18'), 0)

            def get_discount_amount(self):
                if self.coupon:
                    return self.coupon.discount_amount
                return Decimal('0.00')

            def get_total_payable_price(self):
                raw = self.total + self.get_shipping_charge() + self.get_tax_price() - self.get_discount_amount()
                return max(raw, Decimal('0.00'))

        order = MockOrder(total_price, coupon)
        return render(req, "cart.html", {"cart_items": cart_items, "order": order})

    cart_items = OrderItem.objects.select_related('book__author', 'book__genere').filter(order__user=req.user, order__payment=None)
    order = Order.objects.select_related('coupon').filter(user=req.user, payment=None).first()

    return render(req, "cart.html", {"cart_items": cart_items, "order": order})   

@login_required
def profile_view(req):
    if req.method == "POST":
        first_name = req.POST.get("first_name", "").strip()
        last_name = req.POST.get("last_name", "").strip()
        email = req.POST.get("email", "").strip()

        if not email:
            messages.error(req, "Email is required.")
        else:
            req.user.first_name = first_name
            req.user.last_name = last_name
            req.user.email = email
            req.user.save()
            messages.success(req, "Profile details updated successfully.")
            return redirect("profile")

    orders = Order.objects.select_related('payment').filter(user=req.user, payment__isnull=False).order_by('-order_date')
    return render(req, "profile.html", {"orders": orders})

@login_required
def user_order_detail(req, id):
    order = get_object_or_404(
        Order.objects.select_related('user', 'payment', 'address', 'coupon').prefetch_related('order_items__book__author'),
        id=id,
        user=req.user,
        payment__isnull=False
    )
    return render(req, "user_order_detail.html", {"order": order})