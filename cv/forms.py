from django import forms
from django.utils.timezone import now
from .models import CurriculumVitae, Position, Education, Experience
from django.utils.translation import ugettext_lazy as _


class CurriculumVitaeForm(forms.ModelForm):
    class Meta:
        exclude = (
            'candidate', 'experience', 'position', 'education', 'created_at', 'updated_at', 'published',)
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


class PositionForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Position
        labels = {
            'salary_from': 'Salary from, $'
        }


class EducationForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Education
        widgets = {
            'education_from': forms.SelectDateWidget(
                years=[i for i in range(1950, now().year)][::-1],
                empty_label=('Select year', 'month', 'day'),
            ),
            'education_to': forms.SelectDateWidget(
                years=[i for i in range(1950, now().year)][::-1],
                empty_label=('Select year', 'month', 'day'),
            ),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ()

    def clean(self):
        cleaned_data = super(ExperienceForm, self).clean()
        if cleaned_data.get('end_month') and not cleaned_data.get('end_year'):
            raise forms.ValidationError(_(
                "You must specify an end year with end month."))
        if cleaned_data.get('end_year'):
            if cleaned_data.get('end_year') < cleaned_data.get('start_year'):
                raise forms.ValidationError(_("End year is lower than start."))
        if cleaned_data.get('end_year') == cleaned_data.get('start_year'):
            if cleaned_data.get('end_month') < cleaned_data.get('start_month'):
                raise forms.ValidationError(_("End month is lower than start."))

    def clean_end_year(self):
        data = self.cleaned_data['end_year']
        if not self.cleaned_data['still'] and not data:
            raise forms.ValidationError(_(
                "You must specify an end year if experience is finished."))
        return data
