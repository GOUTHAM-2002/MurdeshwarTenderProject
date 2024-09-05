from django.apps import AppConfig


class VendorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendors'

    def ready(self):
        # Import the signals module to ensure signals are connected
        import vendors.signals
