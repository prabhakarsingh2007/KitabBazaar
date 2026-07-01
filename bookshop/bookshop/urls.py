
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# pyrefly: ignore [missing-import]
from ecom.views import homepage, filter, book_view, cart, profile_view, user_order_detail
# pyrefly: ignore [missing-import]
from ecom.authview import (
    dashboard, manageGenere, editGenere, deleteGenere,
    manageCoupons, editCoupon, deleteCoupon,
    manageAuthor, editAuthor, deleteAuthor,
    manageBooks, editBook, deleteBook, insertBook,
    login, register, logout, manageOrders, orderDetail,
    manageStocks, manageUsers
)
# pyrefly: ignore [missing-import]
from ecom.checkoutView import (
    addToCart, removeFromCart, minusFromCart,
    checkout, applyCoupon, removeCoupon, addAddress, success
)

urlpatterns = [
    path('superadmin/', admin.site.urls),
    # admin pages
    path("admin/", dashboard, name="admin_index"),
    path("admin/genere", manageGenere, name="admin_manage_genere"),
    path("admin/genere/<int:id>/edit/", editGenere, name="admin_edit_genere"),
    path("admin/genere/<int:id>/delete/", deleteGenere, name="admin_delete_genere"),
    
    path("admin/coupon", manageCoupons, name="admin_manage_coupon"),
    path("admin/coupon/<int:id>/edit/", editCoupon, name="admin_edit_coupon"),
    path("admin/coupon/<int:id>/delete/", deleteCoupon, name="admin_delete_coupon"),
    
    path("admin/author", manageAuthor, name="admin_manage_author"),
    path("admin/author/<int:id>/edit/", editAuthor, name="admin_edit_author"),
    path("admin/author/<int:id>/delete/", deleteAuthor, name="admin_delete_author"),
    path("admin/book", manageBooks, name="admin_manage_book"),
    path("admin/book/<int:id>/edit/", editBook, name="admin_edit_book"),
    path("admin/book/<int:id>/delete/", deleteBook, name="admin_delete_book"),
    path("admin/book/insert", insertBook, name="admin_insert_book"),
    path("admin/orders/", manageOrders, name="admin_manage_orders"),
    path("admin/orders/<int:id>/", orderDetail, name="admin_order_detail"),
    path("admin/stocks/", manageStocks, name="admin_manage_stocks"),
    path("admin/users/", manageUsers, name="admin_manage_users"),

    # homepage
    path("", homepage, name="home"),
    path("filter/", filter, name="filter"),
    path("filter/<slug:slug>/", filter, name="category_filter"),
    path("book-view/<slug:slug>/",book_view, name="book_view"),
    path("cart/", cart, name="cart"),
    path("profile/", profile_view, name="profile"),
    path("orders/<int:id>/", user_order_detail, name="user_order_detail"),

    # auth pages
    path("auth/login/", login, name="login"),
    path("auth/register/", register, name="register"),
    path("auth/logout/", logout, name="logout"),



    # checkout pages
    path("checkout/add-to-cart/<slug:slug>/", addToCart, name="add_to_cart"),
    path("checkout/remove-from-cart/<slug:slug>/", removeFromCart, name="remove_from_cart"),
    path("checkout/minus-from-cart/<slug:slug>/", minusFromCart, name="minus_from_cart"),
    path("checkout/", checkout, name="checkout"),
    path("checkout/apply-coupon/", applyCoupon, name="apply_coupon"),
    path("checkout/remove-coupon/", removeCoupon, name="remove_coupon"),
    path("checkout/add-address/", addAddress, name="add_address"),
    path("checkout/success/", success, name="success"),


    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)