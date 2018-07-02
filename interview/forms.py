from datetime import timedelta, datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import ActionInterview, ScheduledMeeting


class ActionInterviewForm(forms.ModelForm):
    class Meta:
        model = ActionInterview
        fields = ('start_date', 'end_date', 'start_time', 'end_time', 'duration')

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
        fields = ('date', 'time',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'data' in kwargs:
            self.action_interview = kwargs['data'].get('action_interview')
            self.employer = kwargs['data'].get('employer')

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        date_time = datetime.now()
        date_time = date_time.replace(hour=time.hour, minute=time.minute)
        if date and time:
            meetings = ScheduledMeeting.objects.filter(
                action_interview__action__pipeline__vacancy__company__employer=self.employer,
                date__gte=date,
                date__lt=date + timedelta(days=1)).order_by('time')
            duration = self.action_interview.duration
            a = []
            for item in meetings:
                bla = datetime.now()
                bla = bla.replace(hour=item.time.hour, minute=item.time.minute, second=0)
                if bla >= date_time - timedelta(minutes=duration):
                    a.append(item)
            if a:
                next_date_time = datetime.now().replace(hour=a[0].time.hour, minute=a[0].time.minute)
                if next_date_time < date_time + timedelta(minutes=duration):
                    raise forms.ValidationError(_(
                        "This time is busy."
                    ))
        else:
            raise forms.ValidationError(_(
                "You must specify date and time for schedule meeting."
            ))
