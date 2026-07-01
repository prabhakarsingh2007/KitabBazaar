from django import forms
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
# pyrefly: ignore [missing-import]
from .models import Book

@receiver(post_delete, sender=Book)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes cover image file from filesystem when corresponding Book object is deleted.
    """
    if instance.cover_image:
        try:
            if os.path.isfile(instance.cover_image.path):
                os.remove(instance.cover_image.path)
        except Exception:
            # Avoid crashing the deletion transaction if file was already removed or doesn't exist
            pass
