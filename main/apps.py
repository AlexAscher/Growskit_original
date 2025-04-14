from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django.db.models.signals import post_migrate

        from .signals import create_groups
        post_migrate.connect(create_groups, sender=self)
