from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
# pyrefly: ignore [missing-import]
from .validators import validate_image_extension

# Create your models here.
class Genere(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name 


class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    no_of_pages = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    genere = models.ForeignKey(Genere, on_delete=models.CASCADE, related_name="books")
    cover_image = models.ImageField(upload_to="books/cover", validators=[validate_image_extension])
    edition = models.CharField(max_length=50, default="Latest Edition")
    isbn = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=0)

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
    DISCOUNT_TYPE_CHOICES = (
        ('FLAT', 'Flat Amount'),
        ('PERCENTAGE', 'Percentage'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES, default='FLAT')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Flat amount or percentage value")
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Minimum order subtotal to apply this coupon")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum discount amount allowed for percentage type")
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of times this coupon can be used globally")
    per_user_limit = models.PositiveIntegerField(default=1, null=True, blank=True, help_text="Number of times a single user can use this coupon")
    first_order_only = models.BooleanField(default=False, help_text="Check if coupon is only valid for user's first completed order")
    free_shipping = models.BooleanField(default=False, help_text="Check if this coupon provides free shipping")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid_for_cart(self, user, cart_subtotal):
        from django.utils import timezone
        now = timezone.now()

        if not self.active:
            return False, "Coupon is inactive."

        if now < self.valid_from:
            return False, "Coupon is not active yet."

        if now > self.valid_to:
            return False, "Coupon has expired."

        if cart_subtotal < self.min_order_amount:
            return False, f"Minimum order amount of Rs. {self.min_order_amount} is required to apply this coupon."

        # Global usage limit check
        if self.usage_limit is not None:
            global_uses = self.order_set.filter(payment__isnull=False).count()
            if global_uses >= self.usage_limit:
                return False, "Coupon global usage limit has been exceeded."

        # User-specific limits check
        if user and user.is_authenticated:
            if self.per_user_limit is not None:
                user_uses = self.order_set.filter(user=user, payment__isnull=False).count()
                if user_uses >= self.per_user_limit:
                    return False, f"You have already used this coupon maximum number of times ({self.per_user_limit})."

            if self.first_order_only:
                has_previous_orders = user.order_set.filter(payment__isnull=False).exists()
                if has_previous_orders:
                    return False, "This coupon is only valid for your first order."
        else:
            # If user is guest
            if self.first_order_only or (self.per_user_limit is not None):
                return False, "Please log in to apply this coupon."

        return True, "Coupon applied successfully!"

    def calculate_discount(self, subtotal):
        if self.discount_type == 'PERCENTAGE':
            discount = subtotal * (self.discount_amount / Decimal('100.00'))
            if self.max_discount is not None:
                discount = min(discount, self.max_discount)
            return round(discount, 2)
        else: # FLAT
            return min(self.discount_amount, subtotal)
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"Payment {self.id} - {self.amount}"
    

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Payment'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_date = models.DateField(null=True, blank=True)

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
        if self.coupon and self.coupon.free_shipping:
            # Only apply free shipping if the coupon is currently valid for the order
            is_valid, _ = self.coupon.is_valid_for_cart(self.user, self.get_total_price())
            if is_valid:
                return Decimal('0.00')
        if self.get_total_price() < Decimal('500.00'):
            return Decimal('45.00')
        else:
            return Decimal('0.00')

    def get_tax_price(self):
        return round(self.get_total_price() * Decimal('0.18'), 0)
    
    def get_discount_amount(self):
        if self.coupon:
            is_valid, _ = self.coupon.is_valid_for_cart(self.user, self.get_total_price())
            if not is_valid:
                return Decimal('0.00')
            return self.coupon.calculate_discount(self.get_total_price())
        return Decimal('0.00')

    def get_total_payable_price(self):
        raw_payable = self.get_total_price() + self.get_shipping_charge() + self.get_tax_price() - self.get_discount_amount()
        return max(raw_payable, Decimal('0.00'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="quantity_must_be_greater_than_zero"
            )
        ]

    def __str__(self):
        return f"OrderItem {self.order.id} - {self.book.title} - Quantity: {self.quantity}"
