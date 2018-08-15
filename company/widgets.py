import sys

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from .models import Address

if sys.version > '3':
    long = int
    basestring = (str, bytes)
    unicode = str

USE_DJANGO_JQUERY = getattr(settings, 'USE_DJANGO_JQUERY', False)


class AddressWidget(forms.TextInput):

    class Media:
        """Media defined as a dynamic property instead of an inner class."""
        js = [
            'https://maps.googleapis.com/maps/api/js?libraries=places&key=%s' % settings.GOOGLE_JS_MAP_KEY,
            'js/jquery.geocomplete.min.js',
            'js/address.js',
        ]

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        classes = attrs.get('class', '')
        classes += (' ' if classes else '') + 'address'
        attrs['class'] = classes
        kwargs['attrs'] = attrs
        super(AddressWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        raw = data.get(name, '')
        return raw
