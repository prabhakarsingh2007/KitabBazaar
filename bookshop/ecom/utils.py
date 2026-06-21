from django.utils.text import slugify

def generate_unique_slug(model_class, text, instance_id=None):
    slug = slugify(text, allow_unicode=True)
    if not slug:
        slug = "item"
    
    original_slug = slug
    counter = 1
    while True:
        queryset = model_class.objects.filter(slug=slug)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)
        if not queryset.exists():
            break
        slug = f"{original_slug}-{counter}"
        counter += 1
    return slug
