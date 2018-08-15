import time
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from model_utils.models import SoftDeletableModel

from jobboard.helpers import BaseAction
from users.models import Member


class ActionInterview(BaseAction, models.Model):
    action = models.OneToOneField('pipeline.Action',
                                  on_delete=models.CASCADE,
                                  null=False,
                                  related_name='interview')
    start_date = models.DateField(default=now,
                                  help_text=_('Date from you want to interview candidates'))
    end_date = models.DateField(blank=True,
                                null=True,
                                help_text=_('Date to you want to interview candidates'))
    start_time = models.TimeField(default='08:00',
                                  help_text=_('Time from you want to interview'))
    end_time = models.TimeField(blank=True,
                                null=True,
                                default='18:00',
                                help_text=_('Time to you want to interview'))
    duration = models.IntegerField(help_text=_('Interview duration'),
                                   default=10,
                                   validators=[
                                       MinValueValidator(10, 'Interview duration cannot be less than 10 minutes'), ])
    recruiters = models.ManyToManyField('users.Member')

    def get_result_url(self, **kwargs):
        pass

    def get_candidate_url(self):
        return reverse('candidate_interviewing', kwargs={'pk': self.id})

    @property
    def vacancy(self):
        return self.action.pipeline.vacancy

    class Meta:
        abstract = False


class ScheduledMeeting(SoftDeletableModel):
    # all_objects = models.Manager()
    action_interview = models.ForeignKey(ActionInterview,
                                         on_delete=models.CASCADE,
                                         related_name='scheduled_meetings')
    recruiter = models.ForeignKey(Member,
                                  on_delete=models.CASCADE,
                                  related_name='recruiter_scheduled_meetings')
    candidate = models.ForeignKey(Member,
                                  on_delete=models.CASCADE,
                                  related_name='candidate_scheduled_meetings')
    uuid = models.CharField(max_length=32,
                            blank=False,
                            null=False)
    conf_id = models.CharField(max_length=32,
                               blank=False,
                               null=False)
    link_start = models.URLField(max_length=768,
                                 blank=False,
                                 null=False)
    link_join = models.URLField(blank=False,
                                null=False)
    date = models.DateField(blank=False,
                            null=False)
    time = models.TimeField(blank=False,
                            null=False)

    @property
    def vacancy(self):
        return self.action_interview.action.pipeline.vacancy

    def __str__(self):
        return '{} {}'.format(self.date, self.time)

    class Meta:
        unique_together = (('action_interview', 'candidate', 'is_removed'),)


class InterviewPassed(models.Model):
    interview = models.ForeignKey(ActionInterview,
                                  on_delete=models.CASCADE,
                                  related_name='passes')
    recruiter = models.ForeignKey(Member,
                                  on_delete=models.CASCADE,
                                  related_name='recruiter_passed_interviews')
    candidate = models.ForeignKey(Member,
                                  on_delete=models.CASCADE,
                                  related_name='candidate_passed_interviews')
    data = JSONField(blank=True,
                     null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(blank=True,
                                    null=True)
