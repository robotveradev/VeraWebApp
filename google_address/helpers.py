from django.conf import settings
from django.utils.translation import ugettext as _


def get_settings(string="GOOGLE_ADDRESS"):
  return getattr(settings, string, {})
