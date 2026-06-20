import os
from django.core.exceptions import ValidationError
from PIL import Image

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Please upload a JPG, JPEG, PNG, or WEBP image.')
    
    try:
        img = Image.open(value)
        img.verify()
    except Exception:
        raise ValidationError('Invalid or corrupted image content. Please upload a valid image file.')
    finally:
        if hasattr(value, 'seek'):
            value.seek(0)
