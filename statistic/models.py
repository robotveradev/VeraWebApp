from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Statistic(models.Model):
    role = models.CharField(max_length=25)
    role_obj_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    obj_id = models.PositiveIntegerField()
    ip = models.GenericIPAddressField()
    session_id = models.CharField(max_length=32, blank=False, null=False)
    count = models.PositiveIntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def update_count(self):
        self.count = self.count + 1
        self.save()

    class Meta:
        abstract = True


class CvStatistic(Statistic):
    related_model_name = 'curriculumvitae'

    def __str__(self):
        return '{}'.format(self._meta.verbose_name)

    class Meta:
        verbose_name = _('CV statistic')


class VacancyStatistic(Statistic):
    related_model_name = 'vacancy'

    def __str__(self):
        return '{}'.format(self._meta.verbose_name)

    class Meta:
        verbose_name = _('Vacancy statistic')
