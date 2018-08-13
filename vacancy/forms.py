from django import forms

from company.models import Office
from users.utils import company_member_role
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('uuid', 'enabled', 'published', 'created_by')
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
        qs = member.companies
        owner_in = []
        for company in qs:
            if company_member_role(company.contract_address, member.contract_address) == 'owner':
                owner_in.append(company.id)
        self.fields['company'].queryset = member.companies.filter(id__in=owner_in)
        self.fields['office'].queryset = Office.objects.filter(company__in=self.fields['company'].queryset)


class EditVacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('company', 'uuid', 'published', 'allowed_amount', 'enabled', 'created_by')
        model = Vacancy

        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }
