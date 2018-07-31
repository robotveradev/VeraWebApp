from django.apps import AppConfig


class ProfileConfig(AppConfig):
    name = 'member_profile'

    def ready(self):
        import member_profile.signals.handlers
