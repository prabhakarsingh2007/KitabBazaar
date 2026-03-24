
from django.conf import settings
from django.contrib import admin
from django.urls import path
from ecom.views import *
from django.conf.urls.static import static
from ecom.adminView import *
from ecom.authview import *


urlpatterns = [
    path('superadmin/', admin.site.urls),

    #admin pages
    path('admin/', dashboard, name='admin_index'),
    path('admin/genere', manageGenere, name="admin_manage_genere"),
    path('admin/genere/<int:id>/', editGenere, name="admin_edit_genere"),
    path('admin/genere/<int:id>/delete', deleteGenere, name="admin_delete_genere"),
    path('admin/author', manageAuthor, name="admin_manage_author"),
    path('admin/author/<int:id>/', editAuthor, name="admin_edit_author"),
    path('admin/author/<int:id>/delete', deleteAuthor, name="admin_delete_author"),
    path('admin/book', manageBooks, name="admin_manage_book"),
    path('admin/book/<int:id>/', editBook, name="admin_edit_book"),
    path('admin/book/<int:id>/delete', deleteBook, name="admin_delete_book"),
    path('admin/book/insert', insertBook, name="admin_insert_book"),
    
    
    
    

    #homepage
    path('', home, name='home'),
    path('filter/', filter, name='filter'),
    path('filter/<slug:slug>/', filter, name='category_filter'),
    path('book_view/<slug:slug>/', book_view, name='book_view'),

    #authpages
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
