from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Genere, Author, Book, Coupon, Address, Order, OrderItem, Payment


class GenereAdmin(admin.ModelAdmin):
    list_display = ("title","slug")
    prepopulated_fields = {"slug":("title",)}

admin.site.register(Genere,GenereAdmin)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name","slug")
    prepopulated_fields = {"slug":("name",)}
admin.site.register(Author, AuthorAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = ("title","price","discount_price","genere","author","isbn")
    prepopulated_fields = {"slug":("title",)}
    list_select_related = ("author", "genere")
admin.site.register(Book, BookAdmin)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(Payment)

class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code", "discount_type", "discount_amount", "min_order_amount",
        "usage_limit", "times_used", "total_discount_given", "active"
    )
    list_filter = ("discount_type", "active", "valid_from", "valid_to")
    search_fields = ("code",)

    def times_used(self, obj):
        return obj.order_set.filter(payment__isnull=False).count()
    times_used.short_description = "Times Used"

    def total_discount_given(self, obj):
        orders = obj.order_set.filter(payment__isnull=False)
        total_discount = sum(order.get_discount_amount() for order in orders)
        return f"₹{total_discount:.2f}"
    total_discount_given.short_description = "Total Discount Given"

admin.site.register(Coupon, CouponAdmin)