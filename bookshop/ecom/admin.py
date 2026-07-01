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
admin.site.register(Coupon)