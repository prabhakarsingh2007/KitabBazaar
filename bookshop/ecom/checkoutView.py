from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def addToCart(req, slug):
    book = get_object_or_404(Book, slug=slug)
    if book:
        order_qs = Order.objects.filter(user=req.user, payment=None)
        if order_qs.exists():
            order = order_qs[0]
            order.total_price = order.get_total_payable_price()
            order.save()
            order_item_qs = OrderItem.objects.filter(order=order, book=book)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                order_item.quantity += 1
                order_item.save()
            else:
                OrderItem.objects.create(order=order, book=book, quantity=1)
        else:
            order = Order.objects.create(user=req.user, total_price=0)
            OrderItem.objects.create(order=order, book=book, quantity=1)
    else:
        return redirect("book_view", slug=slug)
    return redirect("cart")

@login_required
def removeFromCart(req, slug):
    book = get_object_or_404(Book, slug=slug)
    if book:
        order_qs = Order.objects.filter(user=req.user, payment=None)
        if order_qs.exists():
            order = order_qs[0]
            order_item_qs = OrderItem.objects.filter(order=order, book=book)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                order_item.delete()
                return redirect("cart")
    else:
        return redirect("cart")

@login_required
def minusFromCart(req, slug):
    book = get_object_or_404(Book, slug=slug)
    if book:
        order_qs = Order.objects.filter(user=req.user, payment=None)
        if order_qs.exists():
            order = order_qs[0]
            order_item_qs = OrderItem.objects.filter(order=order, book=book)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order_item.delete()
                return redirect("cart")
    else:
        return redirect("cart")
    

@login_required
def checkout(req):
    order_qs = Order.objects.filter(user=req.user, payment=None)
    if order_qs.exists():
        order = order_qs[0]

    if req.method == "POST":
        address_id = req.POST.get("address")
        payment_method = req.POST.get("payment_method")

        payment = Payment.objects.create(
            user=req.user,
            amount=order.get_total_payable_price(),
            payment_method=payment_method,
            mode= (payment_method if payment_method != "cod" else "Cash on Delivery"),
            trancation_id="",
        )

        order.payment = payment
        order.address = Address.objects.get(id=address_id)
        order.save()
        return redirect("cart")
          
    order_qs = Order.objects.filter(user=req.user, payment=None)
    addresses = Address.objects.filter(user=req.user)
    if order_qs.exists():
        order = order_qs[0]
        context = {
            "order": order,
            "addresses": addresses,
        }
        return render(req, "checkout.html", context)
    else:
        return redirect("success") 

@login_required
def addAddress(req):
    form = AddressForm(req.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = req.user
        address.save()
        return redirect("checkout")
    return render(req, "add_address.html", {"form": form}) 

@login_required
def applyCoupon(req):
    if req.method == "POST":
        code = req.POST.get("code")
        coupon_qs = Coupon.objects.filter(code=code, active=True)
        if coupon_qs.exists():
            coupon = coupon_qs[0]
            order_qs = Order.objects.filter(user=req.user, payment=None)
            if order_qs.exists():
                order = order_qs[0]
                order.coupon = coupon
                order.save()
                return redirect("cart")
            else:
                return redirect("cart") 
        else:
            return redirect("cart")
    else:
        return redirect("cart")

@login_required
def removeCoupon(req):
    order_qs = Order.objects.filter(user=req.user, payment=None)
    if order_qs.exists():
        order = order_qs[0]
        order.coupon = None
        order.save()
        return redirect("cart")
    else:
        return redirect("cart")


@login_required
def success(req):
    return render(req, "order_success.html")
