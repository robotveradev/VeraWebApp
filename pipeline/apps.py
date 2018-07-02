from django.apps import AppConfig


class PipelineConfig(AppConfig):
    name = 'pipeline'

    def ready(self):
        import pipeline.signals.handlers
