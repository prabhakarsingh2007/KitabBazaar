from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *



@login_required(login_url='login')
def addToCart(req, slug):
    book = get_object_or_404(Book, slug=slug)

    # active order jaisa aapka flow tha, waise hi latest order pick kar rahe hain
    order_qs = Order.objects.filter(user_id=req.user).order_by('-id')
 
    if order_qs.exists():
        order = order_qs[0]

        order_item_qs = OrderItem.objects.filter(order_id=order, book_id=book)

        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order_item.quantity += 1
            order_item.save()
        else:
            OrderItem.objects.create(order_id=order, book_id=book, quantity=1)
    else:
        order = Order.objects.create(user_id=req.user, total_price=0)
        OrderItem.objects.create(order_id=order, book_id=book, quantity=1)

    return redirect('cart')
    
    
@login_required(login_url='login')
def removeFromCart(req, slug):
    pass


@login_required(login_url='login')
def minusFromCart(req, slug):
    pass

@login_required(login_url='login')
def checkout(req):
    pass

@login_required(login_url='login')
def applyCoupon(req):
    pass

@login_required(login_url='login')
def removeCoupon(req):
    pass


@login_required(login_url='login')
def checkCout(req):
    pass

