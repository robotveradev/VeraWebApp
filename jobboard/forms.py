from datetime import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from member_profile.models import Achievement
from users.models import Member

YEARS = [i for i in range(1950, timezone.now().year + 1)][::-1]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ['contract_address', 'enabled', 'user', ]


class LearningForm(forms.Form):
    place = forms.CharField(label='Place of learning', max_length=255, required=True)
    date_from = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    date_up_to = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), required=True)
    specialisation = forms.CharField(label='Specialisation', max_length=255, required=True)
    diploma_number = forms.IntegerField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data['date_from']
        date_up_to = cleaned_data['date_up_to']
        if date_from > date_up_to:
            raise forms.ValidationError(
                _('End year is lower than start.')
            )


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

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data['date_from']
        date_up_to = cleaned_data['date_up_to']
        if date_from > date_up_to:
            raise forms.ValidationError(
                _('End year is lower than start.')
            )


class CustomFactForm(forms.Form):
    date = forms.DateField()
    title = forms.CharField(max_length=31)
    desc = forms.CharField(max_length=255)


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ('title', 'text',)
        labels = {
            'text': 'Achievement description',
        }


class VerifyFactForm(forms.Form):
    fact_id = forms.CharField()
    member_id = forms.IntegerField()
    sender_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        try:
            sender = Member.objects.get(pk=cleaned_data['sender_id'])
            member = Member.objects.get(pk=cleaned_data['member_id'])
        except Member.DoesNotExist:
            raise forms.ValidationError(
                _('Something went wrong. Please try again later.')
            )
        else:
            if sender.is_already_verify_fact(member.contract_address, cleaned_data['fact_id']):
                raise forms.ValidationError(
                    _('You already verify that fact')
                )
            cleaned_data.update({'sender_address': sender.contract_address, 'member_address': member.contract_address})
            return cleaned_data
