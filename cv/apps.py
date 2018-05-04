from django.apps import AppConfig


class CvConfig(AppConfig):
    name = 'cv'

    def ready(self):
        import cv.signals.handlers
