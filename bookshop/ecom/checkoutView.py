from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
# pyrefly: ignore [missing-import]
from .forms import AddressForm
# pyrefly: ignore [missing-import]
from .models import Book, Order, OrderItem, Payment, Address, Coupon


def addToCart(req, slug):
    book = get_object_or_404(Book, slug=slug)
    if book.stock < 1:
        messages.error(req, f"'{book.title}' is currently out of stock.")
        return redirect("cart")

    if not req.user.is_authenticated:
        if req.GET.get("buy_now") == "true" or req.POST.get("buy_now") == "true":
            return redirect(f"/auth/login/?next=/checkout/add-to-cart/{slug}/?buy_now=true")
        
        cart = req.session.get("cart", {})
        quantity = cart.get(slug, 0)
        if quantity + 1 > book.stock:
            messages.error(req, f"Only {book.stock} copies of '{book.title}' are available in stock.")
        else:
            cart[slug] = quantity + 1
            req.session["cart"] = cart
            messages.success(req, f"'{book.title}' added to cart.")
        return redirect("cart")

    order, created = Order.objects.get_or_create(user=req.user, payment=None, defaults={"total_price": 0})
    order_item, item_created = OrderItem.objects.get_or_create(order=order, book=book, defaults={"quantity": 1})
    
    if not item_created:
        if order_item.quantity + 1 > book.stock:
            messages.error(req, f"Only {book.stock} copies of '{book.title}' are available in stock.")
        else:
            order_item.quantity += 1
            order_item.save()
            messages.success(req, f"Quantity of '{book.title}' increased.")
    else:
        messages.success(req, f"'{book.title}' added to cart.")
        
    if req.GET.get("buy_now") == "true":
        return redirect("checkout")
    return redirect("cart")

def removeFromCart(req, slug):
    if req.method == "POST":
        if not req.user.is_authenticated:
            cart = req.session.get("cart", {})
            if slug in cart:
                del cart[slug]
                req.session["cart"] = cart
                book = Book.objects.filter(slug=slug).first()
                title = book.title if book else slug
                messages.success(req, f"'{title}' removed from cart.")
            return redirect("cart")

        book = get_object_or_404(Book, slug=slug)
        order = Order.objects.filter(user=req.user, payment=None).first()
        if order:
            OrderItem.objects.filter(order=order, book=book).delete()
            messages.success(req, f"'{book.title}' removed from cart.")
    return redirect("cart")


def minusFromCart(req, slug):
    if req.method == "POST":
        if not req.user.is_authenticated:
            cart = req.session.get("cart", {})
            if slug in cart:
                if cart[slug] > 1:
                    cart[slug] -= 1
                    messages.success(req, "Quantity decreased.")
                else:
                    del cart[slug]
                    messages.success(req, "Item removed from cart.")
                req.session["cart"] = cart
            return redirect("cart")

        book = get_object_or_404(Book, slug=slug)
        order = Order.objects.filter(user=req.user, payment=None).first()
        if order:
            order_item = OrderItem.objects.filter(order=order, book=book).first()
            if order_item:
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.success(req, f"Quantity of '{book.title}' decreased.")
                else:
                    order_item.delete()
                    messages.success(req, f"'{book.title}' removed from cart.")
    return redirect("cart")
    

@login_required
def checkout(req):
    order = Order.objects.select_related('coupon').prefetch_related('order_items__book').filter(user=req.user, payment=None).first()
    if not order or not order.order_items.exists():
        messages.error(req, "Your cart is empty.")
        return redirect("cart")

    if req.method == "POST":
        address_id = req.POST.get("address")
        payment_method = req.POST.get("payment_method")

        if not address_id or not payment_method:
            messages.error(req, "Please select an address and payment method.")
            return redirect("checkout")

        try:
            with transaction.atomic():
                address = get_object_or_404(Address, id=address_id, user=req.user)
                
                # Check and deduct stock levels
                for item in order.order_items.all():
                    # Select for update to prevent race conditions in highly concurrent environments
                    book_ref = Book.objects.select_for_update().get(id=item.book.id)
                    if book_ref.stock < item.quantity:
                        raise ValueError(f"Not enough stock for book: '{book_ref.title}'. Only {book_ref.stock} copies available.")
                    book_ref.stock -= item.quantity
                    book_ref.save()

                # Finalize total price on the order
                order.total_price = order.get_total_payable_price()

                payment = Payment.objects.create(
                    user=req.user,
                    amount=order.total_price,
                    payment_method=payment_method,
                    mode=(payment_method if payment_method != "cod" else "Cash on Delivery"),
                    transaction_id="",
                )

                order.payment = payment
                order.address = address
                order.save()
            
            messages.success(req, "Your order has been placed successfully!")
            return redirect("success")
        except Exception as e:
            messages.error(req, f"An error occurred while placing your order: {str(e)}")
            return redirect("checkout")
          
    addresses = Address.objects.filter(user=req.user)
    context = {
        "order": order,
        "addresses": addresses,
    }
    return render(req, "checkout.html", context)

@login_required
def addAddress(req):
    form = AddressForm(req.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = req.user
        address.save()
        messages.success(req, "Address added successfully.")
        return redirect("checkout")
    return render(req, "add_address.html", {"form": form}) 

def applyCoupon(req):
    if req.method == "POST":
        code = req.POST.get("code")
        now = timezone.now()
        coupon = Coupon.objects.filter(
            code=code,
            active=True,
            valid_from__lte=now,
            valid_to__gte=now
        ).first()
        if coupon:
            if not req.user.is_authenticated:
                req.session["coupon_code"] = code
                messages.success(req, "Coupon applied successfully!")
            else:
                order = Order.objects.filter(user=req.user, payment=None).first()
                if order:
                    order.coupon = coupon
                    order.save()
                    messages.success(req, "Coupon applied successfully!")
                else:
                    messages.error(req, "No active order found.")
        else:
            messages.error(req, "Invalid or expired coupon code.")
    return redirect("cart")


def removeCoupon(req):
    if not req.user.is_authenticated:
        if "coupon_code" in req.session:
            del req.session["coupon_code"]
        messages.success(req, "Coupon removed.")
    else:
        order = Order.objects.filter(user=req.user, payment=None).first()
        if order:
            order.coupon = None
            order.save()
            messages.success(req, "Coupon removed.")
    return redirect("cart")


@login_required
def success(req):
    return render(req, "order_success.html")
