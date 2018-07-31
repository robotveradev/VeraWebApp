from django.db import models
from django.urls import reverse

from quiz.models import ActionExam


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
    must_fee = models.BooleanField(default=False)
    must_approvable = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Action(models.Model):
    pipeline = models.ForeignKey(Pipeline,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='actions')
    action_type = models.ForeignKey(ActionType,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    related_name='actions')
    index = models.SmallIntegerField(default=0)
    published = models.BooleanField(default=False)
    to_delete = models.BooleanField(default=False)

    def __str__(self):
        return '{} action'.format(self.pipeline.vacancy.title if self.pipeline and self.pipeline.vacancy else '')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.index = Action.objects.values('id').filter(pipeline=self.pipeline).count()
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse('action_details', kwargs={'pk': self.id})

    def new_exam(self):
        ActionExam.objects.create(action=self)

    class Meta:
        ordering = ('index',)
