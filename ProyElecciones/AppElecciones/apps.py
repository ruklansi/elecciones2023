from django.apps import AppConfig

class AppeleccionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AppElecciones'

    def ready(self):
        from . import signals
