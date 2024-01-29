from django.apps import AppConfig


class GenometagConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "GenomeTag"

    def ready(self):
        import GenomeTag.signals
