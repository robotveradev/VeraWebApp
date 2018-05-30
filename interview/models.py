from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.template.defaultfilters import date as dj_date
from django.utils.timezone import localtime

INTERVIEWER = (
    ('me', 'Me'),
    ('vera', 'Vera'),
)


class ActionInterview(models.Model):
    action = models.ForeignKey('pipeline.Action',
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='interview')
    interviewer = models.CharField(max_length=64,
                                   choices=INTERVIEWER)


class Interview(models.Model):
    action_interview = models.ForeignKey(ActionInterview,
                                         on_delete=models.CASCADE,
                                         null=False,
                                         related_name='interviews')
    cv = models.ForeignKey('candidateprofile.CandidateProfile',
                           on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return "Interview {}".format(self.cv.uuid)


class Message(TimeStampedModel, SoftDeletableModel):
    interview = models.ForeignKey(Interview,
                                  related_name="messages",
                                  on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("Author"),
                               related_name="messages",
                               on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_("Message text"))
    read = models.BooleanField(verbose_name=_("Read"),
                               default=False)
    all_objects = models.Manager()

    def get_formatted_create_datetime(self):
        return dj_date(localtime(self.created), settings.DATETIME_FORMAT)

    def __str__(self):
        return self.sender.username + "(" + self.get_formatted_create_datetime() + ") - '" + self.text + "'"
