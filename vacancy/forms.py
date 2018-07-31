from django import forms

from company.models import Company, Office
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('uuid', 'enabled', 'published',)
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
            'salary_from': 'Salary from, $',
            'salary_up_to': 'Salary up to, $'
        }

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member')
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = member.companies
        self.fields['office'].queryset = Office.objects.filter(company__in=self.fields['company'].queryset)


class EditVacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('company', 'uuid', 'published', 'allowed_amount', 'enabled',)
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }
