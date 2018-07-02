from django import forms
from django.utils import timezone

from candidateprofile.models import Achievement
from jobboard.models import Candidate, Employer

YEARS = [i for i in range(1950, timezone.now().year + 1)][::-1]


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ['contract_address', 'enabled', 'user', ]


class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        exclude = ['contract_address', 'enabled', 'user', ]


class LearningForm(forms.Form):
    place = forms.CharField(label='Place of learning', max_length=255, required=True)
    date_from = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    date_up_to = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    specialisation = forms.CharField(label='Specialisation', max_length=255, required=True)
    diploma_number = forms.IntegerField(required=True)


class CertificateForm(forms.Form):
    institution = forms.CharField(label='Institution', max_length=255, required=True)
    date_of_receiving = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    doc_number = forms.CharField(label='Certificate number', max_length=255, required=True)
    course = forms.CharField(label='Course', max_length=255, required=True)


class WorkedForm(forms.Form):
    place = forms.CharField(label='Place of work', max_length=255, required=True)
    date_from = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    date_up_to = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    position = forms.CharField(label='Position', max_length=255, required=True)


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ('title', 'text', )
        labels = {
            'text': 'Achievement description',
        }
