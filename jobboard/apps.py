from django.apps import AppConfig


class JobboardConfig(AppConfig):
    name = 'jobboard'

    def ready(self):
        import jobboard.signals.handlers
