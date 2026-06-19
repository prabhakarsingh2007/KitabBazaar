from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.
class Genere(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name 


class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    no_of_pages = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="authors")
    genere = models.ForeignKey(Genere, on_delete=models.CASCADE, related_name="category")
    cover_image = models.ImageField(upload_to="books/cover")
    edition = models.CharField(max_length=50, default="Latest Edition")
    isbn = models.CharField(max_length=200)

    def __str__(self):
        return self.title



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=50)
    trancation_id = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"Payment {self.id} - {self.amount}"
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Order {self.user.username} - {self.total_price}"

    def get_total_price(self):
        total_price = Decimal('0.00')
        for item in self.order_items.all():
            if item.book.discount_price:
                total_price += item.book.discount_price * item.quantity
            else:
                total_price += item.book.price * item.quantity
        return round(total_price, 1)
    

    def get_shipping_charge(self):
        if self.get_total_price() < Decimal('500.00'):
            return Decimal('45.00')
        else:
            return Decimal('0.00')

    def get_tax_price(self):
        return round(self.get_total_price() * Decimal('0.18'), 0)
    
    def get_discount_amount(self):
        if self.coupon:
            return self.coupon.discount_amount
        else:
            return Decimal('0.00')

    def get_total_payable_price(self):
        return self.get_total_price() + self.get_shipping_charge() + self.get_tax_price() - self.get_discount_amount()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"OrderItem {self.order.id} - {self.book.title} - Quantity: {self.quantity}"
