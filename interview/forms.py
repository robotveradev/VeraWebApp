from datetime import datetime, timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _

from interview.utils import get_recruiter_for_time
from .models import ActionInterview, ScheduledMeeting


class ActionInterviewForm(forms.ModelForm):
    class Meta:
        model = ActionInterview
        fields = ('recruiters', 'start_date', 'end_date', 'start_time', 'end_time', 'duration')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = kwargs.get('initial')['company']
        self.fields['recruiters'].queryset = company.collaborators

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('start_date') or not cleaned_data.get('start_time'):
            raise forms.ValidationError(_(
                "You must specify an start date and start time."))
        if cleaned_data.get('end_date') and cleaned_data.get('start_date') > cleaned_data.get('end_date'):
            raise forms.ValidationError(_(
                "Start date must be less than end date."
            ))


class ScheduleMeetingForm(forms.ModelForm):
    class Meta:
        model = ScheduledMeeting
        fields = ('date', 'time')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'data' in kwargs:
            self.action_interview = kwargs['data'].get('action_interview')
            self.recruiters = kwargs['data'].get('recruiters')

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        if date and time:
            if datetime.combine(date, time) + timedelta(minutes=1) < datetime.now():
                raise forms.ValidationError(
                    _('The selected time has already passed')
                )
            if date > self.action_interview.end_date:
                raise forms.ValidationError(
                    _('Interview end date is {}'.format(self.action_interview.end_date.strftime('%d %B %Y'))))
            elif date < self.action_interview.start_date:
                raise forms.ValidationError(
                    _('Interview start date is {}'.format(self.action_interview.start_date.strftime('%d %B %Y'))))

            if time > self.action_interview.end_time:
                raise forms.ValidationError(
                    _('Interview must start before {}'.format(self.action_interview.end_time.strftime('%H:%M')))
                )
            elif time < self.action_interview.start_time:
                raise forms.ValidationError(
                    _('Interview must start after {}'.format(self.action_interview.start_time.strftime('%H:%M')))
                )

            recruiter = get_recruiter_for_time(self.recruiters, datetime.combine(date, time),
                                               self.action_interview.duration)
            if not recruiter:
                raise forms.ValidationError(_('Time is busy. Please choose another.'))

        else:
            raise forms.ValidationError(_(
                "You must specify date and time for schedule meeting."
            ))
