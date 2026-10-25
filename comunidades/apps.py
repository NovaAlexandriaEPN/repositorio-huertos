from django.apps import AppConfig


class ComunidadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comunidades'

    def ready(self):
        from . import checks  # Registrar las comprobaciones al cargar las aplicaciones.
