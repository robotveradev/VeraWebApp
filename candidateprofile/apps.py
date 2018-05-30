from django.apps import AppConfig


class CandidateProfileConfig(AppConfig):
    name = 'candidateprofile'

    def ready(self):
        import candidateprofile.signals.handlers
