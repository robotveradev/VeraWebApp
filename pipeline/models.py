from django.db import models


class Pipeline(models.Model):
    vacancy = models.OneToOneField('vacancy.Vacancy',
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='pipeline')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Pipeline for {}'.format(self.vacancy.title)


class ActionType(models.Model):
    title = models.CharField(max_length=64)
    condition_of_passage = models.CharField(max_length=255,
                                            null=True,
                                            blank=True,
                                            default=None)
    fee = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Action(models.Model):
    pipeline = models.ForeignKey(Pipeline,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='actions')
    type = models.ForeignKey(ActionType,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name='actions')
    index = models.SmallIntegerField(default=0)

    def __str__(self):
        return '{}: {}'.format(self.pipeline.vacancy.title if self.pipeline and self.pipeline.vacancy else '',
                               self.type.title)
