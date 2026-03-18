
from django.conf import settings
from django.contrib import admin
from django.urls import path
from ecom.views import *
from django.conf.urls.static import static
from ecom.adminView import *


urlpatterns = [
    path('superadmin/', admin.site.urls),

    #admin pages
    path('admin/', dashboard, name='admin_index'),
    path('admin/genere', manageGenere, name="admin_manage_genere"),
    path('admin/author', manageAuthor, name="admin_manage_author"),
    path('admin/book', manageBooks, name="admin_manage_book"),
    

    #homepage
    path('', home, name='home'),
    path('filter/', filter, name='filter'),
    path('book_view/', book_view, name='book_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
