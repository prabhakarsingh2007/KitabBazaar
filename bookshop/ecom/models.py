import email

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect



# Create your models here.

class Genere(models.Model):
    tittle = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.tittle
    

class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
  

    def __str__(self):
        return self.name
    

class Book(models.Model):
    tittle = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    discount_price = models.FloatField(null=True, blank=True)
    description = models.TextField()
    no_of_pages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    genere = models.ForeignKey(Genere, on_delete=models.CASCADE, related_name='categories')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='authors')
    cover_image = models.ImageField(upload_to='book_covers/')
    edition = models.CharField(default='latest edition')
    isbn = models.CharField(max_length=20)

    def __str__(self):
        return self.tittle
    


class Address(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"
    

class Coupon(models.Model):
        code = models.CharField(max_length=50, unique=True)
        discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
        valid_from = models.DateTimeField()
        valid_to = models.DateTimeField()
        active = models.BooleanField(default=True)

        def __str__(self):
            return self.code
        

class Pyment(models.Model):
   user_id = models.ForeignKey(User, on_delete=models.CASCADE)
   amount = models.DecimalField(max_digits=10, decimal_places=2)    
   payment_method = models.CharField(max_length=50)
   payment_date = models.DateTimeField(auto_now_add=True)
   mode = models.CharField(max_length=50, default='pending')    
   traction_id = models.CharField(max_length=100, null=True, blank=True)

   def __str__(self):
        return f"Payment {self.id} by {self.amount}"
   



class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    Pyment_id = models.ForeignKey(Pyment, on_delete=models.CASCADE, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    adderss_id = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"Order {self.user_id.username} - {self.total_price}"
    
class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    

    def __str__(self):
        return f"{self.quantity} of {self.book_id.tittle} -Quantity: {self.order_id.id}"    