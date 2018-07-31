from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Company, Office
from .widgets import AddressWidget

if not settings.GOOGLE_ADDRESS['API_KEY']:
    raise ImproperlyConfigured("GOOGLE_API_KEY is not configured in settings.py")


class CompanyForm(forms.ModelForm):
    class Meta:
        exclude = ['employer', 'verified', 'contract_address', 'published', 'created_by']
        model = Company
        widgets = {
            'legal_address': AddressWidget()
        }
        labels = {
            'description': 'Aims and objectives'
        }


class OfficeForm(forms.ModelForm):
    class Meta:
        exclude = ['company', ]
        model = Office
        widgets = {
            'address': AddressWidget()
        }
