from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
import razorpay
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
        is_ajax = req.POST.get("ajax") == "true" or req.headers.get('x-requested-with') == 'XMLHttpRequest'

        if not address_id or not payment_method:
            if is_ajax:
                return JsonResponse({"status": "error", "message": "Please select an address and payment method."}, status=400)
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

                if payment_method != "cod":
                    payment = Payment.objects.create(
                        user=req.user,
                        amount=order.total_price,
                        payment_method=payment_method,
                        mode=f"Razorpay - {payment_method.upper()}",
                        transaction_id="",
                    )
                    order.payment = payment
                    order.address = address
                    order.status = 'PENDING'
                    order.save()

                    if payment_method == "upi_collect":
                        payment.transaction_id = f"order_sim_{order.id}"
                        payment.save()
                        if is_ajax:
                            return JsonResponse({
                                "status": "success",
                                "payment_method": "upi_collect",
                                "order_id": order.id,
                                "amount": float(order.total_price),
                                "vpa": req.POST.get("vpa") or "success@razorpay"
                            })
                        return redirect("pay_order", order_id=order.id)

                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    amount_in_paise = int(order.total_price * 100)
                    try:
                        razorpay_order = client.order.create({
                            "amount": amount_in_paise,
                            "currency": "INR",
                            "receipt": f"order_rcpt_{order.id}",
                            "payment_capture": 1
                        })
                        payment.transaction_id = razorpay_order['id']
                        payment.save()
                    except Exception as e:
                        raise ValueError(f"Razorpay order generation failed: {str(e)}")

                    if is_ajax:
                        return JsonResponse({
                            "status": "success",
                            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                            "razorpay_amount": amount_in_paise,
                            "razorpay_order_id": razorpay_order['id'],
                            "order_id": order.id,
                            "user_email": req.user.email,
                            "user_name": req.user.get_full_name() or req.user.username,
                            "contact_number": order.address.contact if order.address else ""
                        })
                    return redirect("pay_order", order_id=order.id)

                payment = Payment.objects.create(
                    user=req.user,
                    amount=order.total_price,
                    payment_method=payment_method,
                    mode="Cash on Delivery",
                    transaction_id="",
                )

                order.payment = payment
                order.address = address
                order.save()
            
            if is_ajax:
                return JsonResponse({"status": "success", "redirect_url": "/checkout/success/"})
            messages.success(req, "Your order has been placed successfully!")
            return redirect("success")
        except Exception as e:
            if is_ajax:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
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
        code = req.POST.get("code", "").strip()
        if not code:
            messages.error(req, "Please enter a coupon code.")
            return redirect("cart")

        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            messages.error(req, "Invalid Coupon")
            return redirect("cart")

        from decimal import Decimal
        if not req.user.is_authenticated:
            # Calculate guest cart subtotal
            cart_session = req.session.get('cart', {})
            subtotal = Decimal('0.00')
            for slug, quantity in cart_session.items():
                book = Book.objects.filter(slug=slug).first()
                if book:
                    price = book.discount_price if book.discount_price else book.price
                    subtotal += price * quantity
            
            is_valid, message = coupon.is_valid_for_cart(None, subtotal)
            if is_valid:
                req.session["coupon_code"] = coupon.code
                messages.success(req, "Coupon Applied Successfully")
            else:
                messages.error(req, message)
        else:
            order = Order.objects.filter(user=req.user, payment=None).first()
            if order:
                subtotal = order.get_total_price()
                is_valid, message = coupon.is_valid_for_cart(req.user, subtotal)
                if is_valid:
                    order.coupon = coupon
                    order.save()
                    messages.success(req, "Coupon Applied Successfully")
                else:
                    messages.error(req, message)
            else:
                messages.error(req, "No active order found.")
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


@login_required
def pay_order(req, order_id):
    order = get_object_or_404(Order, id=order_id, user=req.user, payment__isnull=False)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    amount_in_paise = int(order.total_price * 100)
    payment = order.payment
    razorpay_order_id = payment.transaction_id
    
    if not razorpay_order_id.startswith("order_"):
        try:
            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"order_rcpt_{order.id}",
                "payment_capture": 1
            })
            razorpay_order_id = razorpay_order['id']
            payment.transaction_id = razorpay_order_id
            payment.save()
        except Exception as e:
            messages.error(req, f"Razorpay order generation failed: {str(e)}")
            return redirect("checkout")

    context = {
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_amount": amount_in_paise,
        "razorpay_order_id": razorpay_order_id,
        "user_email": req.user.email,
        "user_name": req.user.get_full_name() or req.user.username,
        "contact_number": order.address.contact if order.address else ""
    }
    return render(req, "razorpay_payment.html", context)


@csrf_exempt
@login_required
def verify_payment(req):
    if req.method == "POST":
        razorpay_payment_id = req.POST.get("razorpay_payment_id")
        razorpay_order_id = req.POST.get("razorpay_order_id")
        razorpay_signature = req.POST.get("razorpay_signature")
        order_id = req.GET.get("order_id") or req.POST.get("order_id")
    else:
        razorpay_payment_id = req.GET.get("razorpay_payment_id")
        razorpay_order_id = req.GET.get("razorpay_order_id")
        razorpay_signature = req.GET.get("razorpay_signature")
        order_id = req.GET.get("order_id")

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, order_id]):
        messages.error(req, "Payment verification parameters missing.")
        return redirect("checkout")

    order = get_object_or_404(Order, id=order_id, user=req.user)
    payment = order.payment

    if not payment:
        messages.error(req, "No payment record found for this order.")
        return redirect("checkout")

    if order.status == 'PROCESSING':
        messages.success(req, "Payment verified successfully!")
        return redirect("success")

    if payment.payment_method == "upi_collect":
        payment.transaction_id = razorpay_payment_id
        payment.save()
        order.status = 'PROCESSING'
        order.save()
        messages.success(req, "Simulated UPI Payment verified successfully!")
        return redirect("success")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    
    try:
        client.utility.verify_payment_signature(params_dict)
        
        payment.transaction_id = razorpay_payment_id
        payment.save()

        order.status = 'PROCESSING'
        order.save()

        messages.success(req, "Payment verified and order placed successfully!")
        return redirect("success")
    except Exception as e:
        messages.error(req, f"Payment verification failed: {str(e)}")
        return redirect(f"/checkout/payment-failed/{order.id}/?error_description=" + str(e))


@login_required
def cancel_payment(req, order_id):
    order = get_object_or_404(Order, id=order_id, user=req.user)
    
    if order.status == 'PENDING':
        with transaction.atomic():
            for item in order.order_items.all():
                book_ref = Book.objects.select_for_update().get(id=item.book.id)
                book_ref.stock += item.quantity
                book_ref.save()
            
            payment = order.payment
            order.payment = None
            order.status = 'CANCELLED'
            order.save()
            if payment:
                payment.delete()

        messages.warning(req, "Payment was cancelled. You can review your cart or try again.")
    return redirect("cart")


@login_required
def payment_failed(req, order_id):
    order = get_object_or_404(Order, id=order_id, user=req.user)
    error_description = req.GET.get("error_description", "Payment transaction failed.")
    
    if order.status == 'PENDING':
        with transaction.atomic():
            for item in order.order_items.all():
                book_ref = Book.objects.select_for_update().get(id=item.book.id)
                book_ref.stock += item.quantity
                book_ref.save()
            
            payment = order.payment
            order.payment = None
            order.status = 'CANCELLED'
            order.save()
            if payment:
                payment.delete()

        messages.error(req, f"Payment failed: {error_description}. Please try again.")
    return redirect("checkout")
