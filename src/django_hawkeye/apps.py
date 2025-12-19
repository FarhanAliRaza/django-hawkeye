from django.apps import AppConfig


class DjangoHawkeyeConfig(AppConfig):
    name = "django_hawkeye"
    verbose_name = "Django Hawkeye"

    def ready(self):
        from . import checks  # noqa: F401
