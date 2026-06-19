from .models import Genere

def generes_processor(request):
    return {
        'generes': Genere.objects.all()
    }
