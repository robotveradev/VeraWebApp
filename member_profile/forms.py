from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from company.widgets import AddressWidget
from .models import Profile, Position, Education, Experience, LanguageItem, Citizenship, WorkPermit


class ProfileForm(forms.ModelForm):
    class Meta:
        exclude = (
            'member', 'created_at', 'updated_at', 'enabled',)
        model = Profile
        labels = {
            'level': 'Education level',
            'relocation': 'Ready for relocation',
            'official_journey': 'Ready for official journey',
        }
        widgets = {
            'birth_date': forms.SelectDateWidget(
                years=[i for i in range(1950, now().year - 17)][::-1],
                empty_label=('Select year of birth', 'month of birth', 'day of birth'),
            ),
            'address': AddressWidget()
        }


class PositionForm(forms.ModelForm):
    class Meta:
        exclude = ['profile', ]
        model = Position
        labels = {
            'salary_from': 'Salary from, $'
        }


class EducationForm(forms.ModelForm):
    class Meta:
        exclude = ('profile', )
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

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('start') or not cleaned_data.get('end'):
            raise forms.ValidationError(_(
                "You must specify an start date and end date."))
        if cleaned_data.get('start') > cleaned_data.get('end'):
            raise forms.ValidationError(_(
                "Start date must be less than end date"
            ))


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ('profile', )
        widgets = {
            'city': AddressWidget()
        }

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


class LanguageItemForm(forms.ModelForm):
    class Meta:
        model = LanguageItem
        fields = ['language', 'level', ]


class CitizenshipForm(forms.ModelForm):
    class Meta:
        model = Citizenship
        fields = ['country', ]


class WorkPermitForm(forms.ModelForm):
    class Meta:
        model = WorkPermit
        fields = ['country', ]
