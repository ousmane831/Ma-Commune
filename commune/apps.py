from django.apps import AppConfig


class CommuneConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "commune"
    verbose_name = "Commune de Niakhar"

    def ready(self):
        from . import signals  # noqa: F401
