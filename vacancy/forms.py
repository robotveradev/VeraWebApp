from django import forms
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        exclude = ('employer', 'contract_address', 'enabled',)
        model = Vacancy
        help_texts = {
            'interview_fee': 'How many VeraCoin will a candidate receive for an interview',
            'allowed_amount': 'Allowance to spend VeraCoin by vacancy',
        }
        labels = {
            'description': 'Vacancy description',
            'experience': 'Required work experience, years',
            'requirement': 'Requirements',
        }
