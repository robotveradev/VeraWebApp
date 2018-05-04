from django.db import models


class Pipeline(models.Model):
    vacancy = models.OneToOneField('vacancy.Vacancy',
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='pipeline')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ActionType(models.Model):
    title = models.CharField(max_length=64)
    condition_of_passage = models.CharField(max_length=255,
                                            null=True,
                                            blank=True,
                                            default=None)
    fee = models.BooleanField(default=False)


class Action(models.Model):
    pipeline = models.ForeignKey(Pipeline,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='actions')
    type = models.ForeignKey(ActionType,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name='actions')
    sort = models.SmallIntegerField(default=0)

    def __str__(self):
        return '{}: {}'.format(self.pipeline.vacancy.title if self.pipeline and self.pipeline.vacancy else '',
                               self.type.title)


class CandidateAction(models.Model):
    candidate = models.ForeignKey('jobboard.Candidate',
                                  on_delete=models.SET_NULL,
                                  null=True,
                                  related_name='actions')
    action = models.ForeignKey(Action,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='candidates_on_action')
    passed = models.NullBooleanField(default=None)
    passed_date = models.DateTimeField(null=True,
                                       blank=True,
                                       default=None)
