from django import forms
from django.utils.timezone import now
from .models import CurriculumVitae


class CurriculumVitaeForm(forms.ModelForm):
    class Meta:
        exclude = (
            'user', 'experience', 'position', 'education', 'created_at', 'updated_at', 'languages',)
        model = CurriculumVitae
        labels = {
            'level': 'Education level',
        }
        widgets = {
            'birth_date': forms.SelectDateWidget(
                years=[i for i in range(1950, now().year - 17)][::-1],
                empty_label=('Select year of birth', 'month of birth', 'day of birth'),
            ),
        }

