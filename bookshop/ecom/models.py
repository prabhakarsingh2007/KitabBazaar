import email

from django.db import models



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
    