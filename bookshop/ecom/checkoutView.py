
from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def addToCart(req, slug):
    # phele product to find krna hoga
    book = get_object_or_404(Book, slug=slug)
    if book:
        # order check krna hoga ki user ka koi order chal rha h ya nhi jiska payment id null ho
        order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
        if order_qs.exists():
            # order item check krna hoga ki order me ye book pehle se h ya nhi
            order = order_qs[0]
            # update total price 
            order.total_price = order.get_total_payable_price()
            order.save()
            order_item_qs = OrderItem.objects.filter(order_id=order, book_id=book)
            if order_item_qs.exists():
                # agr order item me ye book pehle se h to quantity ko 1 se badha do
                order_item = order_item_qs[0]
                order_item.quantity += 1
                order_item.save()
            else:
                # agr order item me ye book pehle se nhi h to order item create kr do
                OrderItem.objects.create(order_id=order, book_id=book, quantity=1)
        else:
            # agr order nhi h to order create kr do aur order item create kr do
            order = Order.objects.create(user_id=req.user, total_price=0)
            # order item create kr do
            OrderItem.objects.create(order_id=order, book_id=book, quantity=1)
    else:
        # agr book nhi mila to book view page pe redirect kr do
        return redirect("book_view", slug=slug)
    # agr book mil gaya to items order create or update ke baadd cart page pe redirect kr do
    return redirect("cart")

@login_required
def removeFromCart(req, slug):
    book = get_object_or_404(Book, slug=slug)
    if book:
        order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
        if order_qs.exists():
            order = order_qs[0]
            order_item_qs = OrderItem.objects.filter(order_id=order, book_id=book)
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
        order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
        if order_qs.exists():
            order = order_qs[0]
            order_item_qs = OrderItem.objects.filter(order_id=order, book_id=book)
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
    order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
    if order_qs.exists():
        order = order_qs[0]

    if req.method == "POST":
        address_id = req.POST.get("address")
        payment_method = req.POST.get("payment_method")

        # create payment object
        payment = Payment.objects.create(
            user_id=req.user,
            amount=order.get_total_payable_price(),
            payment_method=payment_method,
            mode= (payment_method if payment_method != "cod" else "Cash on Delivery"),
            trancation_id="",
        )

        order.payment_id = payment
        order.address_id = Address.objects.get(id=address_id)
        order.save()
        return redirect("cart")
          
    order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
    addresses = Address.objects.filter(user_id=req.user)
    if order_qs.exists():
        order = order_qs[0]
        context = {
            "order": order,
            "addresses": addresses,
        }
        return render(req, "cheackout.html", context)
    else:
        return redirect("success") 

@login_required
def addAddress(req):
    form = AddressForm(req.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user_id = req.user
        address.save()
        return redirect("checkout")
    return render(req, "add_adderesh.html", {"form": form}) 

@login_required
def applyCoupon(req):
    if req.method == "POST":
        code = req.POST.get("code")
        # now check code
        print(timezone.now())
        coupon_qs = Coupon.objects.filter(code=code, active=True)
        if coupon_qs.exists():
            coupon = coupon_qs[0]
            # now check if user has an active order
            order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
            if order_qs.exists():
                order = order_qs[0]
                order.coupon_id = coupon
                order.save()
                return redirect("cart")
            else:
                return redirect("cart") 
        else:
            # flash message that coupon is invalid
            return redirect("cart")
    else:
        return redirect("cart")

@login_required
def removeCoupon(req):
    order_qs = Order.objects.filter(user_id=req.user, payment_id=None)
    if order_qs.exists():
        order = order_qs[0]
        order.coupon_id = None
        order.save()
        return redirect("cart")
    else:
        return redirect("cart")


@login_required
def success(req):
    return render(req, "order_succes.html")
