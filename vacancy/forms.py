from django import forms
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('employer', 'uuid', 'enabled', 'published', )
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }


class EditVacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('employer', 'uuid', 'published', 'allowed_amount', 'enabled', )
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }
