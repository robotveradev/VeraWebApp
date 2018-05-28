from django.apps import AppConfig


class GoogleAddressConfig(AppConfig):
  name = 'google_address'

  def ready(self):
    import google_address.signals
