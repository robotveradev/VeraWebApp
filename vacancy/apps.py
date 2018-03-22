from django.apps import AppConfig


class VacancyConfig(AppConfig):
    name = 'vacancy'

    def ready(self):
        import vacancy.signals.handlers
