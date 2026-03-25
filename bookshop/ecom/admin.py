from django.contrib import admin
from .models import *

# Register your models here.

class GenereAdmin(admin.ModelAdmin):
    list_display = ('tittle', 'slug')
    prepopulated_fields = {'slug': ('tittle',)}


admin.site.register(Genere, GenereAdmin)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', )
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Author, AuthorAdmin)
class BookAdmin(admin.ModelAdmin):
    list_display = ('tittle', 'author', 'genere', 'price', 'discount_price', 'isbn')
    prepopulated_fields = {'slug': ('tittle',)}
admin.site.register(Book, BookAdmin )




admin.site.register(Address)
admin.site.register(Order)  
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)

