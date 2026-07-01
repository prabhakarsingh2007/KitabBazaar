from django.apps import AppConfig


class EcomConfig(AppConfig):
    name = 'ecom'

    def ready(self):
        # pyrefly: ignore [missing-import]
        import ecom.signals
