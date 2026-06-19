from django.core.cache import cache
from .models import Genere

def generes_processor(request):
    genres = cache.get_or_set('global_genres_list', Genere.objects.all, 3600)
    return {
        'generes': genres
    }
