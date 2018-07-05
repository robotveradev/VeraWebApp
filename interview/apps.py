from django.apps import AppConfig


class InterviewConfig(AppConfig):
    name = 'interview'

    def ready(self):
        import interview.signals.handlers
