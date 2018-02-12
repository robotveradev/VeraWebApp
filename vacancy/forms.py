from django import forms
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    allowed_amount = forms.CharField(widget=forms.NumberInput)
    interview_fee = forms.CharField(widget=forms.NumberInput)

    class Meta:
        exclude = ('employer', 'contract_address', 'enabled',)
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }


class EditVacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('employer', 'contract_address',)
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }
